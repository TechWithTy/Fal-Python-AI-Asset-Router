from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import FalClient

class BaseResource:
    def __init__(self, client: "FalClient"):
        self.client = client
