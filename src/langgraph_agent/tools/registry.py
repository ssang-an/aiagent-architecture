from __future__ import annotations

from .base import Tool


def knowledge_search(payload: dict) -> dict:
    query = payload.get("query", "")
    return {"docs": [f"doc_about:{query}", f"context_for:{query}"]}


def summarize_text(payload: dict) -> dict:
    text = payload.get("text", "")
    return {"summary": f"요약: {text[:80]}"}


def ticket_create(payload: dict) -> dict:
    return {"ticket_id": "TICK-1001", "status": "created", "payload": payload}


TOOL_REGISTRY: dict[str, Tool] = {
    "knowledge_search": Tool(name="knowledge_search", handler=knowledge_search),
    "summarize_text": Tool(name="summarize_text", handler=summarize_text),
    "ticket_create": Tool(name="ticket_create", handler=ticket_create),
}
