# EasyMaaS: 让AI服务部署变得简单

中文 | [Engilsh](./README_EN.md)

EasyMaaS 是一个轻量级的Python库，用于将Python代码轻松包装成OpenAI兼容的服务。它提供了一个简单而灵活的方式来创建和管理AI服务，支持快速部署和集成。

在 AI 应用开发中，我们经常需要将本地模型或业务逻辑封装成 API 服务。OpenAI 的 API 格式因其简洁性和广泛使用而成为了事实上的标准。然而，为每个服务实现完整的 OpenAI API 兼容性是一项重复且繁琐的工作。EasyMaaS 的诞生正是为了解决这个问题，让开发者能够专注于业务逻辑，而不是重复实现 API 格式转换。

如果您的项目有一些函数或模型想要封装成OpenAI格式的API，EasyMaaS可以帮助您快速封装，并提供一键部署方法。

[了解更多项目背景和动机](docs/why_easymaas.md)

## 特性

- 🚀 快速将Python函数转换为OpenAI兼容的API服务
- 📦 内置CLI工具，简化服务管理
- 🔌 自动映射OpenAI API格式
- 🛠️ 支持异步和同步函数

## 安装

```bash
# 使用 pip 安装
git clone https://github.com/llipa/EasyMaaS.git
cd EasyMaaS
pip install -e .

# 使用 uv 安装
uv add --editable /path/to/EasyMaaS
```

## 快速开始

1. 创建一个项目（推荐使用uv）

```bash
# 创建项目
mkdir your_project
cd your_project
uv init # 使用 uv 初始化

# 使用 uv 安装
uv add --editable /path/to/EasyMaaS
```

2. 创建一个简单的服务：

```python
from easymaas import service

@service(model_name="example-model", description="An example service")
def example_service(content: str):
    return f"Processed: {content}"
```

2. 启动服务：

```bash
easymaas start
```

3. 使用服务：

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

## 详细文档

- [为什么选择 EasyMaaS](docs/why_easymaas.md) - 了解项目背景、优势和使用场景
- [OpenAI API 格式映射说明](docs/openai_api_format.md) - 了解如何将Python函数映射为OpenAI兼容的服务
- [CLI 命令参考](docs/cli_reference.md) - 查看所有可用的命令行工具

## 项目结构

```
easymaas/
├── src/
│   └── easymaas/
│       ├── core/          # 核心功能模块
│       ├── server/        # 服务器实现
│       ├── cli/           # 命令行工具
│       └── config/        # 配置管理
├── examples/              # 示例服务
└── docs/                  # 文档
```

## 贡献指南

我们欢迎任何形式的贡献！也可以通过Issue提交您的宝贵意见。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有任何问题或建议，请通过以下方式联系我们：
- GitHub Issues
- 项目维护者邮箱

## 致谢

感谢所有为这个项目做出贡献的开发者！
