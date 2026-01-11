from sqlalchemy import Column, Integer, String, DateTime, func

from app.db import Base


class LineStatusRequest(Base):

    """

    Stores an audit trail of requests made via /line-status.

    Why this is useful:

    - Proves database integration in the deployed environment.

    - Supports traceability (what was queried, when, what was returned).

    """

    __tablename__ = "line_status_requests"

    id = Column(Integer, primary_key=True, index=True)

    line_id = Column(String, nullable=False, index=True)

    status = Column(String, nullable=False)

    severity = Column(Integer, nullable=False)

    reason = Column(String, nullable=True)

    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
 