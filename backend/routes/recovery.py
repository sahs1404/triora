from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import MaterialDB
from schemas.recovery_schema import RecoveryRecommendation
from services.recovery_service import get_recovery_recommendation

router = APIRouter(prefix="/project", tags=["recovery"])


@router.get("/{project_name}/material/{material_id}/recovery", response_model=RecoveryRecommendation)
def recovery_options(project_name: str, material_id: str, db: Session = Depends(get_db)):
    material = db.query(MaterialDB).filter(
        MaterialDB.project_id == project_name, MaterialDB.id == material_id
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail=f"Material '{material_id}' not found in '{project_name}'")

    class _MaterialLike:
        material_id = material.id
        name = material.name
        status = material.status
        p_delay = material.p_delay or 0.0
        lead_time_days = material.lead_time_days

    approx_float = 0 if material.status == "critical" else 5
    approx_blast_radius = 5

    recommendation = get_recovery_recommendation(
        material=_MaterialLike(),
        activity_float_days=approx_float,
        blast_radius=approx_blast_radius,
    )
    return recommendation