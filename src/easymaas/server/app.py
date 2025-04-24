from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import inspect
from ..core.decorators import ServiceRegistry

app = FastAPI(
    title="EasyMaaS",
    description="A lightweight framework for wrapping Python code as OpenAI-compatible services",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1/chat/completions")
async def chat_completion(request: Request):
    """处理聊天完成请求"""
    # 获取原始请求数据
    request_data = await request.json()
    model_name = request_data.get("model", "")
    
    service = ServiceRegistry.get_service(model_name)
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Model {model_name} not found. Available models: {', '.join(ServiceRegistry.list_services())}"
        )
    
    # 直接传递原始请求数据给服务
    response = await service(request_data) if inspect.iscoroutinefunction(service) else service(request_data)
    
    # 检查响应是否已经是StreamingResponse
    if isinstance(response, StreamingResponse):
        return response
    
    # 返回普通JSON响应
    return response

@app.get("/v1/models")
async def list_models():
    """列出所有可用的模型"""
    return {
        "object": "list",
        "data": [
            {
                "id": model_name,
                "object": "model",
                "created": 0,
                "owned_by": "organization"
            }
            for model_name in ServiceRegistry.list_services()
        ]
    }