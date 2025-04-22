# OpenAI API 格式映射说明

EasyMaaS 支持将 Python 函数映射为 OpenAI 兼容的 API 服务。本文档详细介绍了支持的函数类型和参数映射规则。

## 基本用法

使用 `@service` 装饰器将函数转换为服务：

```python
from easymaas import service

@service(model_name="my-model", description="My custom service")
def my_function(content: str):
    return f"Processed: {content}"
```

## 参数映射

### 自动参数映射

EasyMaaS 使用递归JSON映射机制，自动将 OpenAI API 请求中的参数映射到函数参数，例如：

1. `content` 参数会自动映射到最后一个用户消息的内容
2. `request` 参数会接收完整的请求对象
3. 其他参数会尝试从请求对象中获取对应属性

### 参数验证
EasyMaaS 会在服务运行时动态验证函数参数是否可以正确映射到请求：

1. 在运行时，会记录未映射的参数并发出警告
2. 系统会提供详细的错误信息，包括可用参数列表
例如，如果函数包含无法映射的参数：

```python
@service(model_name="invalid-param-model")
def invalid_param_function(content: str, invalid_param: str):
    return f"Content: {content}, Invalid: {invalid_param}"
```

系统会生成类似以下的警告：

```plaintext
================================================================================
⚠️ 警告: 函数 'invalid_param_function' 的以下参数无法映射到请求: invalid_param
================================================================================
```

### 支持的参数类型

函数可以接收以下参数：

```python
@service(model_name="my-model")
def my_function(
    content: str,                    # 用户消息内容
    request: ChatCompletionRequest,  # 完整请求对象
    temperature: float,              # 温度参数
    top_p: float,                    # top_p参数
    n: int,                          # 生成数量
    stream: bool,                    # 是否流式响应
    stop: Union[str, List[str]],     # 停止标记
    max_tokens: int,                 # 最大token数
    presence_penalty: float,         # 存在惩罚
    frequency_penalty: float,        # 频率惩罚
    user: str                        # 用户标识
):
    # 函数实现
    pass
```

## 返回值处理

### 基本返回值

函数可以返回以下类型的值：

1. 字符串：直接作为响应内容
2. 字典：支持以下字段
   ```python
   {
       "content": "响应内容",
       "role": "assistant",
       "finish_reason": "stop",
       "prompt_tokens": 10,
       "completion_tokens": 20,
       "total_tokens": 30
   }
   ```

EasyMaaS使用递归JSON映射机制处理返回值，将函数返回的字典值映射到标准OpenAI响应格式中。这使得开发者可以灵活地控制响应的各个方面，而不必构建完整的响应对象。

### 返回值验证

EasyMaaS 会验证函数返回值是否符合预期格式：

1. 返回值应为字符串或包含响应的键的字典
2. 如果返回值格式不正确，系统会发出警告
例如，如果函数返回不符合格式的字典：

```python
@service(model_name="invalid-return-model")
def invalid_return_function(content: str):
    return {"invalid_key": "value"}  # 缺少 content 键
```

系统会生成类似以下的警告：

```plaintext
================================================================================
⚠️ 警告: 函数 'invalid_return_function' 的无法匹配到返回值 'invalid_key' 到响应
================================================================================
```

### 流式响应

要支持流式响应，函数需要返回可迭代对象：

```python
@service(model_name="stream-model")
async def stream_function(content: str):
    for chunk in generate_chunks(content):
        yield chunk
```

## 异步支持

支持同步和异步函数：

```python
# 同步函数
@service(model_name="sync-model")
def sync_function(content: str):
    return process_content(content)

# 异步函数
@service(model_name="async-model")
async def async_function(content: str):
    return await process_content_async(content)
```

## 示例

### 简单文本处理

```python
@service(model_name="text-processor")
def process_text(content: str):
    return f"Processed: {content.upper()}"
```

### 多选项生成

```python
@service(model_name="multi-choice")
def generate_choices(content: str, n: int = 3):
    return [
        {"content": f"Option {i}: {content}", "role": "assistant"}
        for i in range(n)
    ]
```

### 流式响应

```python
@service(model_name="stream-generator")
async def stream_generator(content: str):
    words = content.split()
    for word in words:
        yield {"content": word}
        await asyncio.sleep(0.1)
```

## 注意事项

1. 函数必须指定 `model_name`
2. 建议提供函数描述
3. 流式响应需要使用异步函数
4. 返回值会被自动转换为 OpenAI 兼容格式
