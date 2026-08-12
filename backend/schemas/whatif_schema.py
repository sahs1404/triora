from pydantic import BaseModel
from typing import Literal, Union
from schemas.project_schema import ProjectState


class WhatIfChange(BaseModel):
    """A single hypothetical change a user proposes in the simulator."""
    change_type: Literal["expedite_material", "delay_material", "change_duration", "reassign_vendor"]
    target_id: str                     # material_id or activity_id depending on change_type
    value: Union[float, str]           # days (float) for schedule/lead-time changes,
                                        # new vendor_id (str) for reassign_vendor


class WhatIfRequest(BaseModel):
    project_name: str
    changes: list[WhatIfChange]


class WhatIfResult(BaseModel):
    before: ProjectState
    after: ProjectState
    project_duration_delta_days: int
    materials_changed_status: list[str]