"""Corpus loading and retrieval adapters.

The local lexical index is deterministic and is used when Chroma is not
available. Chroma can be enabled by setting CHROMA_URL and is never populated
from network scraping at request time.
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from pathlib import Path
from typing import Any

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
_SECTION_INDEX = CORPUS_DIR / "section_index.json"

_DOCUMENTS = [
    {
        "document_id": "satender-kumar-antil-v-cbi-2022",
        "title": "Satender Kumar Antil v. CBI",
        "offense_category": "general",
        "factors": ["flight_risk", "witness_influence", "general_precedent"],
        "source_url": "https://indiankanoon.org/doc/157569972/",
        "text": (
            "Satender Kumar Antil v. CBI (Supreme Court of India, 2022) discusses the "
            "need for consistent application of bail principles and directions concerning "
            "arrest and bail procedure. The judgment describes categories of offences and "
            "records that courts must consider the facts and governing law in the individual "
            "matter. This source does not determine the result of any different case."
        ),
    },
    {
        "document_id": "it-act-2000-india-code",
        "title": "Information Technology Act, 2000",
        "offense_category": "cyber_crimes",
        "factors": ["general_precedent", "witness_influence"],
        "source_url": "https://www.indiacode.nic.in/handle/123456789/1362",
        "text": (
            "The Information Technology Act, 2000 is statutory material published through "
            "India Code. Section 66C concerns dishonest or fraudulent use of another person's "
            "electronic signature, password or unique identification feature. Section 66D "
            "concerns cheating by personation using a computer resource or communication device."
        ),
    },
    {
        "document_id": "pmla-act-2002-india-code",
        "title": "Prevention of Money-Laundering Act, 2002",
        "offense_category": "economic_offences",
        "factors": ["flight_risk", "general_precedent"],
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2001",
        "text": (
            "The Prevention of Money-Laundering Act, 2002 is statutory material published "
            "through India Code. Section 3 describes the offence of money-laundering in the "
            "terms set out by the Act. Section 45 contains statutory provisions concerning "
            "offences under the Act; the statutory text does not resolve the facts or outcome "
            "of an individual proceeding."
        ),
    },
    {
        "document_id": "pocso-act-2012-india-code",
        "title": "Protection of Children from Sexual Offences Act, 2012",
        "offense_category": "crimes_against_children",
        "factors": ["witness_influence", "general_precedent"],
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2079",
        "text": (
            "The Protection of Children from Sexual Offences Act, 2012 is statutory material "
            "published through India Code. Section 4 sets out punishment for penetrative sexual "
            "assault as described in the Act. The statutory text is presented as source material "
            "and does not resolve the facts or outcome of an individual proceeding."
        ),
    },
    {
        "document_id": "sc-st-prevention-atrocities-act-1989",
        "title": "Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989",
        "offense_category": "crimes_against_sc_st",
        "factors": ["witness_influence", "general_precedent"],
        "source_url": "https://www.indiacode.nic.in/handle/123456789/1533",
        "text": (
            "The Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, "
            "1989 is statutory material published through India Code. Section 3(1)(r) addresses "
            "intentional insult or intimidation with intent to humiliate a member of a Scheduled "
            "Caste or Scheduled Tribe in a place within public view."
        ),
    },
]


def load_section_index() -> list[dict[str, str]]:
    try:
        with _SECTION_INDEX.open(encoding="utf-8") as handle:
            value = json.load(handle)
        return value if isinstance(value, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def load_corpus() -> list[dict[str, Any]]:
    return list(_DOCUMENTS)


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.casefold()) if len(token) > 2}


def _lexical_search(query: str, category: str, factors: list[str], top_k: int = 4) -> list[dict[str, Any]]:
    query_tokens = _tokens(query)
    ranked = []
    for document in load_corpus():
        doc_tokens = _tokens(" ".join([document["title"], document["text"], document["offense_category"]]))
        overlap = len(query_tokens & doc_tokens)
        category_match = document["offense_category"] == category
        factor_match = bool(set(factors) & set(document["factors"]))
        score = overlap / max(1, len(query_tokens)) + (0.55 if category_match else 0) + (0.1 if factor_match else 0)
        if category_match or overlap:
            ranked.append((score, document))
    ranked.sort(key=lambda item: (-item[0], item[1]["document_id"]))
    return [{**document, "score": min(1.0, score)} for score, document in ranked[:top_k]]


def _chroma_search(query: str, category: str, factors: list[str], top_k: int) -> list[dict[str, Any]] | None:
    """Attempt Chroma retrieval, returning None when the optional service is absent."""
    try:
        import chromadb
        from config import CHROMA_URL

        match = re.match(r"https?://([^:/]+)(?::(\d+))?", CHROMA_URL)
        if not match:
            return None
        client = chromadb.HttpClient(host=match.group(1), port=int(match.group(2) or 8000))
        collection = client.get_or_create_collection("precedent_engine")
        docs = load_corpus()
        if collection.count() == 0:
            collection.add(
                ids=[doc["document_id"] for doc in docs],
                documents=[doc["text"] for doc in docs],
                metadatas=[{key: value if isinstance(value, str) else ",".join(value) for key, value in doc.items() if key not in {"text", "score"}} for doc in docs],
            )
        result = collection.query(query_texts=[query], n_results=top_k)
        ids = (result.get("ids") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        by_id = {doc["document_id"]: doc for doc in docs}
        output = []
        for index, document_id in enumerate(ids):
            doc = by_id.get(document_id)
            if doc and (doc["offense_category"] == category or category == "general"):
                output.append({**doc, "score": 1.0 / (1.0 + float(distances[index])) if index < len(distances) else 0.5})
        return output
    except Exception:
        return None


def find_relevant_documents(category: str, factors: list[str], top_k: int = 4) -> list[dict[str, Any]]:
    query = " ".join([category, *factors])
    # Chroma gets a hard 3s budget. If it's slow to start, unreachable, or
    # hangs mid-connection, we fail fast and fall back to the deterministic
    # lexical index instead of blocking until the gateway's own 15s
    # timeout - a slow Chroma should degrade the demo, not break it.
    # shutdown(wait=False) is deliberate: if the Chroma call is genuinely
    # stuck, we abandon waiting on it rather than let a `with` block's
    # implicit shutdown(wait=True) block on the same stuck thread.
    pool = ThreadPoolExecutor(max_workers=1)
    future = pool.submit(_chroma_search, query, category, factors, top_k)
    try:
        result = future.result(timeout=3)
    except (FutureTimeoutError, Exception):
        result = None
    finally:
        pool.shutdown(wait=False)
    return result or _lexical_search(query, category, factors, top_k)
