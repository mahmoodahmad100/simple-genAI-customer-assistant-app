import re

import chromadb
from chromadb.utils import embedding_functions

from app.config import chroma_path, policy_path

_collections: dict[tuple[str, str], chromadb.Collection] = {}
_embedding = embedding_functions.DefaultEmbeddingFunction()


def split_policy(markdown: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    for part in re.split(r"\n(?=## )", markdown.strip()):
        if not part.startswith("## "):
            continue
        title_line, _, body = part.partition("\n")
        title = title_line.removeprefix("## ").strip()
        text = body.strip()
        if title and text:
            sections.append({"section": title, "text": text})
    return sections


def citation_for(section: str) -> str:
    return f"sample_policy.md — {section}"


def ingest_policy() -> chromadb.Collection:
    source = policy_path()
    persist = chroma_path()
    key = (str(source), str(persist))
    cached = _collections.get(key)
    if cached is not None:
        return cached

    persist.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist))
    collection = client.get_or_create_collection(
        name="policy",
        embedding_function=_embedding,
    )
    if collection.count() == 0:
        sections = split_policy(source.read_text(encoding="utf-8"))
        if not sections:
            raise ValueError(f"No policy sections found in {source}")
        collection.add(
            ids=[section["section"] for section in sections],
            documents=[section["text"] for section in sections],
            metadatas=[{"section": section["section"]} for section in sections],
        )
    _collections[key] = collection
    return collection


def retrieve_policy(query: str) -> dict[str, str | None]:
    collection = ingest_policy()
    if collection.count() == 0:
        return {
            "citation": None,
            "section": None,
            "text": "",
            "message": "No relevant policy section was found.",
        }

    found = collection.query(query_texts=[query], n_results=1)
    documents = found.get("documents") or [[]]
    metadatas = found.get("metadatas") or [[]]
    if not documents[0]:
        return {
            "citation": None,
            "section": None,
            "text": "",
            "message": "No relevant policy section was found.",
        }

    section = str(metadatas[0][0]["section"])
    return {
        "citation": citation_for(section),
        "section": section,
        "text": documents[0][0],
        "message": None,
    }
