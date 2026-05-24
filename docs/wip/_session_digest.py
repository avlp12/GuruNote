"""18개 세션 → user 메시지 timeline digest (5/24).

- 세션별 독립 처리 (한 번에 하나, 누적 적재 부재)
- user 메시지만 추출 (assistant 길이만 카운트)
- 토큰/키 값 마스킹 (hf_/sk-/Bearer 등)
- 출력: docs/wip/session_history_digest.md
"""
from __future__ import annotations

import json
import re
import os
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path.home() / ".claude" / "projects" / "-Users-gesicht-GuruNote"
OUT = Path("/Users/gesicht/GuruNote/docs/wip/session_history_digest.md")

# 토큰/키 패턴 — 마스킹
TOKEN_PATTERNS = [
    (re.compile(r"hf_[A-Za-z0-9]{20,}"), "hf_***MASKED***"),
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "sk-***MASKED***"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"), "Bearer ***MASKED***"),
    (re.compile(r"AKIA[A-Z0-9]{16,}"), "AKIA***MASKED***"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "ghp_***MASKED***"),
    (re.compile(r"glpat-[A-Za-z0-9_-]{20,}"), "glpat-***MASKED***"),
]


def mask(text: str) -> str:
    for pat, rep in TOKEN_PATTERNS:
        text = pat.sub(rep, text)
    return text


def extract_text(content) -> str:
    """user message content → text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text":
                    parts.append(c.get("text", ""))
                elif c.get("type") == "tool_result":
                    # tool result 는 요약만 (길어서 제외)
                    pass
        return "\n".join(parts)
    return ""


def process_session(jsonl_path: Path) -> dict:
    """세션 하나 → digest dict (RAM 효율, 라인 단위)."""
    user_msgs = []
    assistant_count = 0
    assistant_chars = 0
    first_ts = None
    last_ts = None
    git_branches = set()
    cwds = set()

    with open(jsonl_path) as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            ts = d.get("timestamp")
            if ts:
                if not first_ts:
                    first_ts = ts
                last_ts = ts
            if d.get("gitBranch"):
                git_branches.add(d["gitBranch"])
            if d.get("cwd"):
                cwds.add(d["cwd"])
            if t == "user":
                msg = d.get("message", {})
                if isinstance(msg, dict):
                    text = extract_text(msg.get("content", ""))
                    if text and text.strip():
                        # tool_result 만 있는 user 메시지 (assistant 도구 응답)는 길이로 catch
                        if "tool_use_id" in str(msg.get("content", "")):
                            continue
                        user_msgs.append({
                            "ts": ts,
                            "text": mask(text.strip()),
                        })
            elif t == "assistant":
                assistant_count += 1
                msg = d.get("message", {})
                if isinstance(msg, dict):
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict) and c.get("type") == "text":
                                assistant_chars += len(c.get("text", ""))

    return {
        "uuid": jsonl_path.stem,
        "size_bytes": jsonl_path.stat().st_size,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "user_msg_count": len(user_msgs),
        "user_msgs": user_msgs,
        "assistant_count": assistant_count,
        "assistant_chars": assistant_chars,
        "git_branches": sorted(git_branches),
        "cwds": sorted(cwds),
    }


def fmt_ts(ts: str | None) -> str:
    if not ts:
        return "?"
    # ISO → KST 형식
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%m/%d %H:%M")
    except Exception:
        return ts[:16]


def summarize_user_msg(text: str, max_chars: int = 200) -> str:
    """user 메시지 요약 — 첫 줄 또는 첫 N자."""
    text = text.strip()
    # 트랙 prefix 제거
    for prefix in ["=== 트랙 A:", "=== 트랙 B:", "트랙 A:", "트랙 B:"]:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break
    # 첫 줄 또는 첫 N자
    first_line = text.split("\n")[0].strip()
    if len(first_line) > max_chars:
        return first_line[:max_chars] + "..."
    return first_line


def main():
    sessions = sorted(SESSIONS_DIR.glob("*.jsonl"))
    print(f"세션 수: {len(sessions)}")

    digests = []
    for s in sessions:
        print(f"  처리: {s.name} ({s.stat().st_size//1024}KB)…")
        digest = process_session(s)
        digests.append(digest)

    # 시간순 정렬 (first_ts 기준)
    digests.sort(key=lambda d: d["first_ts"] or "")

    # output 작성
    lines = ["# GuruNote Claude Code 세션 18개 digest (5/24)", ""]
    lines.append(f"위치: `~/.claude/projects/-Users-gesicht-GuruNote/`")
    lines.append(f"세션 수: {len(digests)}")
    lines.append(f"기간: {fmt_ts(digests[0]['first_ts'])} ~ {fmt_ts(digests[-1]['last_ts'])}")
    lines.append("")
    lines.append("user 메시지 (작업 지시) + 시간 + 브랜치만 추출. assistant 응답 길이만 catch.")
    lines.append("토큰/키 (hf_/sk-/Bearer/ghp_/AKIA) 마스킹 적용.")
    lines.append("")

    # 세션별 요약
    for i, d in enumerate(digests, 1):
        lines.append("=" * 70)
        lines.append(f"## {i}. {fmt_ts(d['first_ts'])} ~ {fmt_ts(d['last_ts'])} ({d['size_bytes']//1024} KB)")
        lines.append(f"")
        lines.append(f"- UUID: `{d['uuid']}`")
        if d["git_branches"]:
            lines.append(f"- branch: {', '.join(d['git_branches'])}")
        lines.append(f"- user 메시지: {d['user_msg_count']}건, assistant 응답: {d['assistant_count']}건 ({d['assistant_chars']//1024} KB)")
        lines.append(f"")
        lines.append(f"### user 메시지 (작업 흐름)")
        lines.append(f"")
        for j, m in enumerate(d["user_msgs"][:100], 1):  # 세션당 max 100건
            ts = fmt_ts(m["ts"])
            summary = summarize_user_msg(m["text"])
            lines.append(f"{j}. **[{ts}]** {summary}")
        if len(d["user_msgs"]) > 100:
            lines.append(f"... +{len(d['user_msgs'])-100}건 더")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nsaved: {OUT} ({OUT.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
