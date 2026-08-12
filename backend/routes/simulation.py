from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import ProjectDB, ActivityDB, MaterialDB, VendorDB
from schemas.activity_schema import Activity
from schemas.material_schema import Material
from schemas.vendor_schema import Vendor
from schemas.whatif_schema import WhatIfRequest, WhatIfResult
from services.simulation_service import run_whatif

router = APIRouter(prefix="/project", tags=["simulation"])


@router.post("/{project_name}/whatif", response_model=WhatIfResult)
def whatif(project_name: str, payload: WhatIfRequest, db: Session = Depends(get_db)):
    """
    Runs a hypothetical scenario against a saved project without persisting
    any changes — purely a "what would happen if" query.
    """
    project = db.query(ProjectDB).filter(ProjectDB.id == project_name).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")

    activity_rows = db.query(ActivityDB).filter(ActivityDB.project_id == project_name).all()
    material_rows = db.query(MaterialDB).filter(MaterialDB.project_id == project_name).all()
    vendor_rows = db.query(VendorDB).filter(VendorDB.project_id == project_name).all()

    activities = [
        Activity(id=a.id, name=a.name, duration_days=a.duration_days,
                  predecessors=a.predecessors.split("|") if a.predecessors else [])
        for a in activity_rows
    ]
    materials = [
        Material(id=m.id, name=m.name, activity_id=m.activity_id, vendor_id=m.vendor_id,
                  lead_time_days=m.lead_time_days,
                  vendor_reported_status=m.vendor_reported_status,
                  manual_p_delay_override=m.manual_p_delay_override)
        for m in material_rows
    ]
    vendors = [
        Vendor(id=v.id, name=v.name, historical_delay_rate=v.historical_delay_rate,
               jobs_completed=v.jobs_completed, jobs_delayed=v.jobs_delayed)
        for v in vendor_rows
    ]

    try:
        result = run_whatif(activities, materials, vendors, payload.changes, project_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result