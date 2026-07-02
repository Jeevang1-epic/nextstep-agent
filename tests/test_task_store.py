import json
from pathlib import Path

from nextstep_agent.task_store import load_tasks, persist_action_items


def test_task_store_persists_jsonl_records(tmp_path: Path) -> None:
    store_path = tmp_path / "tasks.jsonl"

    result = persist_action_items(
        [
            {
                "id": "A1",
                "title": "Call [REDACTED_PHONE]",
                "due_date": "2026-07-08",
                "priority": 1,
                "status": "open",
                "source_evidence": "Account Number: 7788-2219-004",
            }
        ],
        session_id="run-test",
        store_path=store_path,
    )

    assert result["stored_count"] == 1
    assert result["session_id"] == "run-test"
    assert store_path.exists()

    line = store_path.read_text(encoding="utf-8").strip()
    record = json.loads(line)
    assert record["session_id"] == "run-test"
    assert "7788-2219-004" not in line
    assert "[REDACTED_IDENTIFIER]" in line
    assert load_tasks("run-test", store_path=store_path)[0]["id"] == "A1"
