from pydantic import BaseModel
from schemas.activity_schema import Activity
from schemas.material_schema import Material, MaterialScore
from schemas.vendor_schema import Vendor


class ProjectInput(BaseModel):
    """What gets POSTed to /project/build — the full upload contract."""
    project_name: str
    activities: list[Activity]
    materials: list[Material]
    vendors: list[Vendor] = []


class ProjectSummary(BaseModel):
    """Top-level project health — what the dashboard shows first."""
    project_name: str
    total_materials: int
    critical_count: int
    watch_count: int
    project_duration_days: int
    critical_path: list[str]


class ProjectState(BaseModel):
    """Full computed state — returned by /project/build, cached for what-if calls."""
    summary: ProjectSummary
    materials: list[MaterialScore]