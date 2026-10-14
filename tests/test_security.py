import pytest
from oreilo_autopilot.security import validate_url, require_approval, PolicyError

@pytest.mark.parametrize("url", ["file:///etc/passwd", "http://localhost", "http://127.0.0.1", "http://10.0.0.1", "https://example.com@localhost", "javascript:alert(1)"])
def test_bad_urls(url):
    with pytest.raises(PolicyError): validate_url(url, resolve_dns=False)

def test_allowlist():
    assert validate_url("https://docs.example.com/a", ("example.com",), resolve_dns=False)
    with pytest.raises(PolicyError): validate_url("https://example.com.attacker.org", ("example.com",), resolve_dns=False)

def test_approval():
    with pytest.raises(PolicyError): require_approval("click", approved=False)
    require_approval("click", approved=True)
    require_approval("extract", approved=False)
