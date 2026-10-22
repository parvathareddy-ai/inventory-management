import math
import threading
from datetime import date, timedelta
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field
from mock_data import inventory_items, orders, demand_forecasts, backlog_items, spending_summary, monthly_spending, category_spending, recent_transactions, purchase_orders, restocking_catalog

app = FastAPI(title="Factory Inventory Management System")

# Quarter mapping for date filtering
QUARTER_MAP = {
    'Q1-2025': ['2025-01', '2025-02', '2025-03'],
    'Q2-2025': ['2025-04', '2025-05', '2025-06'],
    'Q3-2025': ['2025-07', '2025-08', '2025-09'],
    'Q4-2025': ['2025-10', '2025-11', '2025-12']
}

def filter_by_month(items: list, month: Optional[str]) -> list:
    """Filter items by month/quarter based on order_date field"""
    if not month or month == 'all':
        return items

    if month.startswith('Q'):
        # Handle quarters
        if month in QUARTER_MAP:
            months = QUARTER_MAP[month]
            return [item for item in items if any(m in item.get('order_date', '') for m in months)]
    else:
        # Direct month match
        return [item for item in items if month in item.get('order_date', '')]

    return items

def apply_filters(items: list, warehouse: Optional[str] = None, category: Optional[str] = None,
                 status: Optional[str] = None) -> list:
    """Apply common filters to a list of items"""
    filtered = items

    if warehouse and warehouse != 'all':
        filtered = [item for item in filtered if item.get('warehouse') == warehouse]

    if category and category != 'all':
        filtered = [item for item in filtered if item.get('category', '').lower() == category.lower()]

    if status and status != 'all':
        filtered = [item for item in filtered if item.get('status', '').lower() == status.lower()]

    return filtered

# CORS: only the Vite dev server may call the API from a browser. A wildcard would let any page the
# developer visits drive the unauthenticated write endpoints. No credentials are used, so none are allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

# Request bodies here are small JSON objects; reject anything larger before it is parsed.
# Requests without a Content-Length (chunked) are not covered; a reverse proxy should enforce that.
MAX_BODY_BYTES = 64 * 1024

@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    length = request.headers.get("content-length")
    if length is not None and length.isdigit() and int(length) > MAX_BODY_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Request body too large"})
    return await call_next(request)

