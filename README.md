# OmniCare Customer Assistant

A small full-stack prototype for OmniCare Financial. Policyholders can ask about coverage or manage a claim. The Streamlit chat calls a FastAPI backend. A LangGraph agent answers from the policy document, with citations, and uses tools to look up or file claims.

## Architecture

```
Browser
   |
   |  http://localhost:8501
   v
Streamlit chat
   |
   |  POST /api/v1/chat
   v
FastAPI
   |
   v
LangGraph agent
   |                         |
   | retrieve_policy         | get_claim_status / submit_claim
   v                         v
Chroma (local)               data/mock_claims.json
data/sample_policy.md
```

Coverage answers come only from retrieved policy sections. Claim facts come only from the claims file. Prompt-injection attempts are refused before the model runs.

## Why LangGraph

The assistant is one agent with three tools: `retrieve_policy`, `get_claim_status`, and `submit_claim`. LangGraph makes that tool loop explicit and easy to test with a fake model. LangChain is only the chat-model layer (`ChatGroq` or `ChatOllama`). CrewAI, ADK, LiveKit, and Pipecat are a poor fit for a single request/response agent with no voice channel.

## Run

Requires Docker and a free Groq API key.

```bash
cp .env.example .env
```

Put your key in `GROQ_API_KEY`. The default model is `openai/gpt-oss-120b`.

```bash
docker compose up --build
```

- Chat UI: http://localhost:8501
- API: http://localhost:8000

To use local Ollama instead of Groq, set `LLM_PROVIDER=ollama` in `.env` and start the extra service:

```bash
docker compose --profile ollama up --build
```

## Sample requests

Health:

```bash
curl -s http://localhost:8000/api/v1/health
```

Coverage question:

```bash
curl -s -X POST http://localhost:8000/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"usr_123","message":"Does my policy cover sudden pipe bursts, and what is the deductible?"}'
```

Claim status:

```bash
curl -s -X POST http://localhost:8000/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"usr_123","message":"What is the status of claim CLM-8821?"}'
```

File a claim:

```bash
curl -s -X POST http://localhost:8000/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"usr_123","message":"File a water damage claim for policy POL-1092 for 400 dollars. A kitchen pipe burst."}'
```

`POST /api/v1/chat` accepts `{ "user_id", "message" }` and returns `{ "response", "sources", "tool_calls" }`.

## Tests

Pytest covers the health and chat endpoints, claim tools, RAG citations, injection refusal, and the agent tool loop. The suite does not call Groq.

```bash
docker compose run --rm --no-deps \
  -v "./backend/tests:/app/tests" \
  -v "./backend/pytest.ini:/app/pytest.ini" \
  backend pytest
```

## Walkthrough

Open http://localhost:8501. The sidebar user id defaults to `usr_123`.

A coverage question is answered from the policy and cites the section. A claim question returns the status stored in `data/mock_claims.json`.

![Coverage answer with a policy citation, then claim CLM-8821 marked Approved](screenshot2.png)

Opening the tool call shows `get_claim_status` for `CLM-8821`. A message that tries to override the instructions is refused, with no sources and no tool call.

![Claim tool result and a refused prompt-injection message](screenshot1.png)
