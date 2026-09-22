import json
import re
import threading
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.config import claims_path

_lock = threading.Lock()


class ClaimIdInput(BaseModel):
    model_config = ConfigDict(strict=True)

    claim_id: str

    @field_validator("claim_id")
    @classmethod
    def claim_id_pattern(cls, value: str) -> str:
        stripped = value.strip()
        if not re.fullmatch(r"CLM-\d+", stripped):
            raise ValueError("claim_id must match CLM-<digits>")
        return stripped


class SubmitClaimInput(BaseModel):
    model_config = ConfigDict(strict=True)

    policy_number: str
    claim_type: str = Field(min_length=1, max_length=80)
    amount: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=2000)

    @field_validator("amount", mode="before")
    @classmethod
    def amount_must_be_number(cls, value: Any) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("amount must be a number")
        return float(value)

    @field_validator("policy_number")
    @classmethod
    def policy_number_pattern(cls, value: str) -> str:
        stripped = value.strip()
        if not re.fullmatch(r"POL-\d+", stripped):
            raise ValueError("policy_number must match POL-<digits>")
        return stripped

    @field_validator("claim_type", "description")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped


def _validation_error(exc: ValidationError) -> dict[str, Any]:
    return {"error": exc.errors()[0]["msg"]}


def _read_claims() -> list[dict[str, Any]]:
    path = claims_path()
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("claims file must be a JSON list")
    return payload


def _write_claims(claims: list[dict[str, Any]]) -> None:
    path = claims_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(claims, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _next_claim_id(claims: list[dict[str, Any]]) -> str:
    numbers = [
        int(match.group(1))
        for claim in claims
        if (match := re.fullmatch(r"CLM-(\d+)", str(claim.get("claim_id", ""))))
    ]
    return f"CLM-{max(numbers, default=1000) + 1}"


def get_claim_status(claim_id: str) -> dict[str, Any]:
    try:
        parsed = ClaimIdInput(claim_id=claim_id)
    except ValidationError as exc:
        return _validation_error(exc)

    with _lock:
        for claim in _read_claims():
            if claim.get("claim_id") == parsed.claim_id:
                return {"found": True, "claim": claim}
    return {
        "found": False,
        "claim_id": parsed.claim_id,
        "message": "No claim found for this id.",
    }


def submit_claim(
    policy_number: str,
    claim_type: str,
    amount: Any,
    description: str,
) -> dict[str, Any]:
    try:
        parsed = SubmitClaimInput(
            policy_number=policy_number,
            claim_type=claim_type,
            amount=amount,
            description=description,
        )
    except ValidationError as exc:
        return _validation_error(exc)

    with _lock:
        claims = _read_claims()
        claim_id = _next_claim_id(claims)
        record = {
            "claim_id": claim_id,
            "policy_number": parsed.policy_number,
            "claim_type": parsed.claim_type,
            "status": "Submitted",
            "amount": parsed.amount,
            "description": parsed.description,
        }
        claims.append(record)
        _write_claims(claims)
    return {
        "claim_id": claim_id,
        "status": "Submitted",
        "message": "Claim submitted.",
    }
