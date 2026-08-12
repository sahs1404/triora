from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import VendorDB
from schemas.vendor_schema import Vendor
from schemas.vendor_update_schema import JobOutcomeUpdate, ManualRateUpdate
from services.vendor_service import update_vendor_reliability, manual_rate_override

router = APIRouter(prefix="/project", tags=["vendors"])


@router.get("/{project_name}/vendors", response_model=list[Vendor])
def list_vendors(project_name: str, db: Session = Depends(get_db)):
    """All vendors tracked for this project, with current reliability rates."""
    rows = db.query(VendorDB).filter(VendorDB.project_id == project_name).all()
    return [
        Vendor(id=v.id, name=v.name, historical_delay_rate=v.historical_delay_rate,
               jobs_completed=v.jobs_completed, jobs_delayed=v.jobs_delayed)
        for v in rows
    ]


@router.post("/{project_name}/vendors/{vendor_id}/job-outcome", response_model=Vendor)
def record_job_outcome(project_name: str, vendor_id: str, payload: JobOutcomeUpdate,
                        db: Session = Depends(get_db)):
    """
    Records one new job outcome for a vendor and updates their reliability
    rate accordingly. This is what makes Tier 4 a LEARNING layer, not just
    a static lookup table.
    """
    vendor = db.query(VendorDB).filter(
        VendorDB.project_id == project_name, VendorDB.id == vendor_id
    ).first()
    if not vendor:
        raise HTTPException(status_code=404, detail=f"Vendor '{vendor_id}' not found in '{project_name}'")

    updated = update_vendor_reliability(
        current_rate=vendor.historical_delay_rate,
        jobs_completed=vendor.jobs_completed,
        jobs_delayed=vendor.jobs_delayed,
        new_job_was_delayed=payload.was_delayed,
    )

    vendor.historical_delay_rate = updated["historical_delay_rate"]
    vendor.jobs_completed = updated["jobs_completed"]
    vendor.jobs_delayed = updated["jobs_delayed"]
    db.commit()
    db.refresh(vendor)

    return Vendor(id=vendor.id, name=vendor.name, historical_delay_rate=vendor.historical_delay_rate,
                  jobs_completed=vendor.jobs_completed, jobs_delayed=vendor.jobs_delayed)


@router.post("/{project_name}/vendors/{vendor_id}/override", response_model=Vendor)
def override_vendor_rate(project_name: str, vendor_id: str, payload: ManualRateUpdate,
                          db: Session = Depends(get_db)):
    """Directly set a vendor's reliability rate, bypassing the job-outcome history."""
    vendor = db.query(VendorDB).filter(
        VendorDB.project_id == project_name, VendorDB.id == vendor_id
    ).first()
    if not vendor:
        raise HTTPException(status_code=404, detail=f"Vendor '{vendor_id}' not found in '{project_name}'")

    vendor.historical_delay_rate = manual_rate_override(payload.new_rate)
    db.commit()
    db.refresh(vendor)

    return Vendor(id=vendor.id, name=vendor.name, historical_delay_rate=vendor.historical_delay_rate,
                  jobs_completed=vendor.jobs_completed, jobs_delayed=vendor.jobs_delayed)