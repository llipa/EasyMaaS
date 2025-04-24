# EasyMaaS: 轻松构建OpenAI兼容的AI服务

中文 | [English](./README_EN.md)

## 什么是EasyMaaS

EasyMaaS是一个轻量级Python框架，专为AI开发者设计，能够以极简的方式将普通Python函数转换为完全兼容OpenAI API格式的服务。通过简单的装饰器语法，您可以专注于核心业务逻辑，而无需处理复杂的API格式转换工作。

```python
# 一行代码，轻松创建OpenAI兼容服务
@service(model_name="my-model", map_response=True)
def my_service(content: str):
    return f"处理结果: {content}"
```

## 为什么选择EasyMaaS

在当前AI服务开发中，开发者常常需要花费大量时间处理API格式转换、参数映射等繁琐工作。EasyMaaS正是为解决这一痛点而生，它提供了：

- 🚀 **极简开发体验**：通过装饰器语法，一行代码即可创建完整的OpenAI兼容服务
- 🔌 **智能参数映射**：自动处理复杂的请求参数提取和响应格式转换
- 🌊 **原生流式支持**：轻松实现类似ChatGPT的打字机效果输出
- 🔄 **灵活配置选项**：可根据需求自定义请求/响应映射行为
- 🛠️ **全栈函数支持**：同时支持同步和异步函数，适应各种开发场景
- 📦 **便捷服务管理**：内置CLI工具，简化服务的注册、部署和管理

## 快速开始

### 安装

```bash
# 使用pip安装
git clone https://github.com/llipa/EasyMaaS.git
cd EasyMaaS
pip install -e .

# 或使用uv安装
uv add --editable /path/to/EasyMaaS
```

### 创建您的第一个服务

1. 创建项目（推荐使用uv）

```bash
# 创建项目目录
mkdir your_project
cd your_project
uv init  # 使用uv初始化项目

# 安装EasyMaaS
uv add --editable /path/to/EasyMaaS
```

2. 创建一个简单的服务

```python
# app.py
from easymaas import service

@service(
    model_name="greeting-service",  # 模型名称，必需参数
    description="简单的问候服务",  # 服务描述，可选
    map_request=True,             # 启用自动请求映射
    map_response=True             # 启用自动响应映射
)
def greeting(content: str = ""):
    """简单的问候服务"""
    if not content:
        return "你好！有什么可以帮助你的吗？"
    
    if "你好" in content or "hello" in content.lower():
        return "你好！很高兴为您服务。"
    elif "名字" in content or "叫什么" in content:
        return "我是由EasyMaaS驱动的AI助手，很高兴认识你！"
    else:
        return f"收到您的消息：{content}，请问有什么可以帮助您的？"
```

3. 启动服务

```bash
# 启动服务（默认端口8000）
python -m easymaas.cli.commands start

# 或指定端口
python -m easymaas.cli.commands start --port 3000

# 直接使用命令行工具easymaas启动（默认端口8000）
easymaas start

# 或指定端口
easymaas start --port 3000
```

4. 调用服务

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "greeting-service",
    "messages": [
      {"role": "user", "content": "你好，你叫什么名字？"}
    ]
  }'
```

## 核心功能

### 智能参数映射

EasyMaaS的核心功能是智能参数映射机制，它能够：

- **自动提取参数**：从复杂的嵌套JSON请求中自动提取函数所需的参数
- **灵活响应转换**：将简单的返回值自动转换为标准OpenAI响应格式
- **递归映射处理**：智能处理各种数据类型和嵌套结构

这种映射机制让您可以专注于业务逻辑，而不必处理繁琐的格式转换工作。

### 流式响应支持

EasyMaaS原生支持流式响应，让您轻松实现类似ChatGPT的打字机效果：

```python
import asyncio
from easymaas import service

@service(
    model_name="stream-demo",
    map_response=True,
    supports_streaming=True  # 启用流式响应支持
)
async def stream_service(request):
    # 从请求中提取内容
    messages = request.get("messages", [])
    content = messages[-1].get("content", "") if messages else ""
    
    # 逐字输出响应
    response = f"您的输入是: {content}\n这是一个流式响应示例..."
    for char in response:
        yield char  # 每次生成一个字符
        await asyncio.sleep(0.05)  # 模拟打字效果
```

## 进阶使用

### 请求映射模式

EasyMaaS提供两种请求映射模式：

1. **自动映射**（`map_request=True`）：自动从请求中提取与函数参数同名的字段
2. **手动映射**（`map_request=False`，默认）：将整个请求对象传递给函数的第一个参数

### 响应映射模式

同样，EasyMaaS也提供两种响应映射模式：

1. **自动映射**（`map_response=True`）：自动将函数返回值转换为OpenAI格式响应
2. **手动映射**（`map_response=False`，默认）：函数需要返回完整的OpenAI格式响应

## 文档与资源

- [详细使用指南](docs/usage_guide.md)
- [OpenAI API格式说明](docs/openai_api_format.md)
- [CLI命令参考](docs/cli_reference.md)
- [为什么选择EasyMaaS](docs/why_easymaas.md)

## 贡献与反馈

EasyMaaS是一个开源项目，我们欢迎任何形式的贡献和反馈。如果您有任何问题或建议，请通过GitHub Issues提交。

## 许可证

EasyMaaS采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。

## TODO
- [ ] 支持自定义响应模板
- [ ] 支持API密钥校验
- [ ] 支持自定义映射机制
- [ ] 支持快速集成到现有项目
