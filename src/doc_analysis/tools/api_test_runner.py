from crewai.tools import tool
import requests
import json
import os
from urllib.parse import urljoin
from dotenv import load_dotenv
import time

load_dotenv()

@tool("Advanced API Testing Tool")
def test_apis_from_spec(api_file_path: str = "api_specs/carrier.json", environment: str = "staging") -> str:
    """Load carrier JSON from api_specs folder, fetch OAuth2 token, inject headers, and test endpoints for a given environment (staging, qa, production, development)."""
    if not os.path.exists(api_file_path):
        return f"❌ API spec not found at {api_file_path}"

    with open(api_file_path, "r") as f:
        spec = json.load(f)

    # Map environment to server description
    env_map = {
        "production": "production",
        "staging": "staging",
        "qa": "qa",
        "development": "development"
    }
    env_key = environment.lower()
    env_str = env_map.get(env_key)
    if not env_str:
        return f"❌ Invalid environment '{environment}'. Choose from: {', '.join(env_map.keys())}"
    servers = spec.get("servers", [])
    base_url = None
    for server in servers:
        desc = server.get("description", "").lower()
        if env_str in desc:
            base_url = server.get("url")
            break
    if not base_url:
        available = [s.get("description", s.get("url", "")) for s in servers]
        return f"❌ No server found for environment '{environment}'. Available: {available}"
    # Ensure base_url has scheme
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        base_url = "https://" + base_url
    # Ensure base_url ends with a slash for urljoin
    if not base_url.endswith('/'):
        base_url += '/'

    paths = spec.get("paths", {})
    security_schemes = spec.get("components", {}).get("securitySchemes", {})
    global_security = spec.get("security", [{}])[0]

    cache_path = os.getenv("TOKEN_CACHE_PATH", ".token_cache.json")
    
    def load_token_cache():
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def save_token_cache(token, expires_in, obtained_at, env_prefix, token_url):
        cache = {
            "token": token,
            "expires_in": expires_in,
            "obtained_at": obtained_at,
            "env_prefix": env_prefix,
            "token_url": token_url
        }
        with open(cache_path, "w") as f:
            json.dump(cache, f)

    def is_token_valid(cache, env_prefix, token_url):
        if not cache:
            return False
        if cache.get("env_prefix") != env_prefix or cache.get("token_url") != token_url:
            return False
        token = cache.get("token")
        expires_in = cache.get("expires_in")
        obtained_at = cache.get("obtained_at")
        if not token or not expires_in or not obtained_at:
            return False
        now = int(time.time())
        # Add a small buffer (e.g., 30 seconds) to avoid using an expiring token
        return now < obtained_at + expires_in - 30

    headers = {}
    token = None

    # --- Auth: OAuth2 (password flow) ---
    if "OAuth2" in security_schemes:
        oauth2 = security_schemes["OAuth2"]
        flows = oauth2.get("flows", {})
        password_flow = flows.get("password")
        if not password_flow:
            return "❌ OAuth2 'password' flow not found in securitySchemes"
        token_url = password_flow.get("tokenUrl")
        if not token_url:
            return "❌ OAuth2 'tokenUrl' not found in securitySchemes"
        full_token_url = urljoin(base_url, token_url.lstrip('/'))
        env_prefix = env_key.upper()
        username = os.getenv(f"{env_prefix}_API_USERNAME")
        password = os.getenv(f"{env_prefix}_API_PASSWORD")
        client_id = os.getenv(f"{env_prefix}_API_CLIENT_ID")
        client_secret = os.getenv(f"{env_prefix}_API_CLIENT_SECRET")
        if not all([username, password, client_id, client_secret]):
            return f"❌ Missing one or more of {env_prefix}_API_USERNAME, {env_prefix}_API_PASSWORD, {env_prefix}_API_CLIENT_ID, {env_prefix}_API_CLIENT_SECRET in environment"
        cache = load_token_cache()
        if is_token_valid(cache, env_prefix, full_token_url):
            token = cache["token"]
        else:
            try:
                response = requests.post(full_token_url, data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                    "client_id": client_id,
                    "client_secret": client_secret
                })
                resp_json = response.json()
                token = resp_json.get("access_token")
                expires_in = resp_json.get("expires_in", 3600)  # Default 1 hour if not provided
                if not token:
                    return f"❌ Failed to retrieve token: {response.text}"
                obtained_at = int(time.time())
                save_token_cache(token, expires_in, obtained_at, env_prefix, full_token_url)
            except requests.exceptions.ConnectionError as ce:
                return f"❌ Failed to connect to token endpoint: {full_token_url}. Error: {ce} (Check DNS and server URL)"
            except Exception as e:
                return f"❌ Failed to retrieve token: {str(e)}"
        headers["Authorization"] = f"Bearer {token}"

    # --- Auth: API Key ---
    if "AwsApiKey" in security_schemes:
        api_key_name = security_schemes["AwsApiKey"]["name"]
        api_key = os.getenv(f"{env_prefix}_API_KEY")
        if not api_key:
            return f"❌ Missing {env_prefix}_API_KEY in environment"
        headers[api_key_name] = api_key

    results = []

    for endpoint, methods in paths.items():
        for method, details in methods.items():
            method = method.upper()
            full_url = urljoin(base_url, endpoint.lstrip('/'))
            summary = details.get("summary", "")
            response_data = ""
            status = ""

            # Debug: print headers
            #print(f"\nRequesting {method} {full_url}")
            #print(f"Headers: {headers}")

            try:
                if method == "GET":
                    res = requests.get(full_url, headers=headers, params={"sample": "value"})
                elif method in ["POST", "PUT"]:
                    body = {"sample": "data"}  # Placeholder
                    res = requests.request(method, full_url, headers=headers, json=body)
                elif method == "DELETE":
                    res = requests.delete(full_url, headers=headers)
                else:
                    continue

                status = res.status_code
                response_data = res.text[:300]

            except Exception as e:
                status = "Error"
                response_data = str(e)

            results.append({
                "method": method,
                "url": full_url,
                "summary": summary,
                "status": status,
                "response": response_data
            })

    output = []
    for r in results:
        output.append(f"[{r['method']}] {r['url']} - Status: {r['status']}")
        output.append(f"Summary: {r['summary']}")
        output.append(f"Response: {r['response']}")
        output.append("-" * 50)

    return "\n".join(output)
