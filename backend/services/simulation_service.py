from schemas.activity_schema import Activity
from schemas.material_schema import Material
from schemas.vendor_schema import Vendor
from schemas.whatif_schema import WhatIfChange, WhatIfResult
from services.cwrs_service import score_materials


def apply_whatif_changes(activities: list[Activity], materials: list[Material],
                          changes: list[WhatIfChange]) -> tuple[list[Activity], list[Material]]:
    """
    Applies changes to COPIES of activities/materials — never mutates the
    originals, since "before" still needs to be scored with the real data.
    """
    activities = [a.model_copy(deep=True) for a in activities]
    materials = [m.model_copy(deep=True) for m in materials]

    act_map = {a.id: a for a in activities}
    mat_map = {m.id: m for m in materials}

    for change in changes:
        if change.change_type == "change_duration":
            if change.target_id not in act_map:
                raise ValueError(f"Unknown activity_id '{change.target_id}' in what-if change")
            new_dur = int(change.value)
            if new_dur < 1:
                raise ValueError(f"Duration must be at least 1 day (got {new_dur})")
            act_map[change.target_id].duration_days = new_dur

        elif change.change_type == "expedite_material":
            if change.target_id not in mat_map:
                raise ValueError(f"Unknown material_id '{change.target_id}' in what-if change")
            mat_map[change.target_id].lead_time_days = max(
                1, int(mat_map[change.target_id].lead_time_days - float(change.value))
            )

        elif change.change_type == "delay_material":
            if change.target_id not in mat_map:
                raise ValueError(f"Unknown material_id '{change.target_id}' in what-if change")
            mat_map[change.target_id].lead_time_days = int(
                mat_map[change.target_id].lead_time_days + float(change.value)
            )

        elif change.change_type == "reassign_vendor":
            if change.target_id not in mat_map:
                raise ValueError(f"Unknown material_id '{change.target_id}' in what-if change")
            # value is the new vendor_id as a string — applied ONLY to this
            # copy, so "before" (scored from the original materials) is
            # never affected.
            mat_map[change.target_id].vendor_id = str(change.value)

    return activities, materials


def run_whatif(activities: list[Activity], materials: list[Material],
                vendors: list[Vendor], changes: list[WhatIfChange],
                project_name: str) -> WhatIfResult:
    """
    Scores the project as-is ("before"), applies the changes to copies
    ("after"), and returns both states plus the computed delta.
    """
    before = score_materials(materials, activities, vendors, project_name)

    new_activities, new_materials = apply_whatif_changes(activities, materials, changes)
    after = score_materials(new_materials, new_activities, vendors, project_name)

    duration_delta = after.summary.project_duration_days - before.summary.project_duration_days

    before_status = {m.material_id: m.status for m in before.materials}
    after_status = {m.material_id: m.status for m in after.materials}
    changed = [
        mid for mid in before_status
        if mid in after_status and before_status[mid] != after_status[mid]
    ]

    return WhatIfResult(
        before=before, after=after,
        project_duration_delta_days=duration_delta,
        materials_changed_status=changed,
    )