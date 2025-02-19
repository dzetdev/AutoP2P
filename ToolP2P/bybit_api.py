import json
import time
import hmac
import hashlib
import requests
from config import API_KEY, API_SECRET, BASE_URL


def get_server_time():
    """Get timestamp from Bybit with error handling"""
    url = f"{BASE_URL}/v5/time"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error getting server time: {response.status_code}, {response.text}")
        return int(time.time() * 1000)

    try:
        return int(response.json().get("time", int(time.time() * 1000)))
    except requests.exceptions.JSONDecodeError:
        print("Error: API did not return valid JSON:", response.text)
        return int(time.time() * 1000)


def create_signature(timestamp: str, recv_window: str, body: dict):
    """Create signature for Bybit API request"""
    # ✅ Chuyển body thành JSON string (sort key)
    sorted_body = json.dumps(body, sort_keys=True)

    # ✅ Chuỗi để ký phải đúng thứ tự
    param_str = f"{timestamp}{API_KEY}{recv_window}{sorted_body}"

    # ✅ Tạo chữ ký HMAC SHA256
    return hmac.new(
        API_SECRET.encode(),
        param_str.encode(),
        hashlib.sha256
    ).hexdigest()


def create_headers(body: dict = None):
    """Create headers with proper signature"""
    timestamp = str(get_server_time())
    recv_window = "10000"

    if body is None:
        body = {}

    # ✅ Đảm bảo JSON có thứ tự keys đúng
    sorted_body = json.dumps(body, sort_keys=True)
    signature = create_signature(timestamp, recv_window, json.loads(sorted_body))

    return {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature,
        "Content-Type": "application/json"
    }


def send_request(method: str, endpoint: str, body: dict = None):
    """Send API request with proper error handling"""
    url = BASE_URL + endpoint

    if body is None:
        body = {}

    headers = create_headers(body)

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=body)
        elif method.upper() == "POST":
            # ✅ Gửi body với JSON string sắp xếp đúng
            response = requests.post(url, headers=headers, data=json.dumps(body, sort_keys=True))
        else:
            raise ValueError("Method only supports GET or POST")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                return e.response.json()
            except:
                return {"error": str(e), "response": e.response.text}
        return {"error": str(e)}

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return {"error": "API response is not valid JSON", "response": response.text}
