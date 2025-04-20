# CLI Command Reference

## Overview

EasyMaaS provides a command-line interface (CLI) for managing services. This document describes all available commands and their usage.

## Basic Commands

### Start Service

Start a service or multiple services:

```bash
# Start all services
easymaas start

# Start a specific service
easymaas start --service my-service
```

Options:
- `--service`: Specify the service name to start
- `--port`: Specify the port number (default: 8000)
- `--host`: Specify the host address (default: 127.0.0.1)

### Stop Service

Stop a running service:

```bash
# Stop all services
easymaas stop

# Stop a specific service
easymaas stop --service my-service
```

Options:
- `--service`: Specify the service name to stop

### List Services

List all registered services:

```bash
easymaas list
```

This command shows:
- Service names
- Descriptions
- Status (running/stopped)
- Port numbers

## Service Management

### Register Service

Register a new service:

```bash
easymaas register --name my-service --path /path/to/service.py
```

Options:
- `--name`: Service name
- `--path`: Path to the service file
- `--description`: Service description (optional)

### Remove Service

Remove a registered service:

```bash
easymaas remove --service my-service
```

Options:
- `--service`: Service name to remove

### Update Service

Update service configuration:

```bash
easymaas update --service my-service --description "New description"
```

Options:
- `--service`: Service name to update
- `--description`: New description (optional)
- `--path`: New service file path (optional)

## Configuration

### Set Configuration

Set global configuration:

```bash
easymaas config set --key log_level --value debug
```

Options:
- `--key`: Configuration key
- `--value`: Configuration value

### Get Configuration

Get global configuration:

```bash
easymaas config get --key log_level
```

Options:
- `--key`: Configuration key to get

### List Configuration

List all configurations:

```bash
easymaas config list
```

## Examples

### Basic Usage

```bash
# Register a service
easymaas register --name echo --path ./services/echo.py

# Start the service
easymaas start --service echo

# List services
easymaas list

# Stop the service
easymaas stop --service echo
```

### Advanced Usage

```bash
# Register multiple services
easymaas register --name service1 --path ./services/service1.py
easymaas register --name service2 --path ./services/service2.py

# Start all services
easymaas start

# Update service configuration
easymaas update --service service1 --description "Updated description"

# Set global configuration
easymaas config set --key log_level --value info

# List all configurations
easymaas config list
``` 