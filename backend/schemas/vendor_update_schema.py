from pydantic import BaseModel


class JobOutcomeUpdate(BaseModel):
    """Record that a vendor's job either was or wasn't delayed."""
    was_delayed: bool


class ManualRateUpdate(BaseModel):
    """Directly set a vendor's historical_delay_rate."""
    new_rate: float