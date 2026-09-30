from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class IngestResponse(BaseModel):
    filename: str
    chunks_added: int


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    reply: str


class MultiAgentRequest(BaseModel):
    message: str


class MultiAgentResponse(BaseModel):
    reply: str