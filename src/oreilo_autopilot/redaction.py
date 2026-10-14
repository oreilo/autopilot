"""Redact secrets before persisting logs and browser observations."""
import re

PATTERNS=[
 (re.compile(r'(?i)(bearer\s+)[a-z0-9._~+/-]{12,}'),r'\1[REDACTED]'),
 (re.compile(r'(?i)(api[_-]?key\s*[=:]\s*)[a-z0-9_-]{8,}'),r'\1[REDACTED]'),
 (re.compile(r'(?i)(password\s*[=:]\s*)\S+'),r'\1[REDACTED]'),
]
def redact(text):
    result=str(text)
    for pattern,replacement in PATTERNS: result=pattern.sub(replacement,result)
    return result
