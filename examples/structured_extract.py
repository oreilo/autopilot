"""Run: python examples/structured_extract.py"""
from oreilo_autopilot.extraction import extract_html,export_records
html='<html><title>Sample</title><h1>Products</h1><a href="/pricing">Pricing</a></html>'
data=extract_html(html,'https://example.com')
export_records([data],'artifacts/example.json')
print(data['links'])
