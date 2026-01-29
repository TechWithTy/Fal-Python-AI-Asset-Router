import json
import websockets
from typing import AsyncIterator, Dict, Any, Union, TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from ..client import AsyncFalClient

class RealtimeConnection:
    def __init__(self, ws):
        self._ws = ws

    async def send(self, data: Dict[str, Any]):
        await self._ws.send(json.dumps(data))

    async def recv(self) -> Dict[str, Any]:
        msg = await self._ws.recv()
        return json.loads(msg)

    async def close(self):
        await self._ws.close()

class Realtime:
    def __init__(self, client: "AsyncFalClient"):
        self.client = client

    async def connect(self, application: str, connection_key: str = None) -> AsyncIterator[RealtimeConnection]:
        """
        Connect to a realtime endpoint.
        """
        # Note: Real implementation details depend on Fal's WSS URL pattern.
        # Assuming wss://110602490-fal-ai-flux-realtime.gateway.alpha.fal.ai/ws type pattern
        # or simplified standard: wss://base/app/ws
        # Warning: Detailed dynamic routing logic might be needed here.
        
        # For this refactor, we assume the user provides a proper URL or we rely on a known pattern.
        # Fal often returns a connection token or URL from a REST endpoint first.
        
        # Simplified placeholder for "connect" - requiring a full WSS URL or constructing one.
        # Given "application" like "fal-ai/flux-realtime", we might default to a pattern.
        
        endpoint = f"wss://fal.run/{application}/ws" 
        # Only works if the app is exposed there.
        
        headers = {
            "Authorization": f"Key {self.client.api_key}"
        }
        
        async with websockets.connect(endpoint, extra_headers=headers) as websocket:
            connection = RealtimeConnection(websocket)
            yield connection

