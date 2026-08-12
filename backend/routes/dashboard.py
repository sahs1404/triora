from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import ProjectDB, ActivityDB, MaterialDB
from schemas.project_schema import ProjectSummary, ProjectState
from schemas.material_schema import MaterialScore
from schemas.activity_schema import Activity
from services.graph_service import build_schedule_graph
from services.cpm_service import compute_cpm

router = APIRouter(prefix="/project", tags=["dashboard"])


def _load_project_state(project_name: str, db: Session) -> ProjectState:
    """Shared logic: rebuilds ProjectState from the DB for a given project."""
    project = db.query(ProjectDB).filter(ProjectDB.id == project_name).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")

    activity_rows = db.query(ActivityDB).filter(ActivityDB.project_id == project_name).all()
    material_rows = db.query(MaterialDB).filter(MaterialDB.project_id == project_name).all()

    activities = [
        Activity(
            id=a.id, name=a.name, duration_days=a.duration_days,
            predecessors=a.predecessors.split("|") if a.predecessors else [],
        )
        for a in activity_rows
    ]
    activity_name_map = {a.id: a.name for a in activity_rows}

    # Recompute float/blast-radius/critical-path fresh, rather than trusting
    # stale stored values — guarantees the read is always consistent with
    # the actual schedule graph.
    G = build_schedule_graph(activities)
    cpm = compute_cpm(G)

    materials = [
        MaterialScore(
            material_id=m.id, name=m.name, activity_id=m.activity_id,
            activity_name=activity_name_map.get(m.activity_id, "Unknown"),
            lead_time_days=m.lead_time_days,
            p_delay=m.p_delay or 0.0,
            activity_float_days=cpm["float_days"].get(m.activity_id, 0),
            urgency=round(1 - min(max(cpm["float_days"].get(m.activity_id, 0) / max(m.lead_time_days, 1), 0), 1), 3),
            blast_radius=cpm["blast_radius"].get(m.activity_id, 0),
            blast_radius_norm=0.0,  # display-only field; not needed for correctness here
            cwrs=m.cwrs or 0.0, rank=m.rank or 0,
            status=m.status or "safe", reason=m.reason or "",
        )
        for m in material_rows
    ]
    materials.sort(key=lambda x: x.rank)

    summary = ProjectSummary(
        project_name=project_name,
        total_materials=len(materials),
        critical_count=sum(1 for x in materials if x.status == "critical"),
        watch_count=sum(1 for x in materials if x.status == "watch"),
        project_duration_days=cpm["project_duration"],
        critical_path=cpm["critical_path"],
    )

    return ProjectState(summary=summary, materials=materials)


@router.get("/list")
def list_projects(db: Session = Depends(get_db)):
    """Returns all saved project names — for a project switcher in the frontend."""
    projects = db.query(ProjectDB).all()
    return [{"project_name": p.id, "created_at": p.created_at} for p in projects]


@router.get("/{project_name}", response_model=ProjectState)
def get_project(project_name: str, db: Session = Depends(get_db)):
    """Full project state — summary + full ranked material list."""
    return _load_project_state(project_name, db)


@router.get("/{project_name}/summary", response_model=ProjectSummary)
def get_summary(project_name: str, db: Session = Depends(get_db)):
    """Just the top-level health numbers — for the dashboard's KPI cards."""
    return _load_project_state(project_name, db).summary


@router.get("/{project_name}/material/{material_id}", response_model=MaterialScore)
def get_material(project_name: str, material_id: str, db: Session = Depends(get_db)):
    """Single material's full CWRS breakdown — for the detail panel."""
    state = _load_project_state(project_name, db)
    material = next((m for m in state.materials if m.material_id == material_id), None)
    if not material:
        raise HTTPException(status_code=404, detail=f"Material '{material_id}' not found in '{project_name}'")
    return material