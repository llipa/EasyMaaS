# EasyMaaS: Making AI Service Deployment Easy

EasyMaaS is a lightweight Python library that makes it easy to wrap Python code into OpenAI-compatible services. It provides a simple and flexible way to create and manage AI services, supporting rapid deployment and integration.

In AI application development, we often need to encapsulate local models or business logic into API services. OpenAI's API format has become a de facto standard due to its simplicity and widespread use. However, implementing complete OpenAI API compatibility for each service is a repetitive and tedious task. EasyMaaS was born to solve this problem, allowing developers to focus on business logic rather than repeatedly implementing API format conversion.

If you have functions or models that you want to encapsulate into OpenAI-format APIs, EasyMaaS can help you quickly wrap them and provide one-click deployment methods.

[Learn more about project background and motivation](docs/en/why_easymaas.md)

## Features

- 🚀 Quickly convert Python functions to OpenAI-compatible API services
- 📦 Built-in CLI tools for simplified service management
- 🔌 Automatic OpenAI API format mapping
- 🛠️ Support for both async and sync functions

## Installation

```bash
# Install using pip
git clone https://github.com/llipa/EasyMaaS.git
cd EasyMaaS
pip install -e .

# Install using uv
uv add --editable /path/to/EasyMaaS
```

## Quick Start

1. Create a project (recommended using uv)

```bash
# Create project
mkdir your_project
cd your_project
uv init # Initialize with uv

# Install using uv
uv add --editable /path/to/EasyMaaS
```

2. Create a simple service:

```python
from easymaas import service

@service(model_name="example-model", description="An example service")
def example_service(content: str):
    return f"Processed: {content}"
```

3. Start the service:

```bash
easymaas start
```

4. Use the service:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="xxx"
)

response = client.chat.completions.create(
    model="example-model",
    messages=[
        {
            "role": "user",
            "content": "test EasyMaaS."
        }
    ]
)

print(response.choices[0].message.content)
```

## Documentation

- [Why Choose EasyMaaS](docs/en/why_easymaas.md) - Learn about project background, advantages, and use cases
- [OpenAI API Format Mapping](docs/en/openai_api_format.md) - Learn how to map Python functions to OpenAI-compatible services
- [CLI Command Reference](docs/en/cli_reference.md) - View all available command-line tools

## Project Structure

```
easymaas/
├── src/
│   └── easymaas/
│       ├── core/          # Core functionality modules
│       ├── server/        # Server implementation
│       ├── cli/           # Command-line tools
│       └── config/        # Configuration management
├── examples/              # Example services
└── docs/                  # Documentation
```

## Contributing

We welcome all forms of contributions! You can also submit your valuable feedback through Issues.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or suggestions, please contact us through:
- GitHub Issues
- Project maintainer email

## Acknowledgments

Thanks to all developers who have contributed to this project!