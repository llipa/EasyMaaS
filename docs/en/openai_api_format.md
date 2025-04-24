# OpenAI API Format Mapping Specification

EasyMaaS supports mapping Python functions to OpenAI-compatible API services. This document details the supported function types and parameter mapping rules.

## API Endpoints

EasyMaaS provides the following API endpoints:

1. `POST /v1/chat/completions` - Handle chat completion requests
   - Request format: OpenAI-compatible chat completion request
   - Response format: Standard or streaming response based on service configuration

2. `GET /v1/models` - List all available models
   - Response format: List of all registered models

## Service Registration

Use the `@service` decorator to convert functions into services:

```python
from easymaas import service

@service(model_name="my-model", description="My custom service")
def my_function(content: str):
    return f"Processed: {content}"
```

## Service Configuration Options

The `@service` decorator supports the following configuration options:

```python
@service(
    model_name="my-model",          # Model name
    description="My service",       # Service description
    map_request=True,               # Automatically map request parameters
    map_response=True,              # Automatically map response format
    supports_streaming=True         # Support streaming responses
)
```

## Request Handling

### Parameter Mapping

EasyMaaS uses a recursive JSON mapping mechanism to automatically map parameters from OpenAI API requests to function parameters:

1. If `map_request=True`, the system recursively searches for keys in the request JSON that match function parameter names
2. If `map_request=False`, the request data is passed as a dictionary to the first function parameter

### Parameter Validation

The system validates function parameters at runtime:
1. Logs warnings for unmapped parameters
2. Raises ValueError if the function has no parameters

## Response Handling

### Response Templates

EasyMaaS uses the following response templates:

1. Standard response template:
```python
{
    "id": "uuid",
    "object": "chat.completion",
    "created": timestamp,
    "model": "model_name",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "response_content"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }
}
```

2. Streaming response template:
```python
{
    "id": "uuid",
    "object": "chat.completion.chunk",
    "created": timestamp,
    "model": "model_name",
    "choices": [
        {
            "index": 0,
            "delta": {
                "role": "assistant",
                "content": "chunk_content"
            },
            "finish_reason": None
        }
    ]
}
```

### Return Value Handling

Functions can return the following value types:
1. String: Directly used as response content
2. Dictionary: Recursively mapped to response template
3. Generator: Used for streaming responses

## Error Handling

EasyMaaS provides comprehensive error handling:
1. Model not found: Returns 404 error
2. Parameter mapping failure: Logs warnings
3. Function execution error: Logs error and raises exception
4. Streaming response error: Sends error message and terminates stream

## Logging

The system uses the standard logging module to record:
1. Service registration information
2. Parameter mapping warnings
3. Function execution errors
4. Streaming response status

Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`