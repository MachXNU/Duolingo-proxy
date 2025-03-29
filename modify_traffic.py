from mitmproxy import http
import json
import re

TARGET_HOSTS = ["duolingo.com", "ios-api-cf.duolingo.com"]


def request(flow: http.HTTPFlow) -> None:
    """Intercept requests to the target hosts."""
    if any(host in flow.request.pretty_url for host in TARGET_HOSTS):
        web_match = re.search(r"/\d{4}-\d{2}-\d{2}/users/\d+\?", flow.request.path)
        batch_match = re.search(r"/\d{4}-\d{2}-\d{2}/batch", flow.request.path)
        if web_match or batch_match:
            print(f"Intercepted request: {flow.request.url}")


def modify_health_data(data: dict) -> bool:
    """Modify the health-related fields if present in the JSON."""
    if "health" in data and isinstance(data["health"], dict):
        print(f"Original health data: {data['health']}")
        
        # Modify health fields
        data["health"]["unlimitedHeartsAvailable"] = True
        # data["health"]["healthEnabled"] = False  # Not mandatory
        # data["health"]["useHealth"] = False      # Not mandatory
        
        print(f"Modified health data: {data['health']}")
        return True
    return False


def response(flow: http.HTTPFlow) -> None:
    """Modify responses containing the 'health' object or nested JSON in 'responses' -> 'body'."""
    if any(host in flow.request.pretty_url for host in TARGET_HOSTS):
        try:
            data = json.loads(flow.response.text)
            modified = False

            # Modify standard health data
            if modify_health_data(data):
                modified = True
            
            # Handle batch responses containing nested JSON in 'body'
            if "responses" in data and isinstance(data["responses"], list):
                for response_entry in data["responses"]:
                    if "body" in response_entry and isinstance(response_entry["body"], str):
                        try:
                            nested_body = json.loads(response_entry["body"])
                            if modify_health_data(nested_body):
                                response_entry["body"] = json.dumps(nested_body)
                                modified = True
                        except json.JSONDecodeError:
                            pass  # Ignore non-JSON bodies
            
            if modified:
                flow.response.text = json.dumps(data, indent=2)
        except Exception as e:
            print(f"Error modifying response: {e}")
