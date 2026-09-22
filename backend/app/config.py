import os
from pathlib import Path


def policy_path() -> Path:
    return Path(os.environ.get("POLICY_PATH", "/data/sample_policy.md"))


def claims_path() -> Path:
    return Path(os.environ.get("CLAIMS_PATH", "/data/mock_claims.json"))


def chroma_path() -> Path:
    return Path(os.environ.get("CHROMA_PATH", "/app/chroma"))


def llm_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "groq").strip().lower()


def groq_api_key() -> str:
    return os.environ.get("GROQ_API_KEY", "")


def groq_model() -> str:
    return os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")


def ollama_base_url() -> str:
    return os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


def ollama_model() -> str:
    return os.environ.get("OLLAMA_MODEL", "llama3.2")
