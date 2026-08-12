from pydantic import BaseModel


class Activity(BaseModel):
    """A construction schedule activity (a node in the CPM graph)."""
    id: str                          # e.g. "A09"
    name: str                        # e.g. "Switchgear Installation"
    duration_days: int
    predecessors: list[str] = []     # activity ids that must finish first