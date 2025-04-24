import functools
import inspect
import uuid
import logging
import json
from typing import Callable, Any, Dict, List, Optional, Union, Set, Type, Tuple
from fastapi.responses import StreamingResponse

# 导入响应模板
from ..config.templates import get_default_response, get_stream_response

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EasyMaaS")

class ServiceRegistry:
    _instance = None
    _services: Dict[str, Callable] = {}
    _service_configs: Dict[str, Dict[str, Any]] = {}  # 存储服务配置
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, model_name: str, func: Callable, map_request: bool = False, map_response: bool = False, supports_streaming: bool = False):
        # 存储服务配置
        cls._service_configs[model_name] = {
            "map_request": map_request,
            "map_response": map_response,
            "supports_streaming": supports_streaming
        }
    
        # 创建包装函数
        @functools.wraps(func)
        async def wrapper(request_data):
            # 检查是否请求流式输出但函数不支持
            stream = request_data.get("stream", False)
            if stream and not supports_streaming and map_response:
                error_msg = f"\n{'='*80}\n⚠️ Warning: Model '{model_name}' does not support streaming responses\n{'='*80}"
                logger.warning(error_msg)
                return {
                    "error": {
                        "message": f"Model '{model_name}' does not support streaming responses",
                        "type": "invalid_request_error",
                        "param": "stream",
                        "code": "streaming_not_supported"
                    }
                }
            
            # 根据配置决定是否映射请求
            if map_request:
                # 映射请求参数到函数参数
                params = _map_request_to_params(func, request_data)
            else:
                # 获取函数的第一个参数名
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                
                if not param_names:
                    error_msg = f"\n{'='*80}\n❌ Error: Function '{func.__name__}' must have at least one parameter to receive the request\n{'='*80}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                    
                # 使用第一个参数名作为键
                first_param_name = param_names[0]
                params = {first_param_name: request_data}
            
            # 调用原始函数
            try:
                result = await func(**params) if inspect.iscoroutinefunction(func) else func(**params)
            
                # 根据配置决定是否映射响应
                if map_response:
                    # 处理响应
                    model_name = request_data.get("model", "EasyMaaS")
                    stream = request_data.get("stream", False)
                    if stream and supports_streaming:
                        # 处理流式响应
                        return await _create_stream_response(func, request_data, result, model_name)
                    return _create_response(func, request_data, result, model_name)
                else:
                    # 直接返回原始结果
                    return result
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
    def get_service_config(cls, model_name: str) -> Dict[str, Any]:
        return cls._service_configs.get(model_name, {})

    @classmethod
    def list_services(cls) -> List[str]:
        return list(cls._services.keys())

def service(model_name: str, description: str = "", map_request: bool = False, map_response: bool = False, supports_streaming: bool = False):
    """
    将函数装饰为OpenAI兼容的服务
    
    Args:
        model_name: 模型名称
        description: 服务描述
        map_request: 是否将请求映射为OpenAI格式（默认为False）
        map_response: 是否将响应映射为OpenAI格式（默认为False）
        supports_streaming: 是否支持流式输出（默认为False）
    """
    def decorator(func: Callable):
        # 注册服务
        ServiceRegistry.register(model_name, func, map_request, map_response, supports_streaming)
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

