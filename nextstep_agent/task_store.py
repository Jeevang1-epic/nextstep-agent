from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import BASE_DIR
from .redaction import redact_value


DEFAULT_TASK_STORE_PATH = BASE_DIR / "data" / "tasks.jsonl"


def new_session_id() -> str:
    return f"run-{uuid.uuid4().hex[:12]}"


def persist_action_items(
    action_items: list[dict[str, Any]],
    session_id: str | None = None,
    store_path: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(store_path) if store_path else DEFAULT_TASK_STORE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    run_id = session_id or new_session_id()
    now = datetime.now(timezone.utc).isoformat()

    records: list[dict[str, Any]] = []
    for index, item in enumerate(action_items, start=1):
        safe_item = redact_value(item)
        records.append(
            {
                "session_id": run_id,
                "stored_at": now,
                "sequence": index,
                "id": str(safe_item.get("id", f"T{index}")),
                "title": str(safe_item.get("title", "Untitled task")),
                "due_date": safe_item.get("due_date"),
                "priority": safe_item.get("priority"),
                "status": safe_item.get("status", "open"),
                "owner": safe_item.get("owner", "user"),
                "source_evidence": safe_item.get("source_evidence", ""),
            }
        )

    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    return {
        "session_id": run_id,
        "stored_count": len(records),
        "total_count": len(records),
        "task_store_path": _display_path(path),
        "tasks": records,
    }


def load_tasks(session_id: str | None = None, store_path: str | Path | None = None) -> list[dict[str, Any]]:
    path = Path(store_path) if store_path else DEFAULT_TASK_STORE_PATH
    if not path.exists():
        return []

    tasks: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if session_id is None or record.get("session_id") == session_id:
            tasks.append(record)
    return tasks


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(BASE_DIR)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")
