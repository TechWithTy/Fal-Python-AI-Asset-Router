# Fal AI Python Asset Router

A robust, Pythonic SDK for interacting with [Fal AI's](https://fal.ai) generative models and infrastructure. This library is designed with a modular structure (mimicking the Gamma SDK patterns) to provide a clean and intuitive developer experience.

## Features

- **Sync & Async Support**: Full support for both synchronous and asynchronous (`asyncio`) workflows.
- **Application Execution**: Easily run, submit, and poll Fal AI applications.
- **Streaming**: Native support for consuming streaming responses from models.
- **File Storage**: Built-in helpers for uploading files and images to Fal's CDN.
- **Realtime**: WebSocket support for low-latency realtime applications.
- **Type Safety**: Pydantic models for requests, responses, and statuses.

## Installation

```bash
pip install -r requirements.txt
```

*(Note: Package publication pending)*

## Configuration

Set your API key in the environment:

```bash
export FAL_KEY="your-api-key-here"
```

Or pass it directly to the client:

```python
from fal_ai import FalClient

client = FalClient(api_key="your-api-key")
```

## Usage

### 1. Running a Model (Synchronous)

Run a model and wait for the result in one line.

```python
from fal_ai import FalClient

client = FalClient()

result = client.applications.run(
    "fal-ai/flux/dev",
    {
        "prompt": "A cyberpunk street scene at night, neon rain",
        "image_size": "landscape_16_9"
    }
)

print(result)
```

### 2. Async Workflow

Ideal for high-throughput web servers (FastAPI, etc.).

```python
import asyncio
from fal_ai import AsyncFalClient

async def main():
    client = AsyncFalClient()
    
    result = await client.applications.run(
        "fal-ai/flux/dev",
        {"prompt": "A cute robot holding a flower"}
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Uploading Files

Upload images or other assets before sending them to a model.

```python
# Sync
url = client.storage.upload_file("path/to/image.jpg")

# Async
url = await async_client.storage.upload_file("path/to/audio.mp3")

# Use the URL in your model request
client.applications.run("fal-ai/img-to-img", {
    "image_url": url,
    "prompt": "make it anime style"
})
```

### 4. Streaming Responses

Consume partial results as they generate.

```python
for event in client.applications.stream("fal-ai/fast-llm", {"prompt": "Hello!"}):
    print(event)
```

## Project Structure

- `client.py`: Main entry point (`FalClient`, `AsyncFalClient`).
- `endpoints/`: Resource modules (`applications`, `storage`, `realtime`).
- `models.py`: Pydantic data models for type validation.
- `errors.py`: Unified error handling hierarchy.

## License

MIT
