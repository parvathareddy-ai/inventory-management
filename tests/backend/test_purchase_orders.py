"""
Tests for purchase order API endpoints.
"""
from datetime import date, timedelta

import pytest

import main


@pytest.fixture(autouse=True)
def reset_purchase_orders():
    """Keep purchase orders from leaking between tests (the app is module-global)."""
    main.purchase_orders.clear()
    yield
    main.purchase_orders.clear()


@pytest.fixture
def backlog_item_id(client):
    return client.get("/api/backlog").json()[0]["id"]


def po_payload(backlog_item_id, **overrides):
    payload = {
        "backlog_item_id": backlog_item_id,
        "supplier_name": "Acme Parts",
        "quantity": 350,
        "unit_cost": 4.25,
        "expected_delivery_date": (date.today() + timedelta(days=7)).isoformat(),
        "notes": "Rush",
    }
    return {**payload, **overrides}


class TestCreatePurchaseOrder:
    """Test suite for creating purchase orders."""

    def test_create_returns_pending_po(self, client, backlog_item_id):
        response = client.post("/api/purchase-orders", json=po_payload(backlog_item_id))
        assert response.status_code == 201

        po = response.json()
        assert po["id"] == "PO-0001"
        assert po["backlog_item_id"] == backlog_item_id
        assert po["status"] == "Pending"
        assert po["created_date"] == date.today().isoformat()

    def test_second_po_for_same_item_is_conflict(self, client, backlog_item_id):
        client.post("/api/purchase-orders", json=po_payload(backlog_item_id))
        response = client.post("/api/purchase-orders", json=po_payload(backlog_item_id))
        assert response.status_code == 409

    def test_unknown_backlog_item_is_404(self, client):
        response = client.post("/api/purchase-orders", json=po_payload("does-not-exist"))
        assert response.status_code == 404

    @pytest.mark.parametrize("overrides", [
        {"supplier_name": "  "},
        {"quantity": 0},
        {"unit_cost": -1},
        {"expected_delivery_date": "soon"},
        {"expected_delivery_date": (date.today() - timedelta(days=1)).isoformat()},
    ])
    def test_invalid_input_rejected(self, client, backlog_item_id, overrides):
        response = client.post("/api/purchase-orders", json=po_payload(backlog_item_id, **overrides))
        assert response.status_code == 400

    def test_non_finite_unit_cost_rejected(self, client, backlog_item_id):
        # json.dumps would emit NaN, which is not valid JSON; send the raw token as the client could
        response = client.post(
            "/api/purchase-orders",
            content='{"backlog_item_id": "%s", "supplier_name": "A", "quantity": 1, '
                    '"unit_cost": NaN, "expected_delivery_date": "%s"}'
                    % (backlog_item_id, (date.today() + timedelta(days=1)).isoformat()),
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in (400, 422)


class TestGetPurchaseOrder:
    """Test suite for reading purchase orders and their effect on the backlog."""

    def test_get_by_backlog_item(self, client, backlog_item_id):
        created = client.post("/api/purchase-orders", json=po_payload(backlog_item_id)).json()
        response = client.get(f"/api/purchase-orders/{backlog_item_id}")
        assert response.status_code == 200
        assert response.json() == created

    def test_get_without_po_is_404(self, client, backlog_item_id):
        assert client.get(f"/api/purchase-orders/{backlog_item_id}").status_code == 404

    def test_backlog_reports_purchase_order(self, client, backlog_item_id):
        before = next(b for b in client.get("/api/backlog").json() if b["id"] == backlog_item_id)
        assert before["purchase_order_id"] is None
        assert before["has_purchase_order"] is False

        po = client.post("/api/purchase-orders", json=po_payload(backlog_item_id)).json()
        after = next(b for b in client.get("/api/backlog").json() if b["id"] == backlog_item_id)
        assert after["purchase_order_id"] == po["id"]
        assert after["has_purchase_order"] is True
        assert after["purchase_order"]["supplier_name"] == "Acme Parts"
