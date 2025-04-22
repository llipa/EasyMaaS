from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, model_validator
import time
import uuid

class Message(BaseModel):
    role: str = "assistant"
    content: str = "Hello from EasyMaaS"
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str = "EasyMaaS"
    messages: List[Message] = Field(default_factory=lambda: [Message()])
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

class Choice(BaseModel):
    index: int = 0
    message: Message = Field(default_factory=Message)
    finish_reason: Optional[str] = "stop"

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = "EasyMaaS"
    choices: List[Choice] = Field(default_factory=lambda: [Choice()])
    usage: Usage = Field(default_factory=Usage)
    
    @model_validator(mode="after")
    def calculate_tokens(self):
        """计算completion_tokens和total_tokens"""
        # 如果已经设置了completion_tokens，则计算total_tokens
        if self.usage.completion_tokens == 0 and self.choices and self.choices[0].message.content:
            # 计算completion_tokens
            self.usage.completion_tokens = len(self.choices[0].message.content.split())
        
            # 计算total_tokens
            self.usage.total_tokens = self.usage.prompt_tokens + self.usage.completion_tokens
            
        return self

class StreamChoice(BaseModel):
    index: int = 0
    delta: Message = Field(default_factory=Message)
    finish_reason: Optional[str] = None

class StreamChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = "EasyMaaS"
    choices: List[StreamChoice] = Field(default_factory=lambda: [StreamChoice()])