from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.chat import handle_chat
from app.rag.store import ingest_policy
from app.schemas import ChatRequest, ChatResponse, HealthResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ingest_policy()
    yield


app = FastAPI(title="OmniCare Customer Assistant", lifespan=lifespan)


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="healthy")


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    return handle_chat(body.user_id, body.message)
