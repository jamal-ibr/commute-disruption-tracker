import pytest
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

@pytest.mark.parametrize("line_id", ["victoria", "central"])
def test_line_status_endpoint_exists(line_id: str):
   """
   This test checks:
   - the endpoint responds
   - returns expected fields
   It does NOT assert TfL’s real-world status values
   because that would make tests flaky (external dependency).
   """
   r = client.get(f"/line-status?line_id={line_id}")
   # We accept either:
   # - 200 if TfL reachable
   # - 502 if TfL unreachable (still correct behaviour)
   assert r.status_code in (200, 502)
   if r.status_code == 200:
       body = r.json()
       assert "line_id" in body
       assert "status" in body
       assert "severity" in body
       assert "requested_at" in body