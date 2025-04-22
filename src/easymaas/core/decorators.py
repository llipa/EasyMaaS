import functools
import inspect
import time
import uuid
import logging
import json
from typing import Callable, Any, Dict, List, Optional, Union, Set, Type, Tuple
from pydantic import BaseModel
from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Message,
    Choice,
    Usage,
    StreamChatCompletionResponse,
    StreamChoice
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EasyMaaS")

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
            # 映射请求参数到函数参数
            params = _map_request_to_params(func, request)

            # 调用原始函数
            try:
                result = await func(**params) if inspect.iscoroutinefunction(func) else func(**params)
                
                # 处理响应
                if request.stream:
                    return _create_stream_response(func, request, result)
                return _create_response(func, request, result)
            except Exception as e:
                error_msg = f"\n{'='*80}\n❌ Error: Function '{func.__name__}' execution failed: {str(e)}\n{'='*80}"
                logger.error(error_msg)
                raise
        
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

def _find_key_in_json(json_obj: Any, target_key: str) -> Tuple[bool, Any]:
    """
    在JSON对象中递归查找指定的键
    
    Args:
        json_obj: JSON对象
        target_key: 目标键名
        
    Returns:
        Tuple[bool, Any]: (是否找到, 对应的值)
    """
    # 如果是字典，直接检查键
    if isinstance(json_obj, dict):
        # 直接匹配
        if target_key in json_obj:
            return True, json_obj[target_key]
        
        # 递归检查每个值
        for key, value in json_obj.items():
            found, result = _find_key_in_json(value, target_key)
            if found:
                return True, result
    
    # 如果是列表，检查最后一个元素（如果是字典）
    elif isinstance(json_obj, list) and json_obj:
        last_item = json_obj[-1]
        # 只处理列表中的字典元素
        if isinstance(last_item, dict):
            return _find_key_in_json(last_item, target_key)
    
    # 未找到
    return False, None

def _map_request_to_params(func: Callable, request: ChatCompletionRequest) -> Dict[str, Any]:
    """
    使用JSON递归映射请求参数到函数参数
    
    Args:
        func: 要映射的函数
        request: 请求对象
        
    Returns:
        Dict[str, Any]: 映射后的参数字典
    """
    # 获取函数参数
    sig = inspect.signature(func)
    params = {}
    
    # 记录未映射的参数
    unmapped_params = []
    
    # 将请求转换为JSON
    request_json = request.model_dump()
    
    # 处理参数映射
    for param_name, param in sig.parameters.items():
        if param_name == "request":
            # 特殊处理完整请求对象
            params[param_name] = request
        else:
            # 在请求JSON中查找参数
            found, value = _find_key_in_json(request_json, param_name)
            if found:
                params[param_name] = value
            else:
                # 无法映射的参数设置为None
                params[param_name] = None
                unmapped_params.append(param_name)
    
    # 如果有未映射的参数，发出警告
    if unmapped_params:
        warning_msg = f"\n{'='*80}\n⚠️ Warning: The following parameters of function '{func.__name__}' could not be mapped to the request and have been set to None: {', '.join(unmapped_params)}\n"
        logger.warning(warning_msg)
    
    return params

def _update_json_with_key(json_obj: Dict[str, Any], target_key: str, new_value: Any) -> bool:
    """
    递归更新JSON对象中指定键的值
    
    Args:
        json_obj: JSON对象
        target_key: 目标键名
        new_value: 新值
        
    Returns:
        bool: 是否成功更新
    """
    # 直接匹配
    if target_key in json_obj:
        json_obj[target_key] = new_value
        return True
    
    # 递归检查每个值
    for key, value in json_obj.items():
        # 如果值是字典，递归处理
        if isinstance(value, dict):
            if _update_json_with_key(value, target_key, new_value):
                return True
        # 如果值是列表且元素为字典，处理最后一个元素
        elif isinstance(value, list) and value:
            last_item = value[-1]
            if isinstance(last_item, dict):
                if _update_json_with_key(last_item, target_key, new_value):
                    return True
    
    # 未找到
    return False

def _create_response(func: Callable, request: ChatCompletionRequest, result: Any) -> ChatCompletionResponse:
    """
    使用JSON递归映射创建标准响应
    
    Args:
        request: 请求对象
        result: 函数返回值
        
    Returns:
        ChatCompletionResponse: 响应对象
    """
    # 创建默认响应并转换为JSON
    default_response = ChatCompletionResponse(model=request.model)
    response_json = default_response.model_dump()
    
    # 计算提示tokens (如果需要)
    prompt_tokens = sum(len(msg.content.split()) for msg in request.messages)
    response_json["usage"]["prompt_tokens"] = prompt_tokens
    
    # 处理不同类型的返回值
    if result is None:
        # 如果返回值为None，使用默认响应
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' returned None, using default response 'Hello from EasyMaaS'\n{'='*80}")
        return default_response
    
    elif isinstance(result, str):
        # 如果返回值为字符串，将其作为消息内容
        response_json["choices"][0]["message"]["content"] = result
    
    elif isinstance(result, list):
        # 不支持列表返回值
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' does not support list type return values, using default response 'Hello from EasyMaaS'\n{'='*80}")
        return default_response
    
    elif isinstance(result, dict):
        # 如果返回值为字典，进行递归映射
        for key, value in result.items():
            # 尝试更新响应JSON
            if not _update_json_with_key(response_json, key, value):
                logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' could not find a matching response key for return value {key}\n{'='*80}")
    
    else:
        # 其他类型，转换为字符串
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' has an unsupported return value type {type(result).__name__}, converting to string\n{'='*80}")
        return _create_response(request, str(result))
    
    # 使用更新后的JSON创建响应对象
    return ChatCompletionResponse(**response_json)

def _create_stream_response(func: Callable, request: ChatCompletionRequest, result: Any) -> StreamChatCompletionResponse:
    """
    使用JSON递归映射创建流式响应
    
    Args:
        request: 请求对象
        result: 函数返回值
        
    Returns:
        StreamChatCompletionResponse: 流式响应对象
    """
    # 创建默认响应并转换为JSON
    default_response = StreamChatCompletionResponse(model=request.model)
    response_json = default_response.model_dump()
    
    # 处理不同类型的返回值
    if result is None:
        # 如果返回值为None，使用默认响应
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' returned None, using default stream response 'Hello from EasyMaaS'\n{'='*80}")
        return default_response
    
    elif isinstance(result, str):
        # 如果返回值为字符串，将其作为消息内容
        response_json["choices"][0]["delta"]["content"] = result
    
    elif isinstance(result, list):
        # 不支持列表返回值
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' does not support list type stream return values, using default response 'Hello from EasyMaaS'\n{'='*80}")
        return default_response
    
    elif isinstance(result, dict):
        # 如果返回值为字典，进行递归映射
        for key, value in result.items():
            # 尝试更新响应JSON
            if not _update_json_with_key(response_json, key, value):
                logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' could not find a matching response key for return value {key}\n{'='*80}")
    
    else:
        # 其他类型，转换为字符串
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' has an unsupported stream return value type {type(result).__name__}, converting to string\n{'='*80}")
        return _create_stream_response(request, str(result))
    
    # 使用更新后的JSON创建响应对象
    return StreamChatCompletionResponse(**response_json)