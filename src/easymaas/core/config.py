from typing import List, Dict, Optional
from pydantic import BaseModel
from pathlib import Path
import yaml
import os
import time
import psutil
import hashlib  # 添加 hashlib 模块

class ServiceInfo(BaseModel):
    """服务信息"""
    model_name: str
    function_name: str
    file_path: str

class DeploymentInfo(BaseModel):
    """部署信息"""
    services_dir: str
    host: str
    port: int
    pid: int
    start_time: float
    services: List[ServiceInfo]

class DeploymentManager:
    """部署管理器"""
    def __init__(self):
        self.easymaas_dir = Path(".easymaas")
        if not self.easymaas_dir.exists():
            self.easymaas_dir.mkdir()
    
    def get_deployment_file(self, services_dir: str) -> Path:
        """获取部署信息文件路径"""
        # 使用服务目录的绝对路径的MD5哈希作为文件名，确保跨会话一致性
        abs_path = str(Path(services_dir).absolute())
        dir_hash = hashlib.md5(abs_path.encode()).hexdigest()[:10]  # 取前10位足够区分
        return self.easymaas_dir / f"deployment_{dir_hash}.yaml"
    
    def save_deployment(self, info: DeploymentInfo):
        """保存部署信息"""
        deployment_file = self.get_deployment_file(info.services_dir)
        with open(deployment_file, "w", encoding="utf-8") as f:
            yaml.dump(info.model_dump(), f)
    
    def load_deployment(self, services_dir: str) -> Optional[DeploymentInfo]:
        """加载部署信息"""
        deployment_file = self.get_deployment_file(services_dir)
        if not deployment_file.exists():
            return None
        
        with open(deployment_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return DeploymentInfo(**data)
    
    def delete_deployment(self, services_dir: str):
        """删除部署信息"""
        deployment_file = self.get_deployment_file(services_dir)
        if deployment_file.exists():
            deployment_file.unlink()
    
    def list_deployments(self) -> List[DeploymentInfo]:
        """列出所有部署信息"""
        deployments = []
        for file in self.easymaas_dir.glob("deployment_*.yaml"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    deployments.append(DeploymentInfo(**data))
            except Exception:
                # 如果文件损坏，删除它
                file.unlink()
        return deployments
    
    def cleanup_dead_deployments(self):
        """清理已停止的部署"""
        for deployment in self.list_deployments():
            try:
                process = psutil.Process(deployment.pid)
                if not process.is_running():
                    self.delete_deployment(deployment.services_dir)
            except psutil.NoSuchProcess:
                self.delete_deployment(deployment.services_dir)