import pytest
from oreilo_autopilot.models import Action

def test_action_parsing():
    assert Action.model_validate({"kind":"navigate", "url":"https://example.com"}).kind == "navigate"

def test_action_invalid():
    with pytest.raises(Exception): Action.model_validate({"kind":"unknown"})
