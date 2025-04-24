# EasyMaaS Usage Guide

## Request/Response Mapping Mechanism

The core functionality of EasyMaaS is to map complex multi-layer request structures into flat function parameters, and map flat function return values back into multi-layer responses that conform to the OpenAI API format.

### Request Mapping

1. **Automatic Mapping Mode (`map_request=True`)**
   - The system recursively searches for keys in the request JSON that match function parameter names
   - Example:
     ```python
     @service(model_name="example", map_request=True)
     def example_function(content: str, temperature: float):
         # content and temperature are automatically extracted from the request
         pass
     ```

2. **Manual Mapping Mode (`map_request=False`)**
   - The entire request object is passed as a dictionary to the first function parameter
   - Example:
     ```python
     @service(model_name="example", map_request=False)
     def example_function(request: dict):
         # Manually process request data
         content = request.get("messages")[-1]["content"]
         pass
     ```

### Response Mapping

1. **Automatic Mapping Mode (`map_response=True`)**
   - The system recursively maps function return values to the OpenAI response template
   - Supported data types:
     - String: Directly used as response content
     - Dictionary: Recursively mapped to response template
     - Generator: Used for streaming responses

2. **Manual Mapping Mode (`map_response=False`)**
   - The function needs to return a complete OpenAI format response
   - Example:
     ```python
     @service(model_name="example", map_response=False)
     def example_function(content: str):
         return {
             "id": "chatcmpl-123",
             "object": "chat.completion",
             "created": 1677652288,
             "model": "example",
             "choices": [{
                 "index": 0,
                 "message": {
                     "role": "assistant",
                     "content": content
                 },
                 "finish_reason": "stop"
             }]
         }
     ```

## Usage Examples

### Basic Example

```python
from easymaas import service

@service(model_name="greeting")
def greeting_service(name: str):
    return f"Hello, {name}!"
```

### Streaming Response Example

```python
@service(model_name="stream-example", supports_streaming=True)
async def stream_service(content: str):
    for word in content.split():
        yield {"content": word}
        await asyncio.sleep(0.1)
```

### Complex Parameter Mapping Example

```python
@service(model_name="complex-example", map_request=True)
def complex_service(
    content: str,
    temperature: float,
    max_tokens: int
):
    return {
        "content": f"Processed: {content}",
        "temperature": temperature,
        "max_tokens": max_tokens
    }
```

### Error Handling Example

```python
@service(model_name="error-example")
def error_service(content: str):
    if not content:
        raise ValueError("Content cannot be empty")
    return f"Processed: {content}"
```

## Best Practices

1. Provide clear descriptions for each service
2. Use `map_request` and `map_response` options appropriately
3. Use async functions for streaming responses
4. Add proper error handling
5. Log important events

[View detailed API format mapping specification](openai_api_format.md)