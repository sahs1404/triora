from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class Material(BaseModel):
    """A tracked material package — input, before scoring."""
    id: str
    name: str
    activity_id: str
    vendor_id: Optional[str] = None
    lead_time_days: int
    promised_delivery_date: Optional[str] = None
    need_by_date: Optional[str] = None
    vendor_reported_status: Optional[str] = None
    manual_p_delay_override: Optional[float] = None


class PhotoEvidence(BaseModel):
    """A site photo submitted for CV verification (Tier 1)."""
    material_id: str
    activity_id: str
    photo_url: str
    expected_stage: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class MaterialScore(BaseModel):
    """One row of the triage list — output of the CWRS engine."""
    material_id: str
    name: str
    activity_id: str
    activity_name: str
    lead_time_days: int

    p_delay: float
    activity_float_days: int
    urgency: float
    blast_radius: int
    blast_radius_norm: float

    cwrs: float
    rank: int
    status: Literal["critical", "watch", "safe"]
    reason: str