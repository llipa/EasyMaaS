# EasyMaaS 使用指南

本指南将帮助您快速掌握 EasyMaaS 的核心功能和使用方法，通过详细的示例和说明，让您能够轻松地将 Python 函数转换为 OpenAI 兼容的 API 服务。

## 核心概念

EasyMaaS 的核心是 `@service` 装饰器，它能够将普通的 Python 函数转换为符合 OpenAI API 格式的服务。装饰器提供了多种配置选项，让您可以根据需求自定义服务的行为。

```python
@service(
    model_name="my-model",          # 模型名称（必需）
    description="My service",       # 服务描述（可选）
    map_request=True,               # 是否自动映射请求参数（可选，默认False）
    map_response=True,              # 是否自动映射响应格式（可选，默认False）
    supports_streaming=True         # 是否支持流式响应（可选，默认False）
)
def my_function(param1, param2):
    # 函数实现
    pass
```

## 请求/响应映射机制

EasyMaaS 最强大的特性是智能映射机制，它能够自动处理复杂的请求参数提取和响应格式转换，让您专注于业务逻辑实现。

### 请求映射

请求映射决定了如何将 OpenAI API 格式的请求转换为函数参数。EasyMaaS 提供了两种映射模式：

#### 1. 自动映射模式 (`map_request=True`)

在自动映射模式下，EasyMaaS 会递归查找请求 JSON 中与函数参数名匹配的键，无论这些键位于 JSON 的哪个层级。这使得您可以直接使用函数参数来接收请求中的特定字段，而不必手动解析复杂的 JSON 结构。

```python
@service(model_name="auto-mapping-example", map_request=True)
def example_function(content: str, temperature: float, max_tokens: int = 100):
    # 参数会自动从请求中提取：
    # - content 从 request.messages[-1].content 提取
    # - temperature 从 request.temperature 提取
    # - max_tokens 从 request.max_tokens 提取，如果不存在则使用默认值 100
    return f"处理内容: {content}, 温度: {temperature}, 最大令牌数: {max_tokens}"
```

**工作原理**：
- 系统会递归遍历整个请求 JSON，查找与函数参数名匹配的键
- 如果找到匹配的键，将其值传递给对应的函数参数
- 如果未找到匹配的键，参数将设置为 `None`（除非有默认值）
- 系统会记录未映射的参数并发出警告

#### 2. 手动映射模式 (`map_request=False`，默认模式)

在手动映射模式下，整个请求对象会作为字典传递给函数的第一个参数。这种模式适用于需要完全控制请求处理逻辑的场景。

```python
@service(model_name="manual-mapping-example")
def example_function(request: dict):
    # 手动从请求中提取所需数据
    messages = request.get("messages", [])
    content = messages[-1].get("content", "") if messages else ""
    temperature = request.get("temperature", 0.7)
    
    return f"手动提取的内容: {content}, 温度: {temperature}"
```

**使用场景**：当您需要完全控制请求处理逻辑，或请求结构非常复杂时，手动映射模式更为灵活。

### 响应映射

响应映射决定了如何将函数的返回值转换为符合 OpenAI API 格式的响应。EasyMaaS 同样提供了两种映射模式：

#### 1. 自动映射模式 (`map_response=True`)

在自动映射模式下，EasyMaaS 会将函数的返回值智能地映射到标准的 OpenAI 响应模板中。这使得您可以专注于业务逻辑，而不必手动构建复杂的响应结构。

**支持的返回值类型**：

1. **字符串**：直接作为响应内容
   ```python
   @service(model_name="string-example", map_response=True)
   def string_response():
       return "这是一个简单的字符串响应"
   ```
   生成的响应：
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
         "content": "这是一个简单的字符串响应"
       },
       "finish_reason": "stop"
     }],
     "usage": {...}
   }
   ```

2. **字典**：递归映射到响应模板
   ```python
   @service(model_name="dict-example", map_response=True)
   def dict_response():
       return {
           "content": "这是字典中的内容字段",
           "finish_reason": "length"  # 覆盖默认值
       }
   ```
   生成的响应：
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
         "content": "这是字典中的内容字段"
       },
       "finish_reason": "length"  # 被覆盖的值
     }],
     "usage": {...}
   }
   ```

