from pathlib import Path

import pytest

from app.rag.store import retrieve_policy


def _isolate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLICY_PATH", "/data/sample_policy.md")
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))


def test_water_damage_cites_section_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _isolate(tmp_path, monkeypatch)

    hit = retrieve_policy("sudden pipe burst water damage deductible")

    assert hit["citation"] == "sample_policy.md — Section 1: Home Water Damage Coverage"
    assert "25,000" in hit["text"]


def test_jewelry_cites_section_2(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _isolate(tmp_path, monkeypatch)

    hit = retrieve_policy("jewelry appraisal electronics furniture")

    assert hit["citation"] == "sample_policy.md — Section 2: Personal Property Protection"
    assert "10,000" in hit["text"]
