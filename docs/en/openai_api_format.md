# OpenAI API Format Mapping Specification

EasyMaaS provides a powerful parameter mapping mechanism that can automatically handle request and response format conversions. This document focuses on describing the specific rules and behaviors of parameter mapping.

## Request Parameter Mapping

When automatic request mapping is enabled (`map_request=True`), EasyMaaS recursively traverses the entire request JSON structure, looking for key-value pairs that match function parameter names. Regardless of which level the parameters are at in the request, as long as the names match, they will be automatically extracted and passed to the function.

For example, if the function is defined as `def my_func(content: str, temperature: float)`, the system will automatically search for fields named "content" and "temperature" in the request, regardless of where they are located in the request body.

## Response Parameter Mapping

Response mapping follows predefined template structures (refer to templates.py), and only fields defined in the template will be automatically mapped. This means that even if the dictionary returned by the function contains additional fields, these fields will not appear in the final response unless they are explicitly included in the template.

Currently supported response templates include standard response and streaming response formats, with specific field definitions as follows:

### Standard Response Template
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

### Streaming Response Template
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

## Return Value Handling

Functions can return the following types of values, and the system will automatically select the appropriate mapping strategy based on the return value type:

1. **String**: Directly used as response content (message.content or delta.content)
2. **Dictionary**: Recursively finds and updates corresponding fields in the response template
3. **Generator**: Used for streaming responses, each generated chunk is converted to the standard streaming response format