3. **生成器**：用于流式响应（需要设置 `supports_streaming=True`）
   ```python
   @service(
       model_name="stream-example", 
       map_response=True,
       supports_streaming=True
   )
   async def stream_response():
       words = "这是一个流式响应示例，每个词会单独发送".split()
       for word in words:
           yield word  # 字符串块
           # 或者使用字典：yield {"content": word}
           await asyncio.sleep(0.1)
   ```

**工作原理**：
- 系统会根据返回值类型自动选择合适的映射策略
- 对于字典类型，会递归查找并更新响应模板中的对应字段
- 对于流式响应，会将每个生成的块转换为标准的流式响应格式

#### 2. 手动映射模式 (`map_response=False`，默认模式)

在手动映射模式下，函数需要返回完整的 OpenAI 格式响应。这种模式适用于需要完全控制响应结构的场景。

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
                "content": "这是手动构建的响应"
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

**使用场景**：当您需要完全控制响应结构，或需要自定义特殊字段时，手动映射模式更为适合。

## 实用示例

以下是一些常见场景的使用示例，帮助您快速上手 EasyMaaS。

### 基本示例

最简单的服务示例，手动处理请求并返回字符串响应：

```python
from easymaas import service

@service(model_name="greeting")
def greeting_service(request):
    # 从请求中提取用户名
    messages = request.get("messages", [])
    user_message = messages[-1].get("content", "") if messages else ""
    
    # 简单的问候逻辑
    if "你好" in user_message or "hello" in user_message.lower():
        return "你好！有什么可以帮助你的吗？"
    elif "名字" in user_message or "叫什么" in user_message:
        return "我是由EasyMaaS驱动的AI助手，很高兴为您服务！"
    else:
        return f"收到您的消息：{user_message}，请问有什么可以帮助您的？"
```

### 自动参数映射示例

使用自动参数映射，直接从请求中提取所需参数：

```python
from easymaas import service

@service(model_name="auto-mapping", map_request=True, map_response=True)
def auto_mapping_service(content: str, temperature: float = 0.7, max_tokens: int = 100):
    # content 会自动从请求的messages[-1].content中提取
    # temperature 和 max_tokens 会从请求的顶层参数中提取
    
    response = f"处理内容: {content}\n"
    response += f"使用的温度参数: {temperature}\n"
    response += f"最大令牌数: {max_tokens}"
    
    return response  # 自动映射为OpenAI响应格式
```

### 流式响应示例

实现打字机效果的流式响应服务：

```python
import asyncio
from easymaas import service

@service(
    model_name="stream-example", 
    map_response=True,
    supports_streaming=True
)
async def stream_service(request):
    # 从请求中提取内容
    messages = request.get("messages", [])
    content = messages[-1].get("content", "") if messages else ""
    
    # 生成响应前缀
    yield "正在处理您的请求...\n"
    await asyncio.sleep(0.5)
    
    # 逐字输出响应
    response = f"您的输入是: {content}\n这是一个流式响应示例，每个字符会单独发送..."
    for char in response:
        yield char  # 每次生成一个字符
        await asyncio.sleep(0.05)  # 模拟打字效果
    
    # 生成响应后缀
    await asyncio.sleep(0.3)
    yield "\n\n处理完成！"
```

### 高级映射示例

结合自动请求映射和手动响应构建：

```python
import time
import uuid
from easymaas import service

@service(model_name="advanced-example", map_request=True)
def advanced_service(content: str, temperature: float = 0.7):
    # 处理业务逻辑
    processed_content = f"高级处理: {content}"
    
    # 手动构建完整的OpenAI响应
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

### 错误处理示例

优雅处理异常情况：

```python
from easymaas import service
import logging

