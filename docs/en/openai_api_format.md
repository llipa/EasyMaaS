# OpenAI API Format Mapping Specification

EasyMaaS supports mapping Python functions to OpenAI-compatible API services. This document details the supported function types and parameter mapping rules.

## Basic Usage

Use the `@service` decorator to convert functions into services:

```python
from easymaas import service

@service(model_name="my-model", description="My custom service")
def my_function(content: str):
    return f"Processed: {content}"
```

## Parameter Mapping

### Automatic Parameter Mapping

EasyMaaS employs a recursive JSON mapping mechanism to automatically map parameters from OpenAI API requests to function parameters:

1. The `content` parameter automatically maps to the last user message content
2. The `request` parameter receives the complete request object
3. Other parameters attempt to retrieve corresponding attributes from the request object

### Parameter Validation
EasyMaaS performs dynamic validation of function parameters during service runtime:

1. Unmapped parameters are logged with warnings during execution
2. The system provides detailed error messages including available parameter lists

Example for a function with unmappable parameters:

```python
@service(model_name="invalid-param-model")
def invalid_param_function(content: str, invalid_param: str):
    return f"Content: {content}, Invalid: {invalid_param}"
```

The system generates warnings like:

```plaintext
================================================================================
⚠️ Warning: The following parameters in function 'invalid_param_function' cannot be mapped to requests: invalid_param
================================================================================
```

### Supported Parameter Types

Functions can accept these parameters:

```python
@service(model_name="my-model")
def my_function(
    content: str,                    # User message content
    request: ChatCompletionRequest,  # Complete request object
    temperature: float,              # Temperature parameter
    top_p: float,                    # Top_p parameter
    n: int,                          # Generation count
    stream: bool,                    # Streaming flag
    stop: Union[str, List[str]],     # Stop sequences
    max_tokens: int,                 # Maximum tokens
    presence_penalty: float,         # Presence penalty
    frequency_penalty: float,        # Frequency penalty
    user: str                        # User identifier
):
    # Function implementation
    pass
```

## Response Handling

### Basic Return Values

Functions can return these value types:

1. String: Directly used as response content
2. Dictionary: Supports the following fields
   ```python
   {
       "content": "Response content",
       "role": "assistant",
       "finish_reason": "stop",
       "prompt_tokens": 10,
       "completion_tokens": 20,
       "total_tokens": 30
   }
   ```

EasyMaaS processes return values using recursive JSON mapping, converting function return dictionaries to standard OpenAI response formats. This allows developers flexible control over response aspects without constructing complete response objects.

### Response Validation

EasyMaaS validates function return values against expected formats:

1. Return values should be strings or dictionaries containing response keys
2. The system issues warnings for malformed responses

Example for invalid return format:

```python
@service(model_name="invalid-return-model")
def invalid_return_function(content: str):
    return {"invalid_key": "value"}  # Missing content key
```

System warning:

```plaintext
================================================================================
⚠️ Warning: Function 'invalid_return_function' cannot map return value 'invalid_key' to response
================================================================================
```

### Streaming Responses

For streaming support, functions should return iterable objects:

```python
@service(model_name="stream-model")
async def stream_function(content: str):
    for chunk in generate_chunks(content):
        yield chunk
```

## Async Support

Both synchronous and asynchronous functions are supported:

```python
# Synchronous function
@service(model_name="sync-model")
def sync_function(content: str):
    return process_content(content)

# Asynchronous function
@service(model_name="async-model")
async def async_function(content: str):
    return await process_content_async(content)
```

## Examples

### Simple Text Processing

```python
@service(model_name="text-processor")
def process_text(content: str):
    return f"Processed: {content.upper()}"
```

### Multiple Choice Generation

```python
@service(model_name="multi-choice")
def generate_choices(content: str, n: int = 3):
    return [
        {"content": f"Option {i}: {content}", "role": "assistant"}
        for i in range(n)
    ]
```

### Streaming Response

```python
@service(model_name="stream-generator")
async def stream_generator(content: str):
    words = content.split()
    for word in words:
        yield {"content": word}
        await asyncio.sleep(0.1)
```

## Important Notes

1. Functions must specify `model_name`
2. Providing function descriptions is recommended
3. Streaming responses require async functions
4. Return values are automatically converted to OpenAI-compatible formats