# Data models
class InventoryItem(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_point: int
    unit_cost: float
    location: str
    last_updated: str

class Order(BaseModel):
    id: str
    order_number: str
    customer: str
    items: List[dict]
    status: str
    order_date: str
    expected_delivery: str
    total_value: float
    actual_delivery: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None

class DemandForecast(BaseModel):
    id: str
    item_sku: str
    item_name: str
    current_demand: int
    forecasted_demand: int
    trend: str
    period: str

class BacklogItem(BaseModel):
    id: str
    order_id: str
    item_sku: str
    item_name: str
    quantity_needed: int
    quantity_available: int
    days_delayed: int
    priority: str
    has_purchase_order: Optional[bool] = False
    # Dashboard keys its Create PO / View PO button off purchase_order_id and shows purchase_order in the view modal
    purchase_order_id: Optional[str] = None
    purchase_order: Optional["PurchaseOrder"] = None

class PurchaseOrder(BaseModel):
    id: str
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: str
    created_date: str
    notes: Optional[str] = None

# Upper bounds keep a client from storing unbounded strings or absurd numbers in server memory
MAX_QUANTITY = 1_000_000
MAX_UNIT_COST = 1_000_000

class CreatePurchaseOrderRequest(BaseModel):
    backlog_item_id: str = Field(max_length=50)
    supplier_name: str = Field(max_length=200)
    quantity: int = Field(le=MAX_QUANTITY)
    # Floats are bounds-checked in the handler: a Field(le=...) on NaN fails validation, and FastAPI
    # cannot serialize the NaN echoed back in its own 422 response
    unit_cost: float
    expected_delivery_date: str = Field(max_length=10)
    notes: Optional[str] = Field(default=None, max_length=1000)

class RestockItem(BaseModel):
    sku: str
    name: str
    trend: str
    shortfall: int
    quantity: int
    unit_cost: float
    supplier: str
    lead_time_days: int
    line_total: float

class RestockRecommendation(BaseModel):
    budget: float
    total_cost: float
    remaining_budget: float
    items: List[RestockItem]

class RestockOrderLine(BaseModel):
    sku: str = Field(max_length=50)
    quantity: int = Field(le=MAX_QUANTITY)

class SubmitRestockOrderRequest(BaseModel):
    budget: float
    items: List[RestockOrderLine] = Field(max_length=100)

class SubmittedOrder(BaseModel):
    id: str
    order_date: str
    budget: float
    total_cost: float
    items: List[RestockItem]
    overall_lead_time_days: int
    expected_delivery: str
    status: str

# Submitted restocking orders live only in memory; they reset when the server restarts
submitted_orders: List[dict] = []
# Endpoints run in a threadpool, so ID generation and append must happen atomically
submitted_orders_lock = threading.Lock()

class Task(BaseModel):
    id: int
    title: str
    priority: str
    dueDate: str  # camelCase to match the task objects the client already uses
    status: str

class CreateTaskRequest(BaseModel):
    title: str = Field(max_length=200)
    priority: str = Field(default="medium", max_length=10)
    dueDate: str = Field(max_length=10)

# Tasks are never evicted, so cap the list to stop repeated POSTs from growing memory without bound
MAX_TASKS = 500

TASK_PRIORITIES = {"low", "medium", "high"}

# API tasks live in memory. Ids start at 1000 because the client tells mock tasks (ids 1-4,
# defined in useAuth.js) from API tasks by id, so the two ranges must never overlap.
tasks: List[dict] = []
tasks_lock = threading.Lock()
purchase_orders_lock = threading.Lock()
next_task_id = 1000

# API endpoints
@app.get("/")
def root():
    return {"message": "Factory Inventory Management System API", "version": "1.0.0"}

@app.get("/api/inventory", response_model=List[InventoryItem])
def get_inventory(
    warehouse: Optional[str] = None,
    category: Optional[str] = None
):
    """Get all inventory items with optional filtering"""
    return apply_filters(inventory_items, warehouse, category)

@app.get("/api/inventory/{item_id}", response_model=InventoryItem)
def get_inventory_item(item_id: str):
    """Get a specific inventory item"""
    item = next((item for item in inventory_items if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/api/orders", response_model=List[Order])
def get_orders(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get all orders with optional filtering"""
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)
    return filtered_orders

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    """Get a specific order"""
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/demand", response_model=List[DemandForecast])
def get_demand_forecasts():
    """Get demand forecasts"""
    return demand_forecasts

@app.get("/api/backlog", response_model=List[BacklogItem])
def get_backlog():
    """Get backlog items with purchase order status"""
    # Add has_purchase_order flag to each backlog item
    result = []
    for item in backlog_items:
        item_dict = dict(item)
        # Check if this backlog item has a purchase order
        po = next((po for po in purchase_orders if po["backlog_item_id"] == item["id"]), None)
        item_dict["has_purchase_order"] = po is not None
        item_dict["purchase_order_id"] = po["id"] if po else None
        item_dict["purchase_order"] = po
        result.append(item_dict)
    return result

@app.get("/api/dashboard/summary")
def get_dashboard_summary(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get summary statistics for dashboard with optional filtering"""
    # Filter inventory
    filtered_inventory = apply_filters(inventory_items, warehouse, category)

    # Filter orders
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    total_inventory_value = sum(item["quantity_on_hand"] * item["unit_cost"] for item in filtered_inventory)
    low_stock_items = len([item for item in filtered_inventory if item["quantity_on_hand"] <= item["reorder_point"]])
    pending_orders = len([order for order in filtered_orders if order["status"] in ["Processing", "Backordered"]])
    total_backlog_items = len(backlog_items)

    return {
        "total_inventory_value": round(total_inventory_value, 2),
        "low_stock_items": low_stock_items,
        "pending_orders": pending_orders,
        "total_backlog_items": total_backlog_items,
        "total_orders_value": sum(order["total_value"] for order in filtered_orders)
    }

@app.get("/api/spending/summary")
def get_spending_summary():
    """Get spending summary statistics"""
    return spending_summary

@app.get("/api/spending/monthly")
def get_monthly_spending():
    """Get monthly spending breakdown"""
    return monthly_spending

@app.get("/api/spending/categories")
def get_category_spending():
    """Get spending by category"""
    return category_spending

@app.get("/api/spending/transactions")
def get_recent_transactions():
    """Get recent transactions"""
    return recent_transactions

@app.get("/api/reports/quarterly")
def get_quarterly_reports():
    """Get quarterly performance reports"""
    # Calculate quarterly statistics from orders
    quarters = {}

    for order in orders:
        order_date = order.get('order_date', '')
        # Determine quarter
        if '2025-01' in order_date or '2025-02' in order_date or '2025-03' in order_date:
            quarter = 'Q1-2025'
        elif '2025-04' in order_date or '2025-05' in order_date or '2025-06' in order_date:
            quarter = 'Q2-2025'
        elif '2025-07' in order_date or '2025-08' in order_date or '2025-09' in order_date:
            quarter = 'Q3-2025'
        elif '2025-10' in order_date or '2025-11' in order_date or '2025-12' in order_date:
            quarter = 'Q4-2025'
        else:
            continue

        if quarter not in quarters:
            quarters[quarter] = {
                'quarter': quarter,
                'total_orders': 0,
                'total_revenue': 0,
                'delivered_orders': 0,
                'avg_order_value': 0
            }

        quarters[quarter]['total_orders'] += 1
        quarters[quarter]['total_revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            quarters[quarter]['delivered_orders'] += 1

    # Calculate averages and fulfillment rate
    result = []
    for q, data in quarters.items():
        if data['total_orders'] > 0:
            data['avg_order_value'] = round(data['total_revenue'] / data['total_orders'], 2)
            data['fulfillment_rate'] = round((data['delivered_orders'] / data['total_orders']) * 100, 1)
        result.append(data)

    # Sort by quarter
    result.sort(key=lambda x: x['quarter'])
    return result

@app.get("/api/reports/monthly-trends")
def get_monthly_trends():
    """Get month-over-month trends"""
    months = {}

    for order in orders:
        order_date = order.get('order_date', '')
        if not order_date:
            continue

        # Extract month (format: YYYY-MM-DD)
        month = order_date[:7]  # Gets YYYY-MM

        if month not in months:
            months[month] = {
                'month': month,
                'order_count': 0,
                'revenue': 0,
                'delivered_count': 0
            }

        months[month]['order_count'] += 1
        months[month]['revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            months[month]['delivered_count'] += 1

    # Convert to list and sort
    result = list(months.values())
    result.sort(key=lambda x: x['month'])
    return result

def remaining_shortfall(forecast: dict) -> int:
    """Forecast shortfall minus units already covered by submitted orders"""
    ordered = sum(
        line["quantity"]
        for order in submitted_orders
        for line in order["items"]
        if line["sku"] == forecast["item_sku"]
    )
    return forecast["forecasted_demand"] - forecast["current_demand"] - ordered

def build_restock_item(forecast: dict, catalog_entry: dict, quantity: int, shortfall: int) -> dict:
    """Combine a demand forecast row and its catalog entry into a priced restock line"""
    return {
        "sku": forecast["item_sku"],
        "name": forecast["item_name"],
        "trend": forecast["trend"],
        "shortfall": shortfall,
        "quantity": quantity,
        "unit_cost": catalog_entry["unit_cost"],
        "supplier": catalog_entry["supplier"],
        "lead_time_days": catalog_entry["lead_time_days"],
        "line_total": round(quantity * catalog_entry["unit_cost"], 2),
    }

@app.get("/api/restocking/recommendations", response_model=RestockRecommendation)
def get_restock_recommendations(budget: float = Query(allow_inf_nan=False)):
    """Recommend forecast items to restock within the given budget"""
    if budget < 0:
        raise HTTPException(status_code=400, detail="Budget must not be negative")

    catalog = {entry["sku"]: entry for entry in restocking_catalog}

    # Only items whose forecast exceeds current demand need restocking, and we need a
    # catalog entry to price them. Growing items come first because they risk stockouts
    # soonest; within a trend, the largest shortfall goes first.
    # Units already on submitted orders are subtracted, so the same shortfall cannot be bought twice.
    with submitted_orders_lock:
        candidates = [
            (f, remaining_shortfall(f)) for f in demand_forecasts if f["item_sku"] in catalog
        ]
    candidates = [(f, shortfall) for f, shortfall in candidates if shortfall > 0]
    candidates.sort(key=lambda c: (c[0]["trend"] != "increasing", -c[1]))

    remaining = budget
    items = []
    for forecast, shortfall in candidates:
        entry = catalog[forecast["item_sku"]]
        # Buy the full shortfall when affordable, otherwise as many units as the remaining
        # budget allows (a partial fill), then keep going so cheaper items can still fit
        quantity = min(shortfall, math.floor(remaining / entry["unit_cost"]))
        if quantity < 1:
            continue
        item = build_restock_item(forecast, entry, quantity, shortfall)
        remaining -= item["line_total"]
        items.append(item)

    total_cost = round(sum(i["line_total"] for i in items), 2)
    return {
        "budget": budget,
        "total_cost": total_cost,
        "remaining_budget": round(budget - total_cost, 2),
        "items": items,
    }

@app.post("/api/restocking/orders", response_model=SubmittedOrder, status_code=201)
def submit_restock_order(request: SubmitRestockOrderRequest):
    """Submit a restocking order; prices and lead times are always taken from the server"""
    # NaN/inf must be rejected here rather than by the model: they would make the over-budget
    # comparison always pass, and FastAPI cannot serialize a NaN echoed in its own 422 response
    if not math.isfinite(request.budget) or request.budget < 0:
        raise HTTPException(status_code=400, detail="Budget must be a non-negative number")
    if not request.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    catalog = {entry["sku"]: entry for entry in restocking_catalog}
    forecasts = {f["item_sku"]: f for f in demand_forecasts}

    # Reprice from the catalog instead of trusting the client, so the total can't be tampered with
    skus = [line.sku for line in request.items]
    if len(set(skus)) != len(skus):
        raise HTTPException(status_code=400, detail="Each SKU may appear only once per order")

    # The shortfall check, the budget check and the append run under one lock. Checked outside it,
    # two concurrent orders for the same SKU could both pass and together exceed its shortfall.
    with submitted_orders_lock:
        lines = []
        for line in request.items:
            if line.quantity < 1:
                raise HTTPException(status_code=400, detail=f"Quantity for {line.sku} must be at least 1")
            if line.sku not in catalog or line.sku not in forecasts:
                raise HTTPException(status_code=400, detail=f"Unknown SKU {line.sku}")
            # Only the not-yet-ordered forecast shortfall can be restocked, so cap quantity at it
            # (this also rejects items with flat or falling demand, whose shortfall is <= 0)
            shortfall = remaining_shortfall(forecasts[line.sku])
            if line.quantity > shortfall:
                raise HTTPException(status_code=400, detail=f"Quantity for {line.sku} exceeds its forecast shortfall of {max(shortfall, 0)}")
            lines.append(build_restock_item(forecasts[line.sku], catalog[line.sku], line.quantity, shortfall))

        total_cost = round(sum(l["line_total"] for l in lines), 2)
        if total_cost > request.budget:
            raise HTTPException(status_code=400, detail="Order total exceeds the budget")

        # Items ship from different suppliers, so the order is complete when the slowest one arrives
        overall_lead_time = max(l["lead_time_days"] for l in lines)
        today = date.today()
        order = {
            "id": f"RST-{len(submitted_orders) + 1:04d}",
            "order_date": today.isoformat(),
            "budget": request.budget,
            "total_cost": total_cost,
            "items": lines,
            "overall_lead_time_days": overall_lead_time,
            "expected_delivery": (today + timedelta(days=overall_lead_time)).isoformat(),
            "status": "Submitted",
        }
        submitted_orders.append(order)
    return order

@app.get("/api/restocking/orders", response_model=List[SubmittedOrder])
def get_submitted_orders():
    """Get submitted restocking orders, newest first"""
    return list(reversed(submitted_orders))

@app.get("/api/tasks", response_model=List[Task])
def get_tasks():
    """Get API tasks, newest first"""
    return list(reversed(tasks))

@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(request: CreateTaskRequest):
    """Create a pending task"""
    title = request.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")
    if request.priority not in TASK_PRIORITIES:
        raise HTTPException(status_code=400, detail="Priority must be low, medium or high")
    try:
        date.fromisoformat(request.dueDate)
    except ValueError:
        raise HTTPException(status_code=400, detail="dueDate must be an ISO date (YYYY-MM-DD)")

    global next_task_id
    with tasks_lock:
        if len(tasks) >= MAX_TASKS:
            raise HTTPException(status_code=409, detail=f"Task limit of {MAX_TASKS} reached; delete some tasks first")
        task = {"id": next_task_id, "title": title, "priority": request.priority,
                "dueDate": request.dueDate, "status": "pending"}
        next_task_id += 1
        tasks.append(task)
    return task

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    """Delete a task"""
    with tasks_lock:
        for i, task in enumerate(tasks):
            if task["id"] == task_id:
                return tasks.pop(i)
    raise HTTPException(status_code=404, detail="Task not found")

@app.patch("/api/tasks/{task_id}", response_model=Task)
def toggle_task(task_id: int):
    """Toggle a task between pending and completed"""
    with tasks_lock:
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = "completed" if task["status"] == "pending" else "pending"
                return dict(task)
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/api/purchase-orders", response_model=PurchaseOrder, status_code=201)
def create_purchase_order(request: CreatePurchaseOrderRequest):
    """Create a purchase order for a backlog item (at most one per item)"""
    if not any(b["id"] == request.backlog_item_id for b in backlog_items):
        raise HTTPException(status_code=404, detail="Backlog item not found")
    if not request.supplier_name.strip():
        raise HTTPException(status_code=400, detail="Supplier name is required")
    if request.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    # NaN/inf would pass a plain < 0 check and then break JSON serialization of the response
    if not math.isfinite(request.unit_cost) or request.unit_cost < 0:
        raise HTTPException(status_code=400, detail="Unit cost must be a non-negative number")
    if request.unit_cost > MAX_UNIT_COST:
        raise HTTPException(status_code=400, detail=f"Unit cost must not exceed {MAX_UNIT_COST}")
    try:
        delivery = date.fromisoformat(request.expected_delivery_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="expected_delivery_date must be an ISO date (YYYY-MM-DD)")
    today = date.today()
    if delivery < today:
        raise HTTPException(status_code=400, detail="Expected delivery date cannot be in the past")

    # The duplicate check and the append share the lock so two concurrent requests can't both pass it
    with purchase_orders_lock:
        if any(po["backlog_item_id"] == request.backlog_item_id for po in purchase_orders):
            raise HTTPException(status_code=409, detail="A purchase order already exists for this backlog item")
        po = {
            "id": f"PO-{len(purchase_orders) + 1:04d}",
            "backlog_item_id": request.backlog_item_id,
            "supplier_name": request.supplier_name.strip(),
            "quantity": request.quantity,
            "unit_cost": request.unit_cost,
            "expected_delivery_date": request.expected_delivery_date,
            "status": "Pending",
            "created_date": today.isoformat(),
            "notes": request.notes,
        }
        purchase_orders.append(po)
    return po

@app.get("/api/purchase-orders/{backlog_item_id}", response_model=PurchaseOrder)
def get_purchase_order_for_backlog_item(backlog_item_id: str):
    """Get the purchase order raised for a backlog item"""
    po = next((po for po in purchase_orders if po["backlog_item_id"] == backlog_item_id), None)
    if po is None:
        raise HTTPException(status_code=404, detail="No purchase order for this backlog item")
    return po

if __name__ == "__main__":
    import uvicorn
    # Loopback only: the write endpoints have no authentication, so the API must not be reachable
    # from other machines on the network. Put a reverse proxy with auth in front to expose it.
    uvicorn.run(app, host="127.0.0.1", port=8001)