@service(model_name="error-handling", map_response=True)
def error_handling_service(request):
    try:
        # 尝试处理请求
        messages = request.get("messages", [])
        if not messages:
            return "错误: 未提供消息"
            
        content = messages[-1].get("content", "")
        if not content:
            return "错误: 消息内容为空"
        
        # 模拟可能出错的操作
        if "除零" in content:
            result = 1 / 0  # 会触发异常
        
        return f"成功处理: {content}"
        
    except Exception as e:
        # 记录错误并返回友好的错误消息
        logging.error(f"处理请求时出错: {str(e)}")
        return {
            "content": f"处理您的请求时出现错误: {str(e)}",
            "finish_reason": "error"  # 自定义结束原因
        }
```

## 最佳实践

在使用 EasyMaaS 开发服务时，以下是一些推荐的最佳实践：

### 1. 合理选择映射模式

- **简单服务**：对于简单的服务，使用 `map_request=True` 和 `map_response=True` 可以大幅减少代码量，让您专注于业务逻辑
- **复杂服务**：对于复杂的服务，可能需要手动控制请求和响应的处理，此时可以选择默认的手动映射模式
- **混合模式**：您也可以只启用其中一种映射模式，例如只启用请求映射但手动构建响应

### 2. 异常处理

- 始终在服务中添加适当的异常处理，避免服务因未捕获的异常而崩溃
- 使用日志记录异常信息，便于调试和监控
- 返回友好的错误消息，提升用户体验

### 3. 流式响应优化

- 流式响应中，尽量保持每个块的大小适中，既不要太大也不要太小
- 考虑在流式响应中添加适当的延迟，模拟真实的打字效果
- 对于长文本，可以按句子或段落进行分块，而不是按字符

### 4. 性能考虑

- 对于计算密集型任务，考虑使用异步函数和并行处理
- 避免在服务中进行长时间阻塞操作，可能影响整个服务的响应性
- 对于需要访问外部资源的服务，考虑添加超时和重试机制

### 5. 服务管理

- 为每个服务提供清晰的描述，便于管理和使用
- 使用有意义的模型名称，反映服务的功能和用途
- 对于生产环境，考虑添加监控和日志记录

## 进阶主题

### 服务注册与发现

EasyMaaS 使用 `ServiceRegistry` 类来管理所有注册的服务。当您使用 `@service` 装饰器时，服务会自动注册到这个注册表中。您可以通过以下方式访问注册表：

```python
from easymaas.core.decorators import ServiceRegistry

# 获取所有注册的服务
services = ServiceRegistry.list_services()
print(f"已注册的服务: {services}")

# 获取特定服务的配置
config = ServiceRegistry.get_service_config("my-model")
print(f"服务配置: {config}")
```

### 自定义响应模板

EasyMaaS 使用预定义的模板来生成 OpenAI 格式的响应。如果您需要自定义这些模板，可以修改 `config/templates.py` 文件。

## 常见问题解答

### Q: EasyMaaS 是否支持所有 OpenAI API 功能？

A: EasyMaaS 目前主要支持 Chat Completions API，包括流式响应。其他 API（如 Embeddings、Images 等）尚未完全支持，但计划在未来版本中添加。

### Q: 如何在 EasyMaaS 中使用自定义模型？

A: 您可以使用任何模型名称注册服务，只需确保在调用时使用相同的名称。EasyMaaS 不关心模型的实际实现，它只是一个将 Python 函数包装为 OpenAI 兼容 API 的工具。

### Q: EasyMaaS 是否支持身份验证？

A: 目前 EasyMaaS 不验证 API 密钥，但您可以通过集成到现有的 FastAPI 或 Flask 项目中，利用这些框架的身份验证机制。

## 更多资源

- [OpenAI API 格式说明](openai_api_format.md) - 了解 EasyMaaS 如何映射 OpenAI API 格式
- [CLI 命令参考](cli_reference.md) - 查看所有可用的命令行工具
- [为什么选择 EasyMaaS](why_easymaas.md) - 了解 EasyMaaS 的设计理念和优势