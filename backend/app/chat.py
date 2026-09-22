from app.agent.graph import run_agent
from app.agent.safety import REFUSAL_RESPONSE, is_prompt_injection
from app.schemas import ChatResponse


def handle_chat(user_id: str, message: str) -> ChatResponse:
    if is_prompt_injection(message):
        return ChatResponse(response=REFUSAL_RESPONSE, sources=[], tool_calls=[])
    return run_agent(message, user_id=user_id)
