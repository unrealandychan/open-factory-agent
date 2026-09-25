"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
from open_factory.api.main import app

client = TestClient(app)


def test_system_health():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_workflow_lifecycle():
    # 1. Create workflow
    payload = {
        "name": "API Test Workflow",
        "description": "Integration test created",
        "steps": [
            {
                "id": "step-echo",
                "title": "Echo Step",
                "type": "command",
                "command": "echo 'api test'",
            }
        ],
    }
    create_res = client.post("/api/v1/workflows", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    wf_id = created["id"]
    assert created["name"] == "API Test Workflow"

    # 2. Get workflow
    get_res = client.get(f"/api/v1/workflows/{wf_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == wf_id

    # 3. Trigger run
    run_res = client.post("/api/v1/runs", json={"workflow_id": wf_id})
    assert run_res.status_code == 202
    run_id = run_res.json()["id"]

    # 4. Fetch run
    run_detail = client.get(f"/api/v1/runs/{run_id}")
    assert run_detail.status_code == 200
    assert run_detail.json()["workflow_id"] == wf_id

    # 5. List workflows
    list_res = client.get("/api/v1/workflows")
    assert list_res.status_code == 200
    assert any(w["id"] == wf_id for w in list_res.json()["workflows"])

    # 6. Delete workflow
    del_res = client.delete(f"/api/v1/workflows/{wf_id}")
    assert del_res.status_code == 204
