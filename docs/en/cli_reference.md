# CLI Command Reference

EasyMaaS provides a complete set of command-line tools to help you easily create, manage, and deploy services. This document details all available commands and their usage, helping you quickly get started with EasyMaaS service management features.

## Command Overview

| Command | Description |
|---------|-------------|
| `easymaas init` | Initialize EasyMaaS project |
| `easymaas start` | Start service |
| `easymaas list-services` | List all available services |
| `easymaas status` | View service status |

Below is a detailed explanation and usage example for each command:

## Basic Commands

### Initialize Project

```bash
easymaas init
```

This command will:
- Create the `.easymaas` directory
- Create the `services` directory
- Create an example service file `example_service.py` in the `services` directory

### Start Service

```bash
easymaas start [OPTIONS]
```

Options:
- `--host TEXT`: Server host address (default: "0.0.0.0")
- `--port INTEGER`: Server port (default: 8000)
- `--reload`: Enable auto-reload (development mode)
- `--services-dir TEXT`: Service files directory (default: "services")

### List Services

```bash
easymaas list-services [OPTIONS]
```

Options:
- `--services-dir TEXT`: Service files directory (default: "services")

This command lists all available services in the specified directory.

### View Service Status

```bash
easymaas status
```

This command displays:
- All currently active deployments
- Detailed information for each deployment:
  - Deployment directory
  - Host address
  - Port number
  - Process ID
  - Running time
  - List of included services

## Service Management

Service management is primarily done through the `services` directory:

1. Create Python files in the `services` directory
2. Define services using the `@service` decorator
3. Start services using `easymaas start`

Example service file (`services/example_service.py`):

```python
from easymaas import service

@service(model_name="example-model", description="An example service")
def example_service(content: str):
    return f"Processed: {content}"
```

## Deployment Management

EasyMaaS automatically manages deployment information:

- Deployment information is stored in the `.easymaas` directory
- Automatically cleans up stopped deployments
- Automatically detects port conflicts
- Records service start time and process information

## Troubleshooting

If you encounter issues:

1. Check if the port is already in use
2. Confirm that the service file format is correct
3. Check if the service is correctly defined
4. Use the `--reload` option for development debugging

## Notes

1. Service files must be placed in the `services` directory
2. Services must use the `@service` decorator
3. Services must specify `model_name`
4. It is recommended to use the `--reload` option during development
5. For production environments, it is recommended to use configuration files to manage services