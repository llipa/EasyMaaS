from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import inspect
from ..core.models import ChatCompletionRequest, ChatCompletionResponse, StreamChatCompletionResponse
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

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    """处理聊天完成请求"""
    service = ServiceRegistry.get_service(request.model)
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Model {request.model} not found. Available models: {', '.join(ServiceRegistry.list_services())}"
        )
    
    # 根据服务函数类型决定是否使用await
    if inspect.iscoroutinefunction(service):
        return await service(request)
    else:
        return service(request)

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