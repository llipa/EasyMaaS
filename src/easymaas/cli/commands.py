import click
import uvicorn
import os
import sys
import ast
import time
import psutil
from pathlib import Path
from typing import Tuple, List, Dict, Any
from ..core.decorators import ServiceRegistry
from ..core.config import DeploymentManager, DeploymentInfo, ServiceInfo

def find_decorated_services(directory: Path) -> Dict[str, Dict[str, str]]:
    """查找指定目录下所有被@service装饰的函数"""
    services = {}
    for file in directory.glob("*.py"):
        if file.name == "__init__.py":
            continue
            
        try:
            with open(file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                            if decorator.func.id == "service":
                                # 获取model_name参数
                                for kw in decorator.keywords:
                                    if kw.arg == "model_name":
                                        if isinstance(kw.value, ast.Constant):
                                            services[kw.value.value] = {
                                                "file": str(file),
                                                "function": node.name
                                            }
        except Exception as e:
            click.echo(f"Error parsing {file}: {e}", err=True)
    
    return services

def load_services(services_dir: str) -> Tuple[bool, List[str]]:
    """
    加载并注册服务
    
    Args:
        services_dir: 服务目录路径
    
    Returns:
        (是否成功, 已注册的服务列表)
    """
    services_path = Path(services_dir)
    if not services_path.exists():
        click.echo(f"Services directory {services_dir} not found.", err=True)
        return False, []
    
    # 将services目录添加到Python路径
    sys.path.insert(0, str(services_path.parent))
    
    # 导入所有服务
    for file in services_path.glob("*.py"):
        if file.name != "__init__.py":
            module_name = f"{services_path.name}.{file.stem}"
            try:
                __import__(module_name)
            except Exception as e:
                click.echo(f"Error importing {module_name}: {e}", err=True)
    
    # 获取已注册的服务
    services = ServiceRegistry.list_services()
    if not services:
        click.echo("No services found. Please create services in the services directory.")
        return False, []
    
    return True, services

def display_services(services: List[str]):
    """显示服务列表"""
    click.echo("Available services:")
    for service in services:
        click.echo(f"  - {service}")

@click.group()
def cli():
    """EasyMaaS - A lightweight framework for wrapping Python code as OpenAI-compatible services"""
    pass

@cli.command()
def init():
    """初始化EasyMaaS项目"""
    # 创建.easymaas目录
    easymaas_dir = Path(".easymaas")
    if not easymaas_dir.exists():
        easymaas_dir.mkdir()
        click.echo("Created .easymaas directory")
    
    # 创建services目录
    if click.confirm("Do you want to create a example service?", default=False):
        services_dir = Path("services")
        if not services_dir.exists():
            services_dir.mkdir()
            click.echo("Created services directory")
    
        # 创建示例服务文件
        example_service = services_dir / "example_service.py"
        if not example_service.exists():
            example_service.write_text("""from easymaas import service

@service(model_name="example-model", description="An example service", map_request=True, map_response=True)
def example_service(model:str, content: str):
    return f"{model} received your message: {content}."
""")
            click.echo("Created example service in services/example_service.py")
    
    click.echo("Project initialized successfully!")

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--services-dir", default="services", help="Directory containing service files")
def start(host: str, port: int, reload: bool, services_dir: str):
    """启动EasyMaaS服务"""
    # 清理已停止的部署
    deployment_manager = DeploymentManager()
    deployment_manager.cleanup_dead_deployments()
    
    # 检查端口是否被占用
    for deployment in deployment_manager.list_deployments():
        if deployment.port == port:
            click.echo(f"Port {port} is already in use by another deployment.", err=True)
            sys.exit(1)
    
    success, services = load_services(services_dir)
    if not success:
        sys.exit(1)
    
    display_services(services)
    
    # 确认是否继续
    if not click.confirm("Do you want to start the server with these services?", default=True):
        click.echo("Server startup cancelled.")
        sys.exit(0)
    
    # 创建部署信息
    deployment_info = DeploymentInfo(
        services_dir=services_dir,
        host=host,
        port=port,
        pid=os.getpid(),
        start_time=time.time(),
        services=[
            ServiceInfo(
                model_name=model_name,
                function_name=ServiceRegistry.get_service(model_name).__name__,
                file_path=str(Path(services_dir) / f"{model_name}.py")
            )
            for model_name in services
        ]
    )
    
    # 保存部署信息
    deployment_manager.save_deployment(deployment_info)
    
    # 启动服务器
    click.echo(f"Starting server on {host}:{port}")
    try:
        uvicorn.run(
            "easymaas.server.app:app",
            host=host,
            port=port,
            reload=reload
        )
    finally:
        # 服务器停止时删除部署信息
        deployment_manager.delete_deployment(services_dir)

@cli.command()
@click.option("--services-dir", default="services", help="Directory containing service files")
def list_services(services_dir: str):
    """列出指定目录下所有可用的服务"""
    success, services = load_services(services_dir)
    if not success:
        return
    
    display_services(services)

@cli.command()
def status():
    """查看当前部署的服务状态"""
    deployment_manager = DeploymentManager()
    deployment_manager.cleanup_dead_deployments()
    
    deployments = deployment_manager.list_deployments()
    if not deployments:
        click.echo("No active deployments found.")
        return
    
    click.echo("Active deployments:")
    for deployment in deployments:
        try:
            process = psutil.Process(deployment.pid)
            uptime = time.time() - deployment.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            
            click.echo(f"\nDeployment: {deployment.services_dir}")
            click.echo(f"  Host: {deployment.host}")
            click.echo(f"  Port: {deployment.port}")
            click.echo(f"  PID: {deployment.pid}")
            click.echo(f"  Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
            click.echo(f"  Services:")
            for service in deployment.services:
                click.echo(f"    - {service.model_name} ({service.function_name})")
        except psutil.NoSuchProcess:
            click.echo(f"\nDeployment: {deployment.services_dir} (DEAD)")
            deployment_manager.delete_deployment(deployment.services_dir)

if __name__ == "__main__":
    cli() 