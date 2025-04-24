# EasyMaaS Usage Guide

This guide will help you quickly master the core features and usage methods of EasyMaaS, allowing you to easily convert Python functions into OpenAI-compatible API services through detailed examples and explanations.

## Core Concepts

The core of EasyMaaS is the `@service` decorator, which can convert ordinary Python functions into services that conform to the OpenAI API format. The decorator provides multiple configuration options that allow you to customize the behavior of the service according to your needs.

```python
@service(
    model_name="my-model",          # Model name (required)
    description="My service",       # Service description (optional)
    map_request=True,               # Whether to automatically map request parameters (optional, default False)
    map_response=True,              # Whether to automatically map response format (optional, default False)
    supports_streaming=True         # Whether to support streaming responses (optional, default False)
)
def my_function(param1, param2):
    # Function implementation
    pass
```

## Request/Response Mapping Mechanism

The most powerful feature of EasyMaaS is its intelligent mapping mechanism, which can automatically handle complex request parameter extraction and response format conversion, allowing you to focus on business logic implementation.

### Request Mapping

Request mapping determines how to convert OpenAI API format requests into function parameters. EasyMaaS provides two mapping modes:

#### 1. Automatic Mapping Mode (`map_request=True`)

In automatic mapping mode, EasyMaaS recursively searches for keys in the request JSON that match function parameter names, regardless of which level these keys are at in the JSON. This allows you to directly use function parameters to receive specific fields in the request, without having to manually parse complex JSON structures.

```python
@service(model_name="auto-mapping-example", map_request=True)
def example_function(content: str, temperature: float, max_tokens: int = 100):
    # Parameters are automatically extracted from the request:
    # - content is extracted from request.messages[-1].content
    # - temperature is extracted from request.temperature
    # - max_tokens is extracted from request.max_tokens, or uses default value 100 if not present
    return f"Processed content: {content}, Temperature: {temperature}, Max tokens: {max_tokens}"
```

**How it works**:
- The system recursively traverses the entire request JSON, looking for keys that match function parameter names
- If a matching key is found, its value is passed to the corresponding function parameter
- If no matching key is found, the parameter will be set to `None` (unless it has a default value)
- The system logs unmapped parameters and issues warnings

#### 2. Manual Mapping Mode (`map_request=False`, default mode)

In manual mapping mode, the entire request object is passed as a dictionary to the first parameter of the function. This mode is suitable for scenarios where you need complete control over the request processing logic.

```python
@service(model_name="manual-mapping-example")
def example_function(request: dict):
    # Manually extract required data from the request
    messages = request.get("messages", [])
    content = messages[-1].get("content", "") if messages else ""
    temperature = request.get("temperature", 0.7)
    
    return f"Manually extracted content: {content}, Temperature: {temperature}"
```

**Use cases**: When you need complete control over request processing logic, or when the request structure is very complex, manual mapping mode is more flexible.

### Response Mapping

Response mapping determines how to convert the function's return value into a response that conforms to the OpenAI API format. EasyMaaS also provides two mapping modes:

#### 1. Automatic Mapping Mode (`map_response=True`)

In automatic mapping mode, EasyMaaS intelligently maps the function's return value to the standard OpenAI response template. This allows you to focus on business logic without having to manually construct complex response structures.

**Supported return value types**:

1. **String**: Directly used as response content
   ```python
   @service(model_name="string-example", map_response=True)
   def string_response():
       return "This is a simple string response"
   ```
   Generated response:
   ```json
   {
     "id": "chatcmpl-123...",
     "object": "chat.completion",
     "created": 1677652288,
     "model": "string-example",
     "choices": [{
       "index": 0,
       "message": {
         "role": "assistant",
         "content": "This is a simple string response"
       },
       "finish_reason": "stop"
     }],
     "usage": {...}
   }
   ```

