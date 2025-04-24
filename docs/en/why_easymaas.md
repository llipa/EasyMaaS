# Why Choose EasyMaaS

## Project Background

In AI application development, we often need to encapsulate local models or business logic into API services. OpenAI's API format has become a de facto standard due to its simplicity and widespread use. However, implementing complete OpenAI API compatibility for each service is a repetitive and tedious task.

Imagine that every time you want to wrap a Python function or model into an API service, you need to:
- Handle complex request parameter mapping
- Implement standard response formats
- Manage deployment status of multiple services
- Handle special cases like streaming responses

This is not only time-consuming but also error-prone. EasyMaaS was born to solve this problem. It provides a lightweight solution that allows developers to focus on business logic rather than repeatedly implementing API format conversion.

## Core Advantages

EasyMaaS is designed with simplicity, lightness, and ease of use in mind. Through decorator syntax, it allows developers to convert Python functions into OpenAI-compatible services with just one line of code. For example:

```python
@service(model_name="my-model")
def my_function(content: str):
    return f"Processed: {content}"
```

This design keeps the code clean while automatically handling complex parameter mapping and response format conversion. EasyMaaS automatically maps parameters from OpenAI API requests to function parameters and handles different types of return values to ensure they conform to OpenAI's response format.

In terms of service management, EasyMaaS provides simple CLI tools to help developers manage multiple services in a project. It creates a `.easymaas` directory in the project root to store service information and deployment status, making service management simple and unified.

## New Features

The latest version of EasyMaaS introduces the following new features:

1. **Flexible Request/Response Mapping**
   - Use `map_request` and `map_response` options to control automatic parameter and response format mapping
   - Support custom mapping logic to meet different scenario requirements

2. **Streaming Response Support**
   - Support generator functions for streaming responses
   - Automatically handle streaming response format conversion to ensure OpenAI compliance

3. **Enhanced Error Handling**
   - Provide detailed error messages and warnings to help developers quickly identify issues
   - Automatically handle exceptions to ensure service stability

## Use Cases

EasyMaaS is particularly suitable for the following scenarios:

1. **Local Model Service**
   If you have a locally trained model that you want to quickly deploy as an API service, EasyMaaS can help you achieve this easily. It supports various model formats and frameworks, making model testing and integration simple.

2. **Business Logic Encapsulation**
   For scenarios that require encapsulating complex business logic into standardized services, EasyMaaS provides a unified interface format. Whether synchronous or asynchronous functions, they can be easily converted into standardized API services.

3. **Rapid Prototyping**
   In the early stages of development, you may need to quickly validate ideas or test model performance. EasyMaaS's simple design allows you to quickly deploy services for testing and iteration.
