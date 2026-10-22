"""
Tests for task API endpoints.
"""
import pytest

import main


@pytest.fixture(autouse=True)
def reset_tasks():
    """Keep tasks from leaking between tests (the app is module-global)."""
    main.tasks.clear()
    yield
    main.tasks.clear()


NEW_TASK = {"title": "Check stock", "priority": "high", "dueDate": "2025-10-20"}


class TestTasks:
    """Test suite for the tasks endpoints."""

    def test_list_starts_empty(self, client):
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_returns_pending_task_with_id_outside_mock_range(self, client):
        response = client.post("/api/tasks", json=NEW_TASK)
        assert response.status_code == 201

        task = response.json()
        assert task["title"] == "Check stock"
        assert task["status"] == "pending"
        # The client treats ids 1-4 as mock tasks, so API ids must stay clear of them
        assert task["id"] >= 1000

    def test_list_is_newest_first(self, client):
        client.post("/api/tasks", json={**NEW_TASK, "title": "first"})
        client.post("/api/tasks", json={**NEW_TASK, "title": "second"})
        titles = [t["title"] for t in client.get("/api/tasks").json()]
        assert titles == ["second", "first"]

    @pytest.mark.parametrize("payload", [
        {**NEW_TASK, "title": "   "},
        {**NEW_TASK, "priority": "urgent"},
        {**NEW_TASK, "dueDate": "next week"},
    ])
    def test_create_rejects_invalid_input(self, client, payload):
        assert client.post("/api/tasks", json=payload).status_code == 400

    def test_toggle_flips_status_both_ways(self, client):
        task_id = client.post("/api/tasks", json=NEW_TASK).json()["id"]
        assert client.patch(f"/api/tasks/{task_id}").json()["status"] == "completed"
        assert client.patch(f"/api/tasks/{task_id}").json()["status"] == "pending"

    def test_delete_removes_task(self, client):
        task_id = client.post("/api/tasks", json=NEW_TASK).json()["id"]
        assert client.delete(f"/api/tasks/{task_id}").status_code == 200
        assert client.get("/api/tasks").json() == []

    def test_toggle_and_delete_unknown_id_return_404(self, client):
        assert client.patch("/api/tasks/99999").status_code == 404
        assert client.delete("/api/tasks/99999").status_code == 404
