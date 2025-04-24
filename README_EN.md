# EasyMaaS: Easily Build OpenAI-Compatible AI Services

[English](./README_EN.md) | [中文](./README.md)

## What is EasyMaaS

EasyMaaS is a lightweight Python framework designed for AI developers, enabling you to convert ordinary Python functions into fully OpenAI API-compatible services with minimal effort. Through simple decorator syntax, you can focus on core business logic without dealing with complex API format conversion work.

```python
# One line of code to easily create an OpenAI-compatible service
@service(model_name="my-model", map_request=True, map_response=True)
def my_service(content: str):
    return f"Processing result: {content}"
```

## Why Choose EasyMaaS

In current AI service development, developers often spend significant time handling API format conversions and parameter mapping. EasyMaaS was created to solve this pain point, offering:

- 🚀 **Minimalist Development Experience**: Create complete OpenAI-compatible services with just one line of code using decorator syntax
- 🔌 **Intelligent Parameter Mapping**: Automatically handle complex request parameter extraction and response format conversion
- 🌊 **Native Streaming Support**: Easily implement ChatGPT-like typewriter effect output
- 🔄 **Flexible Configuration Options**: Customize request/response mapping behavior according to your needs
- 🛠️ **Full-Stack Function Support**: Support both synchronous and asynchronous functions for various development scenarios
- 📦 **Convenient Service Management**: Built-in CLI tools to simplify service registration, deployment, and management

## Quick Start

### Installation

```bash
# Install using pip
git clone https://github.com/llipa/EasyMaaS.git
cd EasyMaaS
pip install -e .

# Or install using uv
uv add --editable /path/to/EasyMaaS
```

### Create Your First Service

1. Create a project (recommended using uv)

```bash
# Create project directory
mkdir your_project
cd your_project
uv init  # Initialize project with uv

# Install EasyMaaS
uv add --editable /path/to/EasyMaaS
```

2. Create a simple service

```python
# app.py
from easymaas import service

@service(
    model_name="greeting-service",  # Model name, required parameter
    description="A simple greeting service",  # Service description, optional
    map_request=True,             # Enable automatic request mapping
    map_response=True             # Enable automatic response mapping
)
def greeting(content: str = ""):
    """A simple greeting service"""
    if not content:
        return "Hello! How can I help you?"
    
    if "hello" in content.lower():
        return "Hello! I'm happy to serve you."
    elif "name" in content.lower():
        return "I'm an AI assistant powered by EasyMaaS, nice to meet you!"
    else:
        return f"I received your message: {content}. How can I help you?"
```

3. Start the service

```bash
# Start the service (default port 8000)
python -m easymaas.cli.commands start

# Or specify a port
python -m easymaas.cli.commands start --port 3000

# Directly use the easymaas command-line tool (default port 8000)
easymaas start

# Or specify a port
easymaas start --port 3000
```

4. Call the service

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "greeting-service",
    "messages": [
      {"role": "user", "content": "Hello, what's your name?"}
    ]
  }'
```

## Core Features

### Intelligent Parameter Mapping

The core functionality of EasyMaaS is its intelligent parameter mapping mechanism, which can:

- **Automatically Extract Parameters**: Extract function parameters from complex nested JSON requests
- **Flexible Response Conversion**: Automatically convert simple return values to standard OpenAI response format
- **Recursive Mapping Processing**: Intelligently handle various data types and nested structures

This mapping mechanism allows you to focus on business logic without dealing with tedious format conversion work.

### Streaming Response Support

EasyMaaS natively supports streaming responses, making it easy to implement ChatGPT-like typewriter effects:

```python
import asyncio
from easymaas import service

@service(
    model_name="stream-demo",
    map_response=True,
    supports_streaming=True  # Enable streaming response support
)
async def stream_service(request):
    # Extract content from request
    messages = request.get("messages", [])
    content = messages[-1].get("content", "") if messages else ""
    
    # Output response character by character
    response = f"Your input is: {content}\nThis is a streaming response example..."
    for char in response:
        yield char  # Generate one character at a time
        await asyncio.sleep(0.05)  # Simulate typing effect
```

## Advanced Usage

### Request Mapping Modes

EasyMaaS provides two request mapping modes:

1. **Automatic Mapping** (`map_request=True`): Automatically extract fields from the request that match function parameter names
2. **Manual Mapping** (`map_request=False`, default): Pass the entire request object to the function's first parameter

### Response Mapping Modes

Similarly, EasyMaaS also provides two response mapping modes:

1. **Automatic Mapping** (`map_response=True`): Automatically convert function return values to OpenAI format responses
2. **Manual Mapping** (`map_response=False`, default): Function needs to return complete OpenAI format responses

## Documentation and Resources

- [Detailed Usage Guide](docs/en/usage_guide.md)
- [OpenAI API Format Specification](docs/en/openai_api_format.md)
- [CLI Command Reference](docs/en/cli_reference.md)
- [Why Choose EasyMaaS](docs/en/why_easymaas.md)

## Contributions and Feedback

EasyMaaS is an open-source project, and we welcome contributions and feedback in any form. If you have any questions or suggestions, please submit them through GitHub Issues.

## License

EasyMaaS is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## TODO
- [x] Support custom response templates
- [x] Support API key validation
- [x] Support custom mapping mechanisms
- [x] Support quick integration with existing projects