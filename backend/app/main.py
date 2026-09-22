from fastapi import FastAPI

from app.chat import handle_chat
from app.schemas import ChatRequest, ChatResponse, HealthResponse

app = FastAPI(title="OmniCare Customer Assistant")


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="healthy")


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    return handle_chat(body.user_id, body.message)
