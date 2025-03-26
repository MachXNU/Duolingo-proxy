from mitmproxy import http
import json
import re

TARGET_HOST = "duolingo.com"

def request(flow: http.HTTPFlow) -> None:
    """Intercept requests to the target host."""
    if TARGET_HOST in flow.request.pretty_url:
        match = re.search(r"/\d{4}-\d{2}-\d{2}/users/\d+\?", flow.request.path)
        if match and "fields=" in flow.request.query:
            print(f"Intercepted request: {flow.request.url}")

def response(flow: http.HTTPFlow) -> None:
    """Modify responses containing the 'health' object."""
    if TARGET_HOST in flow.request.pretty_url:
        try:
            data = json.loads(flow.response.text)
            if "health" in data and isinstance(data["health"], dict):
                print(f"Original health data: {data['health']}")

                # Modify health fields
                data["health"]["healthEnabled"] = False
                data["health"]["unlimitedHeartsAvailable"] = True
                data["health"]["useHealth"] = False
                
                flow.response.text = json.dumps(data, indent=2)  # Update response
                
                print(f"Modified health data: {data['health']}")
        except Exception as e:
            print(f"Error modifying response: {e}")
