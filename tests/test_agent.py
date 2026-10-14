import pytest
from oreilo_autopilot.agent import AutoPilot, AgentConfig
from oreilo_autopilot.models import Action

def test_config_requires_domain():
    with pytest.raises(ValueError): AutoPilot(None, AgentConfig(()))

def test_step_limit():
    with pytest.raises(ValueError): AutoPilot(None, AgentConfig(("example.com",), max_steps=0))

def test_action_schema():
    assert Action(kind="finish", answer="ok").answer == "ok"
    with pytest.raises(Exception): Action(kind="run_shell")
