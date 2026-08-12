"""
Vendor reliability learning — Tier 4.

Uses a simple weighted-average update rule rather than a naive replace,
so one bad delivery doesn't swing a vendor's entire reliability score
overnight. This mirrors how a real PM would (and should) reason: trust
history, but let new evidence nudge it.
"""


def update_vendor_reliability(current_rate: float, jobs_completed: int,
                                jobs_delayed: int, new_job_was_delayed: bool) -> dict:
    """
    Returns updated (historical_delay_rate, jobs_completed, jobs_delayed)
    after recording one new job outcome.

    Weighted-average logic: the new outcome counts as 1 data point among
    (jobs_completed + 1) total — so a vendor with a long track record
    moves slowly, and a new vendor with few jobs moves quickly. This is
    intentional: more history should mean more inertia.
    """
    new_jobs_completed = jobs_completed + 1
    new_jobs_delayed = jobs_delayed + (1 if new_job_was_delayed else 0)

    # Recompute rate directly from counts rather than blending floats —
    # this keeps rate and counts always consistent with each other,
    # which matters once someone inspects jobs_completed/jobs_delayed directly.
    new_rate = new_jobs_delayed / new_jobs_completed if new_jobs_completed > 0 else current_rate

    return {
        "historical_delay_rate": round(new_rate, 4),
        "jobs_completed": new_jobs_completed,
        "jobs_delayed": new_jobs_delayed,
    }


def manual_rate_override(new_rate: float) -> float:
    """
    For a PM who wants to directly set a vendor's rate (e.g. based on
    outside knowledge Triora doesn't have yet) rather than recording
    a job outcome. Simple clamp to keep it a valid probability.
    """
    return min(max(new_rate, 0.0), 0.99)