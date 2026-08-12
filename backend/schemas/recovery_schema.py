from pydantic import BaseModel
from typing import Literal


class RecoveryOption(BaseModel):
    action: Literal[
        "expedite_shipment",
        "partial_shipment",
        "alternate_supplier",
        "resequence_activity",
        "absorb_delay",
    ]
    description: str
    estimated_cost_inr: float
    estimated_days_recovered: float
    recommended: bool = False


class RecoveryRecommendation(BaseModel):
    material_id: str
    options: list[RecoveryOption]
    best_option_index: int
    reasoning: str