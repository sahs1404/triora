from schemas.activity_schema import Activity
from schemas.material_schema import Material, MaterialScore
from schemas.vendor_schema import Vendor
from schemas.project_schema import ProjectSummary, ProjectState
from services.graph_service import build_schedule_graph
from services.cpm_service import compute_cpm


CRITICAL_THRESHOLD = 0.30   # CWRS at or above this -> "critical"
WATCH_THRESHOLD = 0.15      # CWRS at or above this -> "watch", else "safe"


def _status_for(cwrs: float) -> str:
    if cwrs >= CRITICAL_THRESHOLD:
        return "critical"
    if cwrs >= WATCH_THRESHOLD:
        return "watch"
    return "safe"


def _reason_for(status: str, material_name: str, activity_name: str,
                 p_delay: float, float_days: int, blast_radius: int) -> str:
    if status == "critical":
        return (f"{material_name} has zero schedule float on {activity_name} and "
                f"blocks {blast_radius} downstream activities. A delay here reaches "
                f"the project milestone directly.")
    if status == "watch":
        return (f"{material_name} carries some risk ({round(p_delay * 100)}% delay "
                f"probability) but has {float_days} days of float or limited "
                f"downstream impact — worth monitoring, not urgent.")
    return (f"{material_name} is low priority: either low delay probability, "
            f"ample schedule float ({float_days} days), or minimal downstream impact.")


def score_materials(materials: list[Material], activities: list[Activity],
                     vendors: list[Vendor] | None = None,
                     project_name: str = "") -> ProjectState:
    """
    Main entry point: builds the graph, runs CPM, computes CWRS for every
    material, and returns the full ranked ProjectState.

    P(delay) priority: manual_p_delay_override > vendor's historical_delay_rate
    > neutral default (0.2) if no vendor is assigned yet.
    """
    vendors = vendors or []
    vendor_map = {v.id: v for v in vendors}

    G = build_schedule_graph(activities)
    cpm = compute_cpm(G)
    activity_map = {a.id: a for a in activities}

    max_blast = max(cpm["blast_radius"].values()) if cpm["blast_radius"] else 1
    max_blast = max_blast or 1  # guard against divide-by-zero on a trivial 1-activity project

    scored = []
    for m in materials:
        if m.activity_id not in activity_map:
            raise ValueError(f"Material '{m.id}' references unknown activity '{m.activity_id}'")

        act = activity_map[m.activity_id]

        if m.manual_p_delay_override is not None:
            p_delay = m.manual_p_delay_override
        elif m.vendor_id and m.vendor_id in vendor_map:
            p_delay = vendor_map[m.vendor_id].historical_delay_rate
        else:
            p_delay = 0.2  # neutral default when there's no evidence yet

        p_delay = min(max(p_delay, 0.0), 0.99)

        act_float = cpm["float_days"][m.activity_id]
        float_ratio = min(max(act_float / m.lead_time_days, 0.0), 1.0) if m.lead_time_days > 0 else 0.0
        urgency = 1 - float_ratio

        br = cpm["blast_radius"][m.activity_id]
        br_norm = br / max_blast

        cwrs = round(p_delay * urgency * (0.15 + 0.85 * br_norm), 4)
        status = _status_for(cwrs)
        reason = _reason_for(status, m.name, act.name, p_delay, act_float, br)

        scored.append(MaterialScore(
            material_id=m.id, name=m.name, activity_id=m.activity_id,
            activity_name=act.name, lead_time_days=m.lead_time_days,
            p_delay=round(p_delay, 3), activity_float_days=act_float,
            urgency=round(urgency, 3), blast_radius=br, blast_radius_norm=round(br_norm, 3),
            cwrs=cwrs, rank=0, status=status, reason=reason,
        ))

    scored.sort(key=lambda s: s.cwrs, reverse=True)
    for i, s in enumerate(scored):
        s.rank = i + 1

    summary = ProjectSummary(
        project_name=project_name,
        total_materials=len(scored),
        critical_count=sum(1 for s in scored if s.status == "critical"),
        watch_count=sum(1 for s in scored if s.status == "watch"),
        project_duration_days=cpm["project_duration"],
        critical_path=cpm["critical_path"],
    )

    return ProjectState(summary=summary, materials=scored)