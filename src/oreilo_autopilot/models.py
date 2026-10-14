from typing import Literal
from pydantic import BaseModel, Field

class Action(BaseModel):
    kind: Literal["navigate", "click", "fill", "press", "select", "scroll", "extract", "screenshot", "finish", "wait", "back", "tab_new", "tab_switch", "extract_structured"]
    url: str | None = None
    selector: str | None = None
    value: str | None = None
    reason: str = ""
    answer: str | None = None

class Decision(BaseModel):
    action: Action

class Observation(BaseModel):
    url: str
    title: str
    text: str
    elements: list[dict]
    step: int

class StepRecord(BaseModel):
    step: int
    action: Action
    url: str
    outcome: str
    detail: str = ""
