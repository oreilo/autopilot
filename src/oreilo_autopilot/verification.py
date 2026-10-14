"""Explicit verification checks rather than trusting model completion blindly."""
from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass
class Verification:
    passed: bool
    checks: list[dict]

async def verify_page(page,expected_url_contains=None,expected_text=None,expected_selector=None):
    checks=[]
    if expected_url_contains:
        checks.append({'check':'url','passed':expected_url_contains in page.url})
    if expected_text:
        text=await page.locator('body').inner_text(timeout=10000)
        checks.append({'check':'text','passed':expected_text.lower() in text.lower()})
    if expected_selector:
        checks.append({'check':'selector','passed':await page.locator(expected_selector).count()>0})
    return Verification(passed=bool(checks) and all(c['passed'] for c in checks),checks=checks)
