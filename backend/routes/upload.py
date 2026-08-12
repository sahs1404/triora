from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.project_schema import ProjectInput, ProjectState
from services.cwrs_service import score_materials
from database.session import get_db
from database.models import ProjectDB, ActivityDB, MaterialDB, VendorDB

router = APIRouter(prefix="/project", tags=["project"])


@router.post("/build", response_model=ProjectState)
def build_project(payload: ProjectInput, db: Session = Depends(get_db)):
    """
    Accepts activities + materials + vendors, runs the CWRS engine,
    persists the result, and returns the full ranked ProjectState.
    """
    try:
        result = score_materials(
            materials=payload.materials,
            activities=payload.activities,
            vendors=payload.vendors,
            project_name=payload.project_name,
        )
    except ValueError as e:
        # bad graph data (cycle, missing reference) -> tell the caller clearly
        raise HTTPException(status_code=400, detail=str(e))

    # --- persist to DB (replace if project with this name already exists) ---
    existing = db.query(ProjectDB).filter(ProjectDB.id == payload.project_name).first()
    if existing:
        db.delete(existing)
        db.commit()

    project_row = ProjectDB(
        id=payload.project_name,
        project_duration_days=result.summary.project_duration_days,
    )
    db.add(project_row)

    for a in payload.activities:
        db.add(ActivityDB(
            id=a.id, project_id=payload.project_name, name=a.name,
            duration_days=a.duration_days, predecessors="|".join(a.predecessors),
        ))

    for v in payload.vendors:
        db.add(VendorDB(
            id=v.id, project_id=payload.project_name, name=v.name,
            historical_delay_rate=v.historical_delay_rate,
            jobs_completed=v.jobs_completed, jobs_delayed=v.jobs_delayed,
        ))

    scored_map = {s.material_id: s for s in result.materials}
    for m in payload.materials:
        s = scored_map[m.id]
        db.add(MaterialDB(
            id=m.id, project_id=payload.project_name, name=m.name,
            activity_id=m.activity_id, vendor_id=m.vendor_id,
            lead_time_days=m.lead_time_days,
            vendor_reported_status=m.vendor_reported_status,
            manual_p_delay_override=m.manual_p_delay_override,
            p_delay=s.p_delay, cwrs=s.cwrs, rank=s.rank,
            status=s.status, reason=s.reason,
        ))

    db.commit()

    return result