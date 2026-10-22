"""
Tests for restocking API endpoints.
"""
import pytest

import main


@pytest.fixture(autouse=True)
def reset_submitted_orders():
    """Keep submitted orders from leaking between tests (the app is module-global)."""
    main.submitted_orders.clear()
    yield
    main.submitted_orders.clear()


class TestRestockingRecommendations:
    """Test suite for the restocking recommendation endpoint."""

    def test_zero_budget_returns_no_items(self, client):
        """Test that a zero budget recommends nothing."""
        response = client.get("/api/restocking/recommendations?budget=0")
        assert response.status_code == 200

        data = response.json()
        assert data["items"] == []
        assert data["total_cost"] == 0
        assert data["remaining_budget"] == 0

    def test_negative_budget_rejected(self, client):
        """Test that a negative budget returns 400."""
        response = client.get("/api/restocking/recommendations?budget=-1")
        assert response.status_code == 400

    def test_non_finite_budget_rejected(self, client):
        """Test that NaN and infinite budgets are rejected instead of causing a 500."""
        for budget in ["nan", "inf", "-inf"]:
            response = client.get(f"/api/restocking/recommendations?budget={budget}")
            assert response.status_code in (400, 422)

    def test_missing_budget_rejected(self, client):
        """Test that the budget parameter is required."""
        response = client.get("/api/restocking/recommendations")
        assert response.status_code == 422

    def test_recommendations_stay_within_budget(self, client):
        """Test that the planned spend never exceeds the budget."""
        for budget in [500, 2500, 10000, 100000]:
            data = client.get(f"/api/restocking/recommendations?budget={budget}").json()
            assert data["total_cost"] <= budget
            assert data["remaining_budget"] == pytest.approx(budget - data["total_cost"], abs=0.01)
            assert sum(i["line_total"] for i in data["items"]) == pytest.approx(data["total_cost"], abs=0.01)

    def test_item_structure(self, client):
        """Test that recommended items carry the expected fields."""
        data = client.get("/api/restocking/recommendations?budget=100000").json()
        assert len(data["items"]) > 0

        item = data["items"][0]
        for field in ["sku", "name", "trend", "shortfall", "quantity", "unit_cost",
                      "supplier", "lead_time_days", "line_total"]:
            assert field in item

    def test_items_never_exceed_shortfall(self, client):
        """Test that quantities are positive and capped at the forecast shortfall."""
        data = client.get("/api/restocking/recommendations?budget=100000").json()
        for item in data["items"]:
            assert 1 <= item["quantity"] <= item["shortfall"]

    def test_decreasing_items_excluded(self, client):
        """Test that items with falling demand are never recommended."""
        forecasts = client.get("/api/demand").json()
        falling = {f["item_sku"] for f in forecasts if f["forecasted_demand"] <= f["current_demand"]}

        data = client.get("/api/restocking/recommendations?budget=100000").json()
        assert falling
        assert not falling & {i["sku"] for i in data["items"]}

    def test_increasing_trends_ranked_first(self, client):
        """Test that growing items come before stable ones."""
        data = client.get("/api/restocking/recommendations?budget=100000").json()
        trends = [i["trend"] for i in data["items"]]

        assert "increasing" in trends
        first_non_increasing = next((n for n, t in enumerate(trends) if t != "increasing"), len(trends))
        assert all(t != "increasing" for t in trends[first_non_increasing:])

    def test_larger_budget_never_buys_less(self, client):
        """Test that raising the budget never lowers the planned spend."""
        spends = [
            client.get(f"/api/restocking/recommendations?budget={b}").json()["total_cost"]
            for b in [0, 1000, 5000, 20000, 100000]
        ]
        assert spends == sorted(spends)


