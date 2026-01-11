import pytest
@pytest.mark.parametrize("line_id", ["victoria", "central"])
def test_line_status_endpoint_exists(client, line_id: str):
   r = client.get(f"/line-status?line_id={line_id}")
   assert r.status_code == 200
   data = r.json()
   assert "line_id" in data
   assert "status" in data
   assert "severity" in data