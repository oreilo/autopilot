from urllib.parse import urlparse
import ipaddress
import socket

class PolicyError(RuntimeError):
    pass

SENSITIVE = {"click", "fill", "press", "select"}
BLOCKED_SCHEMES = {"file", "javascript", "data", "ftp", "chrome", "about"}

def validate_url(url: str, allowed_domains: tuple[str, ...] = (), *, resolve_dns: bool = True) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise PolicyError("Only public http(s) URLs without credentials are allowed")
    hostname = parsed.hostname.lower().rstrip(".")
    if hostname == "localhost" or hostname.endswith(".localhost") or hostname.endswith(".local"):
        raise PolicyError("Local addresses are not permitted")
    if allowed_domains and not any(hostname == d.lower().lstrip(".") or hostname.endswith("." + d.lower().lstrip(".")) for d in allowed_domains):
        raise PolicyError(f"Domain not allowlisted: {hostname}")
    try:
        ip = ipaddress.ip_address(hostname)
        if not ip.is_global:
            raise PolicyError("Non-public IP addresses are prohibited")
    except ValueError:
        pass
    if resolve_dns:
        try:
            addresses = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        except socket.gaierror as exc:
            raise PolicyError(f"DNS lookup failed: {hostname}") from exc
        for info in addresses:
            if not ipaddress.ip_address(info[4][0]).is_global:
                raise PolicyError("DNS resolved to a non-public IP")
    return url

def require_approval(kind: str, *, approved: bool) -> None:
    if kind in SENSITIVE and not approved:
        raise PolicyError(f"Action '{kind}' requires explicit approval")
