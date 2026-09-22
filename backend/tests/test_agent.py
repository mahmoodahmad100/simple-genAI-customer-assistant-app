import json
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage

from app.agent.graph import run_agent

SEED = [
    {
        "claim_id": "CLM-8821",
        "policy_number": "POL-1092",
        "claim_type": "Water Damage",
        "status": "Approved",
        "amount": 3500.00,
    }
]


class ScriptedModel:
    def __init__(self, responses: list[AIMessage]) -> None:
        self._responses = list(responses)

    def bind_tools(self, tools: list[object]) -> "ScriptedModel":
        return self

    def invoke(self, messages: list[object], **_kwargs: object) -> AIMessage:
        if not self._responses:
            raise AssertionError("scripted model ran out of responses")
        return self._responses.pop(0)


def test_graph_looks_up_claim_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    claims = tmp_path / "mock_claims.json"
    claims.write_text(json.dumps(SEED), encoding="utf-8")
    monkeypatch.setenv("CLAIMS_PATH", str(claims))
    model = ScriptedModel(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_claim_status",
                        "args": {"claim_id": "CLM-8821"},
                        "id": "call-1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="Claim CLM-8821 is Approved."),
        ]
    )

    result = run_agent("What is the status of claim CLM-8821?", model=model)

    assert result.response == "Claim CLM-8821 is Approved."
    assert result.tool_calls[0]["name"] == "get_claim_status"
    assert result.tool_calls[0]["arguments"] == {"claim_id": "CLM-8821"}
    assert "Approved" in result.tool_calls[0]["result"]


def test_graph_cites_retrieved_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLICY_PATH", "/data/sample_policy.md")
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    model = ScriptedModel(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "retrieve_policy",
                        "args": {"query": "jewelry appraisal limit"},
                        "id": "call-2",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="Jewelry is covered up to the personal property limit."),
        ]
    )

    result = run_agent("Does the policy cover jewelry?", model=model)

    assert result.sources == [
        "sample_policy.md — Section 2: Personal Property Protection"
    ]
    assert result.tool_calls[0]["name"] == "retrieve_policy"