def _map_request_to_params(func: Callable, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用JSON递归映射请求参数到函数参数
    
    Args:
        func: 要映射的函数
        request_data: 请求数据字典
        
    Returns:
        Dict[str, Any]: 映射后的参数字典
    """
    # 获取函数参数
    sig = inspect.signature(func)
    params = {}
    
    # 记录未映射的参数
    unmapped_params = []
    
    # 处理参数映射
    for param_name, param in sig.parameters.items():
        # 在请求JSON中查找参数
        found, value = _find_key_in_json(request_data, param_name)
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

def _create_response(func: Callable, request_data: Dict[str, Any], result: Any, model_name: str = "EasyMaaS") -> Dict[str, Any]:
    """
    使用JSON递归映射创建标准响应
    
    Args:
        func: 函数
        request_data: 请求数据
        result: 函数返回值
        model_name: 模型名称
        
    Returns:
        Dict[str, Any]: 响应对象
    """
    # 创建默认响应
    response = get_default_response(model_name)
    
    # 计算提示tokens (如果需要)
    messages = request_data.get("messages", [])
    prompt_tokens = sum(len(msg.get("content", "").split()) for msg in messages if isinstance(msg, dict))
    response["usage"]["prompt_tokens"] = prompt_tokens
    
    # 处理不同类型的返回值
    if result is None:
        # 如果返回值为None，使用默认响应
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' returned None, using default response 'Hello from EasyMaaS'\n{'='*80}")
        return response
    
    elif isinstance(result, str):
        # 如果返回值为字符串，将其作为消息内容
        response["choices"][0]["message"]["content"] = result
        # 计算completion_tokens
        response["usage"]["completion_tokens"] = len(result.split())
        response["usage"]["total_tokens"] = response["usage"]["prompt_tokens"] + response["usage"]["completion_tokens"]
    
    elif isinstance(result, list):
        # 不支持列表返回值
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' does not support list type return values, using default response 'Hello from EasyMaaS'\n{'='*80}")
        return response
    
    elif isinstance(result, dict):
        # 如果返回值为字典，进行递归映射
        for key, value in result.items():
            # 尝试更新响应JSON
            if not _update_json_with_key(response, key, value):
                logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' could not find a matching response key for return value {key}\n{'='*80}")
    
    else:
        # 其他类型，转换为字符串
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' has an unsupported return value type {type(result).__name__}, converting to string\n{'='*80}")
        return _create_response(func, request_data, str(result), model_name)
    
    return response

async def _create_stream_response(func: Callable, request_data: Dict[str, Any], result: Any, model_name: str = "EasyMaaS"):
    """
    处理流式响应
    
    Args:
        func: 函数
        request_data: 请求数据
        result: 函数返回值（生成器）
        model_name: 模型名称
        
    Returns:
        StreamingResponse: 流式响应对象
    """
    # 创建响应ID（所有块共享同一个ID）
    response_id = str(uuid.uuid4())
    
    async def stream_generator():
        # 处理不同类型的生成器
        try:
            if inspect.isasyncgen(result):
                # 异步生成器
                async for chunk in result:
                    processed_chunk = _process_stream_chunk(chunk, response_id, model_name)
                    yield f"data: {json.dumps(processed_chunk)}\n\n"
            elif inspect.isgenerator(result):
                # 同步生成器
                for chunk in result:
                    processed_chunk = _process_stream_chunk(chunk, response_id, model_name)
                    yield f"data: {json.dumps(processed_chunk)}\n\n"
            else:
                # 不是生成器，作为单个块处理
                logger.warning(f"\n{'='*80}\n⚠️ Warning: Function '{func.__name__}' is marked as supporting streaming but did not return a generator\n{'='*80}")
                processed_chunk = _process_stream_chunk(result, response_id, model_name)
                yield f"data: {json.dumps(processed_chunk)}\n\n"

        except Exception as e:
            logger.error(f"\n{'='*80}\n❌ Error in stream processing: {str(e)}\n{'='*80}")
            # 发送错误信息
            error_chunk = get_stream_response(model_name)
            error_chunk["id"] = response_id
            error_chunk["choices"][0]["delta"]["content"] = f"Error: {str(e)}"
            error_chunk["choices"][0]["finish_reason"] = "error"
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no"
        }
    )

def _process_stream_chunk(chunk: Any, response_id: str, model_name: str) -> Dict[str, Any]:
    """
    处理流式响应的单个块
    
    Args:
        chunk: 块数据
        response_id: 响应ID
        model_name: 模型名称
        
    Returns:
        Dict[str, Any]: 处理后的块
    """
    # 获取基本响应模板
    response = get_stream_response(model_name)
    response["id"] = response_id
    
    # 处理不同类型的块
    if chunk is None:
        # 如果块为None，使用空内容
        return response
    
    elif isinstance(chunk, str):
        # 如果块为字符串，将其作为消息内容
        response["choices"][0]["delta"]["content"] = chunk
    
    elif isinstance(chunk, dict):
        # 如果块为字典，进行递归映射
        for key, value in chunk.items():
            # 尝试更新响应JSON
            if not _update_json_with_key(response, key, value):
                logger.warning(f"\n{'='*80}\n⚠️ Warning: Could not find a matching response key for stream chunk value {key}\n{'='*80}")
    
    else:
        # 其他类型，转换为字符串
        logger.warning(f"\n{'='*80}\n⚠️ Warning: Unsupported stream chunk type {type(chunk).__name__}, converting to string\n{'='*80}")
        response["choices"][0]["delta"]["content"] = str(chunk)
    
    return response
