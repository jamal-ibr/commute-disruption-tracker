from pydantic import BaseModel

from datetime import datetime


class HealthResponse(BaseModel):

    status: str


class LineStatusResponse(BaseModel):

    line_id: str

    status: str

    severity: int

    reason: str | None

    requested_at: datetime


class HistoryItem(BaseModel):

    id: int

    line_id: str

    status: str

    severity: int

    reason: str | None

    requested_at: datetime
 