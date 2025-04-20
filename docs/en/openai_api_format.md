# OpenAI API Format Mapping

## Overview

EasyMaaS automatically maps Python functions to OpenAI-compatible API services. This document explains how the mapping works and how to customize it.

## Basic Mapping

### Function Parameters

EasyMaaS automatically maps OpenAI API request parameters to Python function parameters. For example:

```python
@service(model_name="my-model")
def my_function(content: str, temperature: float = 0.7):
    return f"Processed: {content} with temperature {temperature}"
```

This function will accept OpenAI API requests with the following parameters:
- `content`: The input text
- `temperature`: The temperature parameter (optional, defaults to 0.7)

### Return Values

EasyMaaS automatically converts Python function return values to OpenAI API response format. For example:

```python
@service(model_name="my-model")
def my_function(content: str):
    return {
        "role": "assistant",
        "content": f"Processed: {content}"
    }
```

This will be converted to a standard OpenAI API response.

## Advanced Mapping

### Streaming Responses

To support streaming responses, use the `yield` keyword:

```python
@service(model_name="my-model")
def my_function(content: str):
    for i in range(5):
        yield f"Chunk {i}: {content}\n"
```

### Error Handling

EasyMaaS automatically handles errors and returns them in OpenAI API format:

```python
@service(model_name="my-model")
def my_function(content: str):
    if not content:
        raise ValueError("Content cannot be empty")
    return f"Processed: {content}"
```

### Custom Response Format

You can customize the response format by returning a dictionary with specific keys:

```python
@service(model_name="my-model")
def my_function(content: str):
    return {
        "role": "assistant",
        "content": f"Processed: {content}",
        "finish_reason": "stop"
    }
```

## Configuration Options

You can customize the mapping behavior using the `@service` decorator parameters:

```python
@service(
    model_name="my-model",
    description="A custom service",
    max_tokens=1000,
    temperature_range=(0.0, 2.0)
)
def my_function(content: str):
    return f"Processed: {content}"
```

Available parameters:
- `model_name`: The name of the model
- `description`: A description of the service
- `max_tokens`: Maximum number of tokens in the response
- `temperature_range`: Valid range for the temperature parameter

## Examples

### Basic Example

```python
@service(model_name="echo")
def echo_service(content: str):
    return content
```

### Advanced Example

```python
@service(
    model_name="advanced",
    description="An advanced service with custom parameters",
    max_tokens=2000,
    temperature_range=(0.0, 1.0)
)
def advanced_service(
    content: str,
    temperature: float = 0.7,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0
):
    # Process the content with the given parameters
    result = f"Processed: {content}\n"
    result += f"Temperature: {temperature}\n"
    result += f"Top P: {top_p}\n"
    result += f"Frequency Penalty: {frequency_penalty}\n"
    result += f"Presence Penalty: {presence_penalty}"
    
    return {
        "role": "assistant",
        "content": result,
        "finish_reason": "stop"
    }
``` 