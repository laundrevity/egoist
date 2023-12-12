from typing import Optional, List, Dict
from pydantic import BaseModel


class FunctionCall(BaseModel):
    name: Optional[str] = None
    arguments: Optional[str] = None


class ToolCall(BaseModel):
    index: Optional[int]
    id: Optional[str] = None
    type: Optional[str] = None
    function: Optional[FunctionCall]


class Delta(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


class Choice(BaseModel):
    index: int
    delta: Optional[Delta]
    finish_reason: Optional[str]


class StreamChunk(BaseModel):
    id: str
    object: str
    created: int
    model: str
    system_fingerprint: str
    choices: List[Choice]


class Message(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
