import json
from pathlib import Path

import pytest

from app.tools.claims import get_claim_status, submit_claim

SEED = [
    {
        "claim_id": "CLM-8821",
        "policy_number": "POL-1092",
        "claim_type": "Water Damage",
        "status": "Approved",
        "amount": 3500.00,
    },
    {
        "claim_id": "CLM-9014",
        "policy_number": "POL-3341",
        "claim_type": "Personal Property",
        "status": "Under Review",
        "amount": 1200.00,
    },
]


def _seed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "mock_claims.json"
    path.write_text(json.dumps(SEED), encoding="utf-8")
    monkeypatch.setenv("CLAIMS_PATH", str(path))
    return path


def test_get_claim_status_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed(tmp_path, monkeypatch)

    result = get_claim_status("CLM-8821")

    assert result["found"] is True
    assert result["claim"]["status"] == "Approved"


def test_get_claim_status_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed(tmp_path, monkeypatch)

    result = get_claim_status("CLM-9999")

    assert result["found"] is False
    assert result["claim_id"] == "CLM-9999"


def test_submit_claim_appends_and_can_be_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(tmp_path, monkeypatch)

    created = submit_claim(
        "POL-1092",
        "Water Damage",
        400,
        "Burst pipe in the kitchen",
    )

    assert created["claim_id"] == "CLM-9015"
    assert created["status"] == "Submitted"
    found = get_claim_status("CLM-9015")
    assert found["found"] is True
    assert found["claim"]["description"] == "Burst pipe in the kitchen"
    assert found["claim"]["status"] == "Submitted"


def test_submit_claim_rejects_bad_amount(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _seed(tmp_path, monkeypatch)
    before = path.read_text(encoding="utf-8")

    rejected_type = submit_claim("POL-1092", "Water Damage", "3500", "Burst pipe")
    rejected_value = submit_claim("POL-1092", "Water Damage", -5, "Burst pipe")

    assert "error" in rejected_type
    assert "error" in rejected_value
    assert path.read_text(encoding="utf-8") == before