class TestSubmitRestockingOrder:
    """Test suite for submitting and listing restocking orders."""

    def test_submit_order(self, client):
        """Test that a valid order is created with server-side totals and lead time."""
        rec = client.get("/api/restocking/recommendations?budget=100000").json()
        lines = [{"sku": i["sku"], "quantity": i["quantity"]} for i in rec["items"]]

        response = client.post("/api/restocking/orders", json={"budget": 100000, "items": lines})
        assert response.status_code == 201

        order = response.json()
        assert order["id"].startswith("RST-")
        assert order["status"] == "Submitted"
        assert order["total_cost"] == pytest.approx(rec["total_cost"], abs=0.01)
        assert order["overall_lead_time_days"] == max(i["lead_time_days"] for i in rec["items"])
        assert "expected_delivery" in order

    def test_submitted_order_appears_in_list(self, client):
        """Test that a submitted order is returned by the list endpoint."""
        rec = client.get("/api/restocking/recommendations?budget=5000").json()
        lines = [{"sku": i["sku"], "quantity": i["quantity"]} for i in rec["items"]]
        order_id = client.post("/api/restocking/orders", json={"budget": 5000, "items": lines}).json()["id"]

        response = client.get("/api/restocking/orders")
        assert response.status_code == 200
        assert order_id in [o["id"] for o in response.json()]

    def test_client_supplied_prices_ignored(self, client):
        """Test that extra price fields in the request cannot change the total."""
        rec = client.get("/api/restocking/recommendations?budget=100000").json()
        item = rec["items"][0]
        body = {"budget": 100000, "items": [{"sku": item["sku"], "quantity": 1, "unit_cost": 0.01}]}

        order = client.post("/api/restocking/orders", json=body).json()
        assert order["total_cost"] == pytest.approx(item["unit_cost"], abs=0.01)

    def test_over_budget_rejected(self, client):
        """Test that an order costing more than the budget returns 400."""
        sku = client.get("/api/restocking/recommendations?budget=100000").json()["items"][0]["sku"]
        response = client.post("/api/restocking/orders", json={"budget": 1, "items": [{"sku": sku, "quantity": 5}]})
        assert response.status_code == 400

    def test_empty_order_rejected(self, client):
        """Test that an order with no items returns 400."""
        response = client.post("/api/restocking/orders", json={"budget": 1000, "items": []})
        assert response.status_code == 400

    def test_unknown_sku_rejected(self, client):
        """Test that an unknown SKU returns 400."""
        response = client.post("/api/restocking/orders",
                               json={"budget": 1000, "items": [{"sku": "NOPE-000", "quantity": 1}]})
        assert response.status_code == 400

    def test_non_positive_quantity_rejected(self, client):
        """Test that a zero or negative quantity returns 400."""
        sku = client.get("/api/restocking/recommendations?budget=100000").json()["items"][0]["sku"]
        for qty in [0, -3]:
            response = client.post("/api/restocking/orders",
                                   json={"budget": 1000, "items": [{"sku": sku, "quantity": qty}]})
            assert response.status_code == 400

    def test_non_finite_budget_rejected(self, client):
        """Test that a NaN budget cannot bypass the over-budget check."""
        sku = client.get("/api/restocking/recommendations?budget=100000").json()["items"][0]["sku"]
        response = client.post("/api/restocking/orders",
                               data='{"budget": NaN, "items": [{"sku": "%s", "quantity": 1}]}' % sku,
                               headers={"Content-Type": "application/json"})
        assert response.status_code == 400

    def test_duplicate_sku_rejected(self, client):
        """Test that the same SKU cannot appear twice in one order."""
        sku = client.get("/api/restocking/recommendations?budget=100000").json()["items"][0]["sku"]
        lines = [{"sku": sku, "quantity": 1}, {"sku": sku, "quantity": 1}]
        response = client.post("/api/restocking/orders", json={"budget": 100000, "items": lines})
        assert response.status_code == 400

    def test_quantity_above_shortfall_rejected(self, client):
        """Test that quantity cannot exceed the forecast shortfall."""
        item = client.get("/api/restocking/recommendations?budget=100000").json()["items"][0]
        lines = [{"sku": item["sku"], "quantity": item["shortfall"] + 1}]
        response = client.post("/api/restocking/orders", json={"budget": 10000000, "items": lines})
        assert response.status_code == 400

    def test_item_without_shortfall_rejected(self, client):
        """Test that items with falling demand cannot be ordered."""
        falling = next(f for f in client.get("/api/demand").json()
                       if f["forecasted_demand"] <= f["current_demand"])
        response = client.post("/api/restocking/orders",
                               json={"budget": 100000, "items": [{"sku": falling["item_sku"], "quantity": 1}]})
        assert response.status_code == 400

    def test_order_ids_are_unique(self, client):
        """Test that consecutive orders get distinct IDs."""
        sku = client.get("/api/restocking/recommendations?budget=100000").json()["items"][0]["sku"]
        ids = {
            client.post("/api/restocking/orders",
                        json={"budget": 100000, "items": [{"sku": sku, "quantity": 1}]}).json()["id"]
            for _ in range(5)
        }
        assert len(ids) == 5

    def test_ordered_units_are_not_recommended_again(self, client):
        """Test that a placed order is subtracted from later recommendations and orders."""
        rec = client.get("/api/restocking/recommendations?budget=100000").json()
        lines = [{"sku": i["sku"], "quantity": i["quantity"]} for i in rec["items"]]
        assert client.post("/api/restocking/orders", json={"budget": 100000, "items": lines}).status_code == 201

        after = client.get("/api/restocking/recommendations?budget=100000").json()
        assert after["items"] == []

        # Re-submitting the same lines must now be rejected as exceeding the remaining shortfall
        again = client.post("/api/restocking/orders", json={"budget": 100000, "items": lines})
        assert again.status_code == 400

    def test_partial_order_leaves_remaining_shortfall(self, client):
        """Test that ordering part of a shortfall leaves only the remainder recommended."""
        rec = client.get("/api/restocking/recommendations?budget=100000").json()
        item = next(i for i in rec["items"] if i["shortfall"] >= 2)
        client.post("/api/restocking/orders",
                    json={"budget": 100000, "items": [{"sku": item["sku"], "quantity": 1}]})

        after = client.get("/api/restocking/recommendations?budget=100000").json()
        remaining = next(i for i in after["items"] if i["sku"] == item["sku"])
        assert remaining["shortfall"] == item["shortfall"] - 1
