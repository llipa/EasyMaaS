# OpenAI API 格式映射说明

EasyMaaS 提供了强大的参数映射机制，能够自动处理请求和响应格式的转换。本文档专注于描述参数映射的具体规则和行为。

## 请求参数映射

当启用自动请求映射(map_request=True)时，EasyMaaS会递归遍历整个请求JSON结构，查找与函数参数名匹配的键值对。无论参数位于请求的哪个层级，只要名称匹配就会被自动提取并传递给函数。

例如，如果函数定义为`def my_func(content: str, temperature: float)`，系统会自动从请求中查找名为"content"和"temperature"的字段，无论它们位于请求体的哪个位置。

## 响应参数映射

响应映射遵循预定义的模板结构(参考templates.py)，只有模板中定义的字段才会被自动映射。这意味着即使函数返回的字典包含额外字段，这些字段也不会出现在最终响应中，除非它们被明确包含在模板中。

当前支持的响应模板包括标准响应和流式响应两种格式，具体字段定义如下：

### 标准响应模板
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

### 流式响应模板
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

## 返回值处理

函数可以返回以下类型的值，系统会根据返回值类型自动选择合适的映射策略：

1. **字符串**：直接作为响应内容(message.content或delta.content)
2. **字典**：递归查找并更新响应模板中的对应字段
3. **生成器**：用于流式响应，每个生成的块都会转换为标准的流式响应格式
