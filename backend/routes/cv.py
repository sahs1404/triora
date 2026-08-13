"""
Main-backend route for CV site-photo verification. Accepts a photo +
material_id + expected_stage, forwards the photo to the separate ML
inference service (CV_SERVICE_URL), stores the result, and nudges the
material's p_delay based on match/mismatch — a mismatch is weak evidence
of hidden risk (e.g. vendor claims "on track" but photo shows otherwise).
"""

import os
import requests

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import MaterialDB, PhotoEvidenceDB

router = APIRouter(prefix="/evidence", tags=["cv"])

# Set this env var on the main backend to point at the deployed CV service,
# e.g. https://triora-cv.onrender.com
CV_SERVICE_URL = os.getenv("CV_SERVICE_URL", "http://127.0.0.1:8100")

MISMATCH_BUMP = 0.15
MATCH_RELIEF = 0.05


@router.post("/photo")
async def submit_photo_evidence(
    project_name: str = Form(...),
    material_id: str = Form(...),
    activity_id: str = Form(...),
    expected_stage: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    material = db.query(MaterialDB).filter(
        MaterialDB.project_id == project_name, MaterialDB.id == material_id
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail=f"Material '{material_id}' not found in '{project_name}'")

    photo_bytes = await photo.read()
    try:
        response = requests.post(
            f"{CV_SERVICE_URL}/verify",
            files={"photo": (photo.filename, photo_bytes, photo.content_type)},
            data={"expected_stage": expected_stage},
            timeout=30,
        )
        response.raise_for_status()
        cv_result = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"CV service unreachable: {e}")

    match_result = cv_result["match_result"]

    current_p_delay = material.p_delay or 0.0
    if match_result == "mismatch":
        material.p_delay = min(0.95, current_p_delay + MISMATCH_BUMP)
    elif match_result == "match":
        material.p_delay = max(0.05, current_p_delay - MATCH_RELIEF)

    evidence = PhotoEvidenceDB(
        material_id=material_id,
        project_id=project_name,
        activity_id=activity_id,
        photo_url=photo.filename,
        expected_stage=expected_stage,
        match_result=match_result,
    )
    db.add(evidence)
    db.commit()
    db.refresh(material)

    return {
        "material_id": material_id,
        "cv_result": cv_result,
        "updated_p_delay": material.p_delay,
    }