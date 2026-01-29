import time
import asyncio
from typing import Any, Dict, Optional, Iterator, AsyncIterator
from ..models import FalStatus, QueueStatus
from .base import BaseResource

class Applications(BaseResource):
    def submit(self, application: str, arguments: Dict[str, Any], webhook_url: Optional[str] = None) -> QueueStatus:
        """
        Submit a request to an application.
        """
        url = f"/{application}"
        # For queue endpoints, Fal typically accepts the argument JSON directly as body.
        # However, some might wrap likely '{"arguments": ..., "webhook_url": ...}'
        # Based on docs behavior, we'll try sending attributes alongside if webhook_url is present,
        # or just arguments if that's the primary mode.
        # Let's assume standard queue endpoint: POST /<app_owner>/<app_name>
        # Body: { ...arguments, webhook_url: ... }
        
        payload = arguments.copy()
        if webhook_url:
            payload["webhook_url"] = webhook_url

        response_data = self.client._request("POST", url, json_data=payload)
        
        return QueueStatus(
            status=FalStatus.QUEUED,
            request_id=response_data.get("request_id"),
            response_url=response_data.get("response_url"),
            status_url=response_data.get("status_url"),
            cancel_url=response_data.get("cancel_url")
        )

    def status(self, application: str, request_id: str, with_logs: bool = False) -> QueueStatus:
        """
        Check status of a request.
        """
        # Status URL is usually /<app>/requests/<id>/status
        # Or relative status url returned from submit. 
        # But we construct it for consistency.
        url = f"/{application}/requests/{request_id}/status"
        params = {"logs": 1} if with_logs else {}
        data = self.client._request("GET", url, params=params)
        
        status_val = data.get("status", "IN_QUEUE")
        # Map generic strings to Enum if needed
        return QueueStatus(
            status=FalStatus(status_val),
            request_id=request_id,
            response_url=data.get("response_url"),
            logs=data.get("logs"),
            metrics=data.get("metrics"),
            error=data.get("error")
        )

    def result(self, application: str, request_id: str) -> Dict[str, Any]:
        """
        Get result of a completed request.
        """
        url = f"/{application}/requests/{request_id}"
        return self.client._request("GET", url)

    def run(self, application: str, arguments: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
        """
        Run synchronously (submit and poll).
        """
        submission = self.submit(application, arguments)
        request_id = submission.request_id
        
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Request {request_id} timed out")
            
            status_data = self.status(application, request_id)
            if status_data.status == FalStatus.COMPLETED:
                return self.result(application, request_id)
            elif status_data.status == FalStatus.FAILED:
                # If logs available, might want to print them?
                raise Exception(f"Request failed: {status_data.error}")
            
            time.sleep(1) # Poll interval

    def stream(self, application: str, arguments: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """
        Yields events from a streaming endpoint.
        """
        url = f"/{application}/stream" # Pattern assumption
        # Note: requests library valid streaming support requires iter_lines
        
        # We need access to the session to stream
        response = self.client.session.post(
            f"{self.client.BASE_URL}{url}", 
            json=arguments, 
            stream=True
        )
        
        if not response.ok:
             raise Exception(f"Stream failed: {response.text}")

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                     json_str = decoded_line[6:] # Strip "data: "
                     try:
                         yield json.loads(json_str)
                     except json.JSONDecodeError:
                         pass

class AsyncApplications(Applications):
    async def submit(self, application: str, arguments: Dict[str, Any], webhook_url: Optional[str] = None) -> QueueStatus:
        url = f"/{application}"
        payload = arguments.copy()
        if webhook_url:
            payload["webhook_url"] = webhook_url
            
        response_data = await self.client._request("POST", url, json_data=payload)
        
        return QueueStatus(
            status=FalStatus.QUEUED,
            request_id=response_data.get("request_id"),
            response_url=response_data.get("response_url"),
            status_url=response_data.get("status_url"),
            cancel_url=response_data.get("cancel_url")
        )

    async def status(self, application: str, request_id: str, with_logs: bool = False) -> QueueStatus:
         url = f"/{application}/requests/{request_id}/status"
         params = {"logs": 1} if with_logs else {}
         data = await self.client._request("GET", url, params=params)
         
         status_val = data.get("status", "IN_QUEUE")
         return QueueStatus(
            status=FalStatus(status_val),
            request_id=request_id,
            response_url=data.get("response_url"),
            logs=data.get("logs"),
            metrics=data.get("metrics"),
            error=data.get("error")
        )

    async def result(self, application: str, request_id: str) -> Dict[str, Any]:
        url = f"/{application}/requests/{request_id}"
        return await self.client._request("GET", url)

    async def run(self, application: str, arguments: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
        submission = await self.submit(application, arguments)
        request_id = submission.request_id
        
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Request {request_id} timed out")
            
            status_data = await self.status(application, request_id)
            if status_data.status == FalStatus.COMPLETED:
                return await self.result(application, request_id)
            elif status_data.status == FalStatus.FAILED:
                raise Exception(f"Request failed: {status_data.error}")
            
            await asyncio.sleep(1)

    async def stream(self, application: str, arguments: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        url = f"/{application}/stream"
        # Using httpx for async streaming
        import httpx
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", f"{self.client.BASE_URL}{url}", json=arguments, headers=self.client._headers()) as response:
                if response.status_code >= 400:
                     raise Exception(f"Stream failed: {response.status_code}")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        json_str = line[6:]
                        try:
                            yield json.loads(json_str)
                        except json.JSONDecodeError:
                            pass
