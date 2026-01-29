import os
import mimetypes
from typing import Optional, Union, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from ..client import FalClient, AsyncFalClient

class Storage:
    def __init__(self, client: Union["FalClient", "AsyncFalClient"]):
        self.client = client

    def upload(self, data: Union[str, bytes], content_type: str, file_name: Optional[str] = None) -> str:
        """
        Upload data to Fal CDN and return the URL.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # 1. Initiate upload
        key = file_name or f"{uuid4()}"
        init_data = self.client._request("POST", "/storage/upload/initiate", json_data={
            "content_type": content_type,
            "file_name": key
        })
        
        upload_url = init_data["upload_url"]
        file_url = init_data["file_url"]
        
        # 2. Upload to signed URL (Direct PUT to cloud storage, usually doesn"t need headers from client)
        headers = {"Content-Type": content_type}
        import requests
        resp = requests.put(upload_url, data=data, headers=headers)
        if not resp.ok:
            raise Exception(f"Failed to upload file: {resp.text}")
            
        return file_url

    def upload_file(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
            
        content_type, _ = mimetypes.guess_type(path)
        content_type = content_type or "application/octet-stream"
        
        with open(path, "rb") as f:
            data = f.read()
            
        return self.upload(data, content_type, file_name=os.path.basename(path))

class AsyncStorage(Storage):
    async def upload(self, data: Union[str, bytes], content_type: str, file_name: Optional[str] = None) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        key = file_name or f"{uuid4()}"
        # Async request for initiate
        init_data = await self.client._request("POST", "/storage/upload/initiate", json_data={
            "content_type": content_type,
            "file_name": key
        })
        
        upload_url = init_data["upload_url"]
        file_url = init_data["file_url"]
        
        # Async PUT
        headers = {"Content-Type": content_type}
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.put(upload_url, content=data, headers=headers)
            if resp.status_code >= 400:
                raise Exception(f"Failed to upload file: {resp.text}")
                
        return file_url

    async def upload_file(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
            
        content_type, _ = mimetypes.guess_type(path)
        content_type = content_type or "application/octet-stream"
        
        # Read file async? For now sync read is fine for small files, but strictly should be async.
        # Keeping it simple with blocking read for now as it's typically fast locally.
        with open(path, "rb") as f:
            data = f.read()
            
        return await self.upload(data, content_type, file_name=os.path.basename(path))
