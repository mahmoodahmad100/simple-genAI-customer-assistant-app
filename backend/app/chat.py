from app.schemas import ChatResponse


def handle_chat(user_id: str, message: str) -> ChatResponse:
    return ChatResponse(
        response=f"Received message from {user_id}.",
        sources=[],
        tool_calls=[],
    )
