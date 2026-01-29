# Fal AI SDK Reference

This SDK provides a Pythonic interface for interacting with Fal AI's models, structured similarly to the Gamma SDK.

## Installation

Ensure you have the required dependencies:

```bash
pip install -r requirements.txt
```

## Authentication

Set your API key in the environment variable `FAL_KEY` or pass it to the client.

```python
import os
os.environ["FAL_KEY"] = "your-api-key"
```

## Client

### `FalClient`

The main entry point for the SDK.

```python
from fal_ai import FalClient

client = FalClient()
```

---

## Resources

### Applications

Interact with any Fal AI application (model).

#### `client.applications.run(application, arguments, timeout=120)`

Run an application synchronously (submits, polls, and returns result).

**Parameters:**
- `application` (str): The application ID (e.g., `"fal-ai/flux/dev"`).
- `arguments` (dict): Dictionary of arguments for the model.
- `timeout` (int): Timeout in seconds (default 120).

**Returns:**
- `dict`: The result of the model execution.

**Example:**

```python
result = client.applications.run(
    "fal-ai/flux/dev",
    {
        "prompt": "A cinematic shot of a futuristic city",
        "image_size": "landscape_4_3"
    }
)
print(result)
```

#### `client.applications.submit(application, arguments, webhook_url=None)`

Submit a request to the queue asynchronously.

**Returns:**
- `QueueStatus`: Object containing `request_id`, `status`, etc.

#### `client.applications.status(application, request_id, with_logs=False)`

Check the status of a request.

#### `client.applications.result(application, request_id)`

Retrieve the result of a completed request.

---

## Models

### `FalStatus`

Enum representing the status of a request.
- `QUEUED`
- `IN_PROGRESS`
- `COMPLETED`
- `FAILED`

### `QueueStatus`

Pydantic model for queue status response.
- `status`: `FalStatus`
- `request_id`: `str`
- `response_url`: `str`
- `logs`: `List[Dict]` (optional)
- `metrics`: `Dict` (optional)
- `error`: `str` (optional)
