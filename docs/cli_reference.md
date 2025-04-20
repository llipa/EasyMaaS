# CLI 命令参考

EasyMaaS 提供了简单易用的命令行工具，帮助您管理服务。本文档详细介绍了所有可用的CLI命令。

## 基本命令

### 初始化项目

```bash
easymaas init
```

此命令会：
- 创建 `.easymaas` 目录
- 创建 `services` 目录
- 在 `services` 目录下创建示例服务文件 `example_service.py`

### 启动服务

```bash
easymaas start [OPTIONS]
```

选项：
- `--host TEXT`: 服务器主机地址 (默认: "0.0.0.0")
- `--port INTEGER`: 服务器端口 (默认: 8000)
- `--reload`: 启用自动重载（开发模式）
- `--services-dir TEXT`: 服务文件目录 (默认: "services")

### 列出服务

```bash
easymaas list-services [OPTIONS]
```

选项：
- `--services-dir TEXT`: 服务文件目录 (默认: "services")

此命令会列出指定目录下所有可用的服务。

### 查看服务状态

```bash
easymaas status
```

此命令会显示：
- 当前所有活跃的部署
- 每个部署的详细信息：
  - 部署目录
  - 主机地址
  - 端口号
  - 进程ID
  - 运行时间
  - 包含的服务列表

## 服务管理

服务管理主要通过 `services` 目录进行：

1. 在 `services` 目录下创建 Python 文件
2. 使用 `@service` 装饰器定义服务
3. 使用 `easymaas start` 启动服务

示例服务文件 (`services/example_service.py`):

```python
from easymaas import service

@service(model_name="example-model", description="An example service")
def example_service(content: str):
    return f"Processed: {content}"
```

## 部署管理

EasyMaaS 会自动管理部署信息：

- 部署信息存储在 `.easymaas` 目录
- 自动清理已停止的部署
- 自动检测端口冲突
- 记录服务启动时间和进程信息

## 故障排除

如果遇到问题：

1. 检查端口是否被占用
2. 确认服务文件格式正确
3. 查看服务是否正确定义
4. 使用 `--reload` 选项进行开发调试

## 注意事项

1. 服务文件必须放在 `services` 目录下
2. 服务必须使用 `@service` 装饰器
3. 服务必须指定 `model_name`
4. 建议在开发时使用 `--reload` 选项
5. 生产环境建议使用配置文件管理服务 