import os
import requests
import httpx
from typing import Optional, Any, Dict, Union
from .endpoints import Applications, AsyncApplications, Storage, AsyncStorage, Realtime
from .errors import raise_for_status, FalError

class FalClient:
    BASE_URL = "https://queue.fal.run"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FAL_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in FAL_KEY env var")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Initialize endpoints
        self.applications = Applications(self)
        self.storage = Storage(self)

    def _request(self, method: str, endpoint: str, json_data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        url = f"{self.BASE_URL}{endpoint}"
        
        response = self.session.request(method, url, json=json_data, params=params)
        
        if not response.ok:
            try:
                error_body = response.json()
                error_msg = error_body.get('message', error_body.get('detail', response.text))
            except:
                error_msg = response.text
            raise_for_status(response.status_code, error_msg, response)
        
        return response.json()

class AsyncFalClient:
    BASE_URL = "https://queue.fal.run"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FAL_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in FAL_KEY env var")
        
        # Endpoints
        self.applications = AsyncApplications(self)
        self.storage = AsyncStorage(self)
        self.realtime = Realtime(self)

    def _headers(self):
        return {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _request(self, method: str, endpoint: str, json_data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        url = f"{self.BASE_URL}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, json=json_data, params=params, headers=self._headers())
            
            if response.status_code >= 400:
                 try:
                    error_body = response.json()
                    error_msg = error_body.get('message', error_body.get('detail', response.text))
                 except:
                    error_msg = response.text
                 raise_for_status(response.status_code, error_msg, response)
            
            return response.json()
