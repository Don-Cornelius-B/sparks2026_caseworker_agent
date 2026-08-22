import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

class ResidentHistoryClient:
    """
    HTTP client for the Calder County Resident History API.
    Interacts with history_service.py running on port 8083.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8083"):
        self.base_url = base_url.rstrip("/")

    def get_resident(self, resident_ref: str) -> Dict[str, Any]:
        """
        Retrieves the complete history profile for a single resident.
        Returns a structured error metadata.
        """
        url = f"{self.base_url}/residents/{resident_ref}"
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "CaseworkerAssistant/1.0", "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"error": "not_found", "resident_ref": resident_ref, "status_code": 404}
            return {"error": "http_error", "status_code": e.code, "resident_ref": resident_ref}
        except urllib.error.URLError as e:
            return {"error": "service_unavailable", "reason": str(e.reason), "resident_ref": resident_ref}
        except Exception as e:
            return {"error": "unexpected_exception", "detail": str(e), "resident_ref": resident_ref}

    def check_health(self) -> Dict[str, Any]:
        """Verifies if the resident history service is alive and healthy."""
        url = f"{self.base_url}/health"
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}