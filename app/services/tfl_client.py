import httpx

from app.config import settings


async def fetch_line_status(line_id: str) -> dict:

    """

    Calls TfL Line Status endpoint.

    Why this approach:

    - A simple, readable HTTP call (httpx).

    - Keeps external API logic separate from endpoint logic.

    Failure modes:

    - TfL API unavailable (timeouts / 5xx).

    - Unexpected response shape.

    - Rate limiting (429) if heavily used without app_key.

    Mitigation:

    - Short timeout.

    - Raise clear error for upstream failure.

    """

    url = f"{settings.tfl_base_url}/Line/{line_id}/Status"

    params = {}

    if settings.tfl_app_id and settings.tfl_app_key:

        params["app_id"] = settings.tfl_app_id

        params["app_key"] = settings.tfl_app_key

    async with httpx.AsyncClient(timeout=10.0) as client:

        r = await client.get(url, params=params)

        r.raise_for_status()

        data = r.json()

    # TfL returns a list of lines; each contains lineStatuses list.

    # We take the first line status as a simple representation.

    first = data[0]

    status_obj = first["lineStatuses"][0]

    return {

        "status": status_obj.get("statusSeverityDescription", "Unknown"),

        "severity": int(status_obj.get("statusSeverity", 0)),

        "reason": status_obj.get("reason"),

    }
 