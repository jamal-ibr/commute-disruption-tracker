import pytest
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

@pytest.mark.parametrize("line_id", ["victoria", "central"])
def test_line_status_endpoint_exists(client, line_id: str):
   """
   This test checks:
   - the endpoint responds
   - returns expected fields
   It does NOT assert TfL’s real-world status values
   because that would make tests flaky (external dependency).
   """
   r = client.get(f"/line-status?line_id={line_id}")
   assert r.status_code == 200
   data = r.json()
   assert "line_id" in data
   assert "status" in data
   assert "severity" in data