"""
Recovery recommendation engine — Tier 3 groundwork.

Given a scored material (its p_delay, float, blast radius, status), evaluates
a fixed set of canned interventions and ranks them heuristically by estimated
days recovered vs cost/feasibility trade-off.
"""

from schemas.recovery_schema import RecoveryOption, RecoveryRecommendation


def _candidate_options(material, activity_float_days: int, blast_radius: int) -> list[RecoveryOption]:
    lead_time = material.lead_time_days
    p_delay = material.p_delay

    options = [
        RecoveryOption(
            action="Expedite Shipment",
            description="Pay a premium to rush fabrication/shipping and pull the delivery date forward.",
            estimated_days_recovered=max(1, round(lead_time * 0.25)),
            estimated_cost="High",
            feasibility="High",
            score=0,
        ),
        RecoveryOption(
            action="Partial / Split Shipment",
            description="Ship completed portions of the order now instead of waiting for the full batch.",
            estimated_days_recovered=max(1, round(lead_time * 0.15)),
            estimated_cost="Medium",
            feasibility="Medium",
            score=0,
        ),
        RecoveryOption(
            action="Source Alternate Vendor",
            description="Split or reassign the order to a more reliable vendor with faster lead time.",
            estimated_days_recovered=max(1, round(lead_time * 0.35)),
            estimated_cost="Medium",
            feasibility="Medium" if p_delay > 0.5 else "Low",
            score=0,
        ),
        RecoveryOption(
            action="Resequence Downstream Activity",
            description="Reorder or overlap downstream construction activities so the critical path isn't blocked while the material catches up.",
            estimated_days_recovered=max(1, round(activity_float_days * 0.5) + 2),
            estimated_cost="Low",
            feasibility="High" if blast_radius <= 5 else "Medium",
            score=0,
        ),
    ]

    cost_penalty = {"Low": 0, "Medium": 1, "High": 2}
    feasibility_bonus = {"High": 2, "Medium": 1, "Low": 0}

    for opt in options:
        opt.score = round(
            opt.estimated_days_recovered
            - cost_penalty[opt.estimated_cost]
            + feasibility_bonus[opt.feasibility],
            2,
        )

    return sorted(options, key=lambda o: o.score, reverse=True)


def get_recovery_recommendation(material, activity_float_days: int, blast_radius: int) -> RecoveryRecommendation:
    options = _candidate_options(material, activity_float_days, blast_radius)

    return RecoveryRecommendation(
        material_id=material.material_id,
        material_name=material.name,
        current_status=material.status,
        options=options,
        recommended_action=options[0].action if options else "No action available",
    )