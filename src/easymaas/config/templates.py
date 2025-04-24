"""
EasyMaaS 响应模板配置
提供标准的OpenAI兼容响应模板
"""
import uuid
import time
from typing import Dict, Any, List

def get_default_response(model_name: str = "EasyMaaS") -> Dict[str, Any]:
    """
    获取默认的响应模板
    
    Args:
        model_name: 模型名称
        
    Returns:
        Dict[str, Any]: 默认响应对象
    """
    return {
        "id": str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello from EasyMaaS"
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

def get_stream_response(model_name: str = "EasyMaaS") -> Dict[str, Any]:
    """
    获取流式响应的模板
    
    Args:
        model_name: 模型名称
        
    Returns:
        Dict[str, Any]: 流式响应对象
    """
    return {
        "id": str(uuid.uuid4()),
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "delta": {
                    "role": "assistant",
                    "content": ""
                },
                "finish_reason": None
            }
        ]
    }
