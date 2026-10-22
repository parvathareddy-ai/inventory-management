"""
Tests for API hardening: CORS policy, request size limits, input bounds and the restock race fix.
"""
import threading
import time
from datetime import date, timedelta

import pytest
from fastapi import HTTPException

import main


@pytest.fixture(autouse=True)
def reset_state():
    """Keep in-memory stores from leaking between tests (the app is module-global)."""
    main.tasks.clear()
    main.purchase_orders.clear()
    main.submitted_orders.clear()
    yield
    main.tasks.clear()
    main.purchase_orders.clear()
    main.submitted_orders.clear()


def po_payload(client, **overrides):
    payload = {
        "backlog_item_id": client.get("/api/backlog").json()[0]["id"],
        "supplier_name": "Acme Parts",
        "quantity": 10,
        "unit_cost": 4.25,
        "expected_delivery_date": (date.today() + timedelta(days=7)).isoformat(),
    }
    return {**payload, **overrides}


class TestCorsPolicy:
    """Test suite for the restricted CORS configuration."""

    def test_dev_server_origin_allowed(self, client):
        """Test that the Vite dev server origin passes a preflight for a write endpoint."""
        response = client.options("/api/tasks", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_foreign_origin_rejected(self, client):
        """Test that an arbitrary website cannot pass a preflight against the local API."""
        response = client.options("/api/tasks", headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        })
        assert response.status_code == 400
        assert "access-control-allow-origin" not in response.headers

    def test_foreign_origin_gets_no_cors_header_on_get(self, client):
        """Test that a simple GET from another origin is not readable by that origin's script."""
        response = client.get("/api/inventory", headers={"Origin": "https://evil.example"})
        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers


class TestRequestLimits:
    """Test suite for body size and field length limits."""

    def test_oversized_body_rejected(self, client):
        """Test that bodies over the size limit get 413 before they are parsed."""
        body = '{"title": "%s", "dueDate": "2025-10-20"}' % ("x" * (main.MAX_BODY_BYTES + 1))
        response = client.post("/api/tasks", content=body, headers={"Content-Type": "application/json"})
        assert response.status_code == 413
        assert main.tasks == []

    def test_task_title_too_long_rejected(self, client):
        """Test that task titles over 200 characters are rejected."""
        response = client.post("/api/tasks", json={"title": "x" * 201, "dueDate": "2025-10-20"})
        assert response.status_code == 422

    def test_task_list_capped(self, client):
        """Test that the task list stops growing at its cap."""
        main.tasks.extend(
            {"id": i, "title": "t", "priority": "low", "dueDate": "2025-10-20", "status": "pending"}
            for i in range(main.MAX_TASKS)
        )
        response = client.post("/api/tasks", json={"title": "one more", "dueDate": "2025-10-20"})
        assert response.status_code == 409
        assert len(main.tasks) == main.MAX_TASKS

    @pytest.mark.parametrize("overrides", [
        {"supplier_name": "x" * 201},
        {"notes": "x" * 1001},
        {"quantity": main.MAX_QUANTITY + 1},
    ])
    def test_purchase_order_field_bounds(self, client, overrides):
        """Test that oversized purchase order fields fail validation."""
        response = client.post("/api/purchase-orders", json=po_payload(client, **overrides))
        assert response.status_code == 422
        assert main.purchase_orders == []

    def test_purchase_order_unit_cost_bound(self, client):
        """Test that an absurd unit cost is rejected with a readable error."""
        response = client.post("/api/purchase-orders", json=po_payload(client, unit_cost=1e30))
        assert response.status_code == 400
        assert "unit cost" in response.json()["detail"].lower()

    def test_purchase_order_at_limits_accepted(self, client):
        """Test that values exactly at the limits are still accepted."""
        response = client.post("/api/purchase-orders", json=po_payload(
            client, supplier_name="x" * 200, notes="x" * 1000,
            quantity=main.MAX_QUANTITY, unit_cost=main.MAX_UNIT_COST,
        ))
        assert response.status_code == 201

    def test_restock_order_item_count_bounded(self, client):
        """Test that a restock order cannot carry an unbounded item list."""
        items = [{"sku": f"SKU-{i}", "quantity": 1} for i in range(101)]
        response = client.post("/api/restocking/orders", json={"budget": 100, "items": items})
        assert response.status_code == 422


class TestRestockRace:
    """Test suite for the restock shortfall check under concurrency."""

    def test_concurrent_orders_cannot_exceed_shortfall(self, monkeypatch):
        """Test that simultaneous orders for a SKU's full shortfall don't all succeed."""
        # TestClient handles requests one at a time, so the handler is called from threads
        # directly, and a short sleep widens the check-then-append window. Without the lock
        # around both, every thread passes the shortfall check (8 orders instead of 1).
        original = main.remaining_shortfall

        def slow_shortfall(forecast):
            value = original(forecast)
            time.sleep(0.01)
            return value

        monkeypatch.setattr(main, "remaining_shortfall", slow_shortfall)
        item = main.get_restock_recommendations(budget=1e8)["items"][0]
        request = main.SubmitRestockOrderRequest(
            budget=1e8, items=[{"sku": item["sku"], "quantity": item["shortfall"]}]
        )

        successes = []
        barrier = threading.Barrier(8)

        def submit():
            barrier.wait()
            try:
                main.submit_restock_order(request)
                successes.append(1)
            except HTTPException:
                pass

        threads = [threading.Thread(target=submit) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(successes) == 1
        ordered = sum(
            line["quantity"] for order in main.submitted_orders
            for line in order["items"] if line["sku"] == item["sku"]
        )
        assert ordered == item["shortfall"]
