from pydantic import BaseModel


class RecoveryOption(BaseModel):
    """One candidate intervention for a critical/watch material."""
    action: str                       # short label e.g. "Expedite Shipment"
    description: str                  # 1-2 sentence explanation
    estimated_days_recovered: int     # how many days of delay this claws back
    estimated_cost: str               # "Low" / "Medium" / "High" (qualitative for demo)
    feasibility: str                  # "High" / "Medium" / "Low"
    score: float                      # internal ranking score (higher = better pick)


class RecoveryRecommendation(BaseModel):
    """Full recovery response for one material."""
    material_id: str
    material_name: str
    current_status: str
    options: list[RecoveryOption]
    recommended_action: str           # the top-ranked option's action, surfaced directly