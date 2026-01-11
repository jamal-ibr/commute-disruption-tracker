from fastapi import FastAPI, Depends, HTTPException, Query

from sqlalchemy.orm import Session

from sqlalchemy import select

from app.db import Base, engine, get_db

from app.models import LineStatusRequest

from app.schemas import HealthResponse, LineStatusResponse, HistoryItem

from app.services.tfl_client import fetch_line_status

from fastapi.responses import HTMLResponse

from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

from fastapi import Request

# Create tables on startup for local/dev.

# In mature systems you would use migrations (e.g., Alembic),

# but for this assignment we keep scope controlled and explain the limitation.

Base.metadata.create_all(bind=engine)

app = FastAPI(

    title="Commute Disruption Tracker",

    description="Fetches TfL line status and stores a request history for traceability.",

    version="0.1.0",

)

# Serve static files (JS/CSS) and HTML templates for a minimal UI.
# This avoids a separate front-end build toolchain, keeping scope controlled.
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
   """
   Minimal UI entry point.
   Rationale:
   - Provides a visible demonstration of live data.
   - Avoids React/Node complexity which is out-of-scope for a DevOps pipeline assessment.
   """
   return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health", response_model=HealthResponse)

def health():

    # Health endpoints must be fast and not depend on external services.

    return {"status": "ok"}


@app.get("/line-status", response_model=LineStatusResponse)

async def line_status(

    line_id: str = Query(..., description="TfL line id, e.g. victoria, central, jubilee"),

    db: Session = Depends(get_db),

):

    """

    Fetch current status for a line and record it in the database.

    Marker-critical points:

    - External API call demonstrates integration.

    - DB write demonstrates persistence and traceability.

    - Separation of concerns: TfL logic is in a service module.

    """

    try:

        tfl = await fetch_line_status(line_id=line_id)

    except Exception as ex:

        # Keep error message controlled; don’t leak internals.

        raise HTTPException(status_code=502, detail="Upstream TfL API request failed") from ex

    record = LineStatusRequest(

        line_id=line_id.lower().strip(),

        status=tfl["status"],

        severity=tfl["severity"],

        reason=tfl.get("reason"),

    )

    db.add(record)

    db.commit()

    db.refresh(record)

    return {

        "line_id": record.line_id,

        "status": record.status,

        "severity": record.severity,

        "reason": record.reason,

        "requested_at": record.requested_at,

    }


@app.get("/history", response_model=list[HistoryItem])

def history(

    limit: int = Query(20, ge=1, le=100, description="How many recent requests to return"),

    db: Session = Depends(get_db),

):

    """

    Returns recent request history.

    Why it matters:

    - Easy evidence in the demo that the DB is working in AWS.

    """

    stmt = select(LineStatusRequest).order_by(LineStatusRequest.requested_at.desc()).limit(limit)

    rows = db.execute(stmt).scalars().all()

    return [

        {

            "id": r.id,

            "line_id": r.line_id,

            "status": r.status,

            "severity": r.severity,

            "reason": r.reason,

            "requested_at": r.requested_at,

        }

        for r in rows

    ]
 