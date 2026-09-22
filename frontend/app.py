import os

import httpx
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://backend:8000").rstrip("/")

st.set_page_config(page_title="OmniCare Customer Assistant")
st.title("OmniCare Customer Assistant")

if "user_id" not in st.session_state:
    st.session_state.user_id = "usr_123"
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.session_state.user_id = st.text_input("User ID", value=st.session_state.user_id).strip()


def render_assistant(message: dict) -> None:
    st.markdown(message["content"])
    sources = message.get("sources") or []
    if sources:
        st.caption("Sources")
        for source in sources:
            st.markdown(f"- {source}")
    tool_calls = message.get("tool_calls") or []
    if tool_calls:
        with st.expander("Tool calls"):
            for call in tool_calls:
                st.markdown(f"**{call.get('name', 'tool')}**")
                st.json(
                    {
                        "arguments": call.get("arguments"),
                        "result": call.get("result"),
                    }
                )


def ask(user_id: str, message: str) -> dict:
    try:
        response = httpx.post(
            f"{API_BASE_URL}/api/v1/chat",
            json={"user_id": user_id, "message": message},
            timeout=60.0,
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        return {
            "role": "assistant",
            "content": f"The assistant API could not answer: {exc}",
            "sources": [],
            "tool_calls": [],
        }
    return {
        "role": "assistant",
        "content": payload.get("response") or "",
        "sources": payload.get("sources") or [],
        "tool_calls": payload.get("tool_calls") or [],
    }


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            render_assistant(message)
        else:
            st.markdown(message["content"])

prompt = st.chat_input("Ask about coverage or a claim")
if prompt:
    user_id = st.session_state.user_id or "usr_123"
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    assistant = ask(user_id, prompt)
    st.session_state.messages.append(assistant)
    with st.chat_message("assistant"):
        render_assistant(assistant)