2. **Dictionary**: Recursively mapped to response template
   ```python
   @service(model_name="dict-example", map_response=True)
   def dict_response():
       return {
           "content": "This is the content field in the dictionary",
           "finish_reason": "length"  # Override default value
       }
   ```
   Generated response:
   ```json
   {
     "id": "chatcmpl-123...",
     "object": "chat.completion",
     "created": 1677652288,
     "model": "dict-example",
     "choices": [{
       "index": 0,
       "message": {
         "role": "assistant",
         "content": "This is the content field in the dictionary"
       },
       "finish_reason": "length"  # Overridden value
     }],
     "usage": {...}
   }
   ```

3. **Generator**: Used for streaming responses (requires setting `supports_streaming=True`)
   ```python
   @service(
       model_name="stream-example", 
       map_response=True,
       supports_streaming=True
   )
   async def stream_response():
       words = "This is a streaming response example, each word will be sent separately".split()
       for word in words:
           yield word  # String chunk
           # Or use a dictionary: yield {"content": word}
           await asyncio.sleep(0.1)
   ```

**How it works**:
- The system automatically selects the appropriate mapping strategy based on the return value type
- For dictionary types, it recursively finds and updates the corresponding fields in the response template
- For streaming responses, it converts each generated chunk into the standard streaming response format

#### 2. Manual Mapping Mode (`map_response=False`, default mode)

In manual mapping mode, the function needs to return a complete OpenAI format response. This mode is suitable for scenarios where you need complete control over the response structure.

```python
import time
import uuid

@service(model_name="manual-response-example")
def manual_response(request):
    return {
        "id": "chatcmpl-" + str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "manual-response-example",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a manually constructed response"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }
```

**Use cases**: When you need complete control over the response structure, or need to customize special fields, manual mapping mode is more suitable.

## Usage Examples

Here are some examples of common scenarios to help you quickly get started with EasyMaaS.

### Basic Example

The simplest service example, manually processing requests and returning string responses:

```python
from easymaas import service

@service(model_name="greeting")
def greeting_service(request):
    # Extract user name from request
    messages = request.get("messages", [])
    user_message = messages[-1].get("content", "") if messages else ""
    
    # Simple greeting logic
    if "hello" in user_message.lower() or "hi" in user_message.lower():
        return "Hello! How can I help you?"
    elif "name" in user_message or "who are you" in user_message.lower():
        return "I am an AI assistant powered by EasyMaaS, nice to serve you!"
    else:
        return f"Received your message: {user_message}, how can I help you?"
```

### Automatic Parameter Mapping Example

Using automatic parameter mapping to directly extract required parameters from the request:

```python
from easymaas import service

@service(model_name="auto-mapping", map_request=True, map_response=True)
def auto_mapping_service(content: str, temperature: float = 0.7, max_tokens: int = 100):
    # content will be automatically extracted from request.messages[-1].content
    # temperature and max_tokens will be extracted from top-level parameters in the request
    
    response = f"Processed content: {content}\n"
    response += f"Temperature used: {temperature}\n"
    response += f"Max tokens: {max_tokens}"
    
    return response  # Automatically mapped to OpenAI response format
```

### Streaming Response Example

Implementing a typewriter effect streaming response service:

```python
import asyncio
from easymaas import service

@service(
    model_name="stream-example", 
    map_response=True,
    supports_streaming=True
)
async def stream_service(request):
    # Extract content from request
    messages = request.get("messages", [])
    content = messages[-1].get("content", "") if messages else ""
    
    # Generate response prefix
    yield "Processing your request...\n"
    await asyncio.sleep(0.5)
    
    # Output response character by character
    response = f"Your input is: {content}\nThis is a streaming response example, each character will be sent separately..."
    for char in response:
        yield char  # Generate one character at a time
        await asyncio.sleep(0.05)  # Simulate typing effect
    
    # Generate response suffix
    await asyncio.sleep(0.3)
    yield "\n\nProcessing complete!"
```

### Advanced Mapping Example

Combining automatic request mapping and manual response construction:

```python
import time
import uuid
from easymaas import service

@service(model_name="advanced-example", map_request=True)
def advanced_service(content: str, temperature: float = 0.7):
    # Process business logic
    processed_content = f"Advanced processing: {content}"
    
    # Manually construct complete OpenAI response
    return {
        "id": "chatcmpl-" + str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "advanced-example",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": processed_content
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": len(content.split()),
            "completion_tokens": len(processed_content.split()),
            "total_tokens": len(content.split()) + len(processed_content.split())
        }
    }
```

