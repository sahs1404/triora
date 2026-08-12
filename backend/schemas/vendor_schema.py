from pydantic import BaseModel


class Vendor(BaseModel):
    """A supplier — used for the reliability memory layer (Tier 4)."""
    id: str
    name: str
    historical_delay_rate: float = 0.15
    jobs_completed: int = 0
    jobs_delayed: int = 0