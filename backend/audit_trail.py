"""Append-only audit trail of the agent loop: output/audit_trail.json.

The file stays a valid JSON array. Each new entry is written just before the closing "]",
so earlier entries are never rewritten, only added to.
"""
import json
import threading
from pathlib import Path

from pydantic_ai.messages import ModelResponse, ToolCallPart

from models import AuditEntry, ToolCallRecord

AUDIT_TRAIL = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"
_lock = threading.Lock()  # two chats finishing at once must not interleave their writes


def tool_calls_from(messages: list) -> list[ToolCallRecord]:
    """Every tool the agent called during the run, in order (not the final-answer step)."""
    calls = []
    for message in messages:
        if isinstance(message, ModelResponse):
            for part in message.parts:
                if isinstance(part, ToolCallPart) and part.tool_name != "final_result":
                    calls.append(ToolCallRecord(tool=part.tool_name, args=part.args_as_dict()))
    return calls


def append_entry(entry: AuditEntry) -> None:
    text = json.dumps(entry.model_dump(), ensure_ascii=False, indent=2)
    text = "\n".join("  " + line for line in text.splitlines())
    with _lock:
        AUDIT_TRAIL.parent.mkdir(parents=True, exist_ok=True)
        if not AUDIT_TRAIL.exists() or AUDIT_TRAIL.stat().st_size == 0:
            AUDIT_TRAIL.write_text("[\n" + text + "\n]\n", encoding="utf-8")
            return
        with AUDIT_TRAIL.open("r+b") as f:
            # Step back over the closing "]" (and trailing whitespace), then add ",<entry>]".
            f.seek(0, 2)
            pos = f.tell()
            while pos > 0:
                pos -= 1
                f.seek(pos)
                if f.read(1) == b"]":
                    break
            f.seek(pos)
            f.truncate()
            f.write((",\n" + text + "\n]\n").encode("utf-8") if pos > 2 else (text + "\n]\n").encode("utf-8"))
