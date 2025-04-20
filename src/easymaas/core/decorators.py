import functools
import inspect
import time
import uuid
from typing import Callable, Any, Dict, List, Optional, Union
from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Message,
    Choice,
    Usage,
    StreamChatCompletionResponse,
    StreamChoice
)

class ServiceRegistry:
    _instance = None
    _services: Dict[str, Callable] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, model_name: str, func: Callable):
        # 创建包装函数
        @functools.wraps(func)
        async def wrapper(request: ChatCompletionRequest) -> Union[ChatCompletionResponse, StreamChatCompletionResponse]:
            # 获取函数参数
            sig = inspect.signature(func)
            params = {}
            
            # 处理参数映射
            for param_name, param in sig.parameters.items():
                if param_name == "content":
                    # 获取最后一个user消息的content
                    user_messages = [msg for msg in request.messages if msg.role == "user"]
                    if user_messages:
                        params[param_name] = user_messages[-1].content
                elif param_name == "request":
                    params[param_name] = request
                else:
                    # 尝试从request中获取对应参数
                    if hasattr(request, param_name):
                        params[param_name] = getattr(request, param_name)
            
            # 调用原始函数
            result = await func(**params) if inspect.iscoroutinefunction(func) else func(**params)
            
            # 处理响应
            if request.stream:
                return _create_stream_response(request, result)
            return _create_response(request, result)
        
        # 存储包装后的函数
        cls._services[model_name] = wrapper

    @classmethod
    def get_service(cls, model_name: str) -> Optional[Callable]:
        return cls._services.get(model_name)

    @classmethod
    def list_services(cls) -> List[str]:
        return list(cls._services.keys())

def service(model_name: str, description: str = ""):
    """
    将函数装饰为OpenAI兼容的服务
    
    Args:
        model_name: 模型名称
        description: 服务描述
    """
    def decorator(func: Callable):
        # 注册服务
        ServiceRegistry.register(model_name, func)
        return func
    return decorator

def _create_response(request: ChatCompletionRequest, result: Any) -> ChatCompletionResponse:
    """创建标准响应"""
    # 生成响应ID和时间戳
    response_id = str(uuid.uuid4())
    created = int(time.time())
    
    # 处理不同类型的返回值
    if isinstance(result, dict):
        # 如果返回字典，尝试从中提取字段
        content = result.get("content", f"Hello from {request.model}")
        role = result.get("role", "assistant")
        finish_reason = result.get("finish_reason", "stop")
        prompt_tokens = result.get("prompt_tokens", 0)
        completion_tokens = result.get("completion_tokens", 0)
        total_tokens = result.get("total_tokens", prompt_tokens + completion_tokens)
    elif isinstance(result, list):
        # 如果返回列表，将其作为choices
        choices = []
        for i, item in enumerate(result):
            if isinstance(item, dict):
                content = item.get("content", str(item))
                role = item.get("role", "assistant")
                finish_reason = item.get("finish_reason", "stop")
            else:
                content = str(item)
                role = "assistant"
                finish_reason = None
            
            message = Message(role=role, content=content)
            choice = Choice(index=i, message=message, finish_reason=finish_reason)
            choices.append(choice)
        
        # 计算token使用量（简化处理）
        prompt_tokens = sum(len(msg.content.split()) for msg in request.messages)
        completion_tokens = sum(len(choice.message.content.split()) for choice in choices)
        total_tokens = prompt_tokens + completion_tokens
        
        return ChatCompletionResponse(
            id=response_id,
            created=created,
            model=request.model,
            choices=choices,
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens
            )
        )
    else:
        # 其他类型，转换为字符串作为content
        content = str(result)
        role = "assistant"
        finish_reason = None
        # 计算token使用量（简化处理）
        prompt_tokens = sum(len(msg.content.split()) for msg in request.messages)
        completion_tokens = len(content.split())
        total_tokens = prompt_tokens + completion_tokens
    
    # 创建消息和选择
    message = Message(role=role, content=content)
    choice = Choice(index=0, message=message, finish_reason=finish_reason)
    
    return ChatCompletionResponse(
        id=response_id,
        created=created,
        model=request.model,
        choices=[choice],
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )
    )

def _create_stream_response(request: ChatCompletionRequest, result: Any) -> StreamChatCompletionResponse:
    """创建流式响应"""
    # 生成响应ID和时间戳
    response_id = str(uuid.uuid4())
    created = int(time.time())
    
    # 处理不同类型的返回值
    if isinstance(result, dict):
        content = result.get("content", f"Hello from {request.model}")
    elif isinstance(result, list):
        # 对于列表，只处理第一个元素
        if result:
            item = result[0]
            if isinstance(item, dict):
                content = item.get("content", str(item))
            else:
                content = str(item)
        else:
            content = ""
    else:
        content = str(result)
    
    delta = {"content": content}
    choice = StreamChoice(index=0, delta=delta)
    
    return StreamChatCompletionResponse(
        id=response_id,
        created=created,
        model=request.model,
        choices=[choice]
    ) 