### Error Handling Example

Gracefully handling exception situations:

```python
from easymaas import service
import logging

@service(model_name="error-handling", map_response=True)
def error_handling_service(request):
    try:
        # Try to process the request
        messages = request.get("messages", [])
        if not messages:
            return "Error: No messages provided"
            
        content = messages[-1].get("content", "")
        if not content:
            return "Error: Message content is empty"
        
        # Simulate an operation that might fail
        if "divide by zero" in content:
            result = 1 / 0  # Will trigger an exception
        
        return f"Successfully processed: {content}"
        
    except Exception as e:
        # Log the error and return a friendly error message
        logging.error(f"Error processing request: {str(e)}")
        return {
            "content": f"An error occurred while processing your request: {str(e)}",
            "finish_reason": "error"  # Custom finish reason
        }
```

## Best Practices

When developing services with EasyMaaS, here are some recommended best practices:

### 1. Choose Mapping Modes Wisely

- **Simple services**: For simple services, using `map_request=True` and `map_response=True` can greatly reduce code volume, allowing you to focus on business logic
- **Complex services**: For complex services, you may need manual control over request and response processing, in which case you can choose the default manual mapping mode
- **Mixed mode**: You can also enable only one of the mapping modes, for example, only enable request mapping but manually construct the response

### 2. Exception Handling

- Always add appropriate exception handling in services to prevent services from crashing due to uncaught exceptions
- Use logging to record exception information for debugging and monitoring
- Return friendly error messages to improve user experience

### 3. Streaming Response Optimization

- In streaming responses, try to keep the size of each chunk moderate, neither too large nor too small
- Consider adding appropriate delays in streaming responses to simulate real typing effects
- For long texts, consider chunking by sentences or paragraphs rather than by characters

### 4. Performance Considerations

- For compute-intensive tasks, consider using asynchronous functions and parallel processing
- Avoid long-blocking operations in services, which may affect the responsiveness of the entire service
- For services that need to access external resources, consider adding timeout and retry mechanisms

### 5. Service Management

- Provide clear descriptions for each service for easy management and use
- Use meaningful model names that reflect the functionality and purpose of the service
- For production environments, consider adding monitoring and logging

## Advanced Topics

### Service Registration and Discovery

EasyMaaS uses the `ServiceRegistry` class to manage all registered services. When you use the `@service` decorator, the service is automatically registered in this registry. You can access the registry as follows:

```python
from easymaas.core.decorators import ServiceRegistry

# Get all registered services
services = ServiceRegistry.list_services()
print(f"Registered services: {services}")

# Get configuration for a specific service
config = ServiceRegistry.get_service_config("my-model")
print(f"Service configuration: {config}")
```

### Custom Response Templates

EasyMaaS uses predefined templates to generate OpenAI format responses. If you need to customize these templates, you can modify the `config/templates.py` file.

## Frequently Asked Questions

### Q: Does EasyMaaS support all OpenAI API features?

A: EasyMaaS currently mainly supports the Chat Completions API, including streaming responses. Other APIs (such as Embeddings, Images, etc.) are not yet fully supported, but are planned to be added in future versions.

### Q: How do I use custom models in EasyMaaS?

A: You can register services with any model name, just make sure to use the same name when calling. EasyMaaS doesn't care about the actual implementation of the model, it's just a tool that wraps Python functions as OpenAI-compatible APIs.

### Q: Does EasyMaaS support authentication?

A: Currently EasyMaaS does not validate API keys, but you can integrate it into existing FastAPI or Flask projects and leverage the authentication mechanisms of these frameworks.

## More Resources

- [OpenAI API Format Specification](openai_api_format.md) - Learn how EasyMaaS maps OpenAI API formats
- [CLI Command Reference](cli_reference.md) - View all available command-line tools
- [Why Choose EasyMaaS](why_easymaas.md) - Understand the design philosophy and advantages of EasyMaaS