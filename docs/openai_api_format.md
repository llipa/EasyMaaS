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

EasyMaaS 会自动将 OpenAI API 请求中的参数映射到函数参数：

1. `content` 参数会自动映射到最后一个用户消息的内容
2. `request` 参数会接收完整的请求对象
3. 其他参数会尝试从请求对象中获取对应属性

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
3. 列表：每个元素生成一个选择
   ```python
   [
       {"content": "选项1", "role": "assistant"},
       {"content": "选项2", "role": "assistant"}
   ]
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
3. 参数类型注解有助于自动映射
4. 流式响应需要使用异步函数
5. 返回值会被自动转换为 OpenAI 兼容格式

## 最佳实践

1. 使用类型注解提高可读性
2. 为复杂函数提供详细文档
3. 处理异常情况
4. 合理使用异步函数
5. 考虑性能优化
