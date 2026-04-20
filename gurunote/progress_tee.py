"""
stderr/stdout tee for forwarding tqdm-style backend progress to the GUI log.

What problem this solves
------------------------
HuggingFace `snapshot_download`, `mlx-whisper`, `faster-whisper` 등은 모두
`tqdm` 진행률을 **stderr 로** 직접 print 한다. GUI 의 `_log()` 콜백은 우리
애플리케이션 코드가 명시적으로 호출하는 메시지만 받으므로, 모델 다운로드나
전사 프레임 진행률은 CLI 터미널에서만 보이고 GUI 로그 패널에는 안 나타난다.

이 모듈은 `install_tee(callback)` 동안 `sys.stderr` (선택적으로 `sys.stdout`)
를 교체해, 모든 출력을 원본에도 그대로 내보내면서 **한 줄 단위로 callback 에도
전달**한다. callback 은 GUI 로그에 연결되며, 내부적으로 tqdm 패턴을 파싱해
퍼센트/경과/남은 시간/속도만 압축해 표시한다.

Design
------
- `_StderrTee.write` 는 기존 stream 에 즉시 write + 내부 버퍼에 누적
- tqdm 은 `\\r` 로 같은 줄을 갱신하므로 `\\r` / `\\n` 모두 줄 경계로 처리
- `_throttle_ms` (기본 500ms) 스로틀링으로 GUI 홍수 방지
- ANSI color escape (`\\x1b[...m`) 제거 후 파싱
- 패턴별 압축:
  * `NN%|...|cur/total [elapsed<eta, rate unit]`  → `[STT] 39% · 03:12 경과 · ~9:37 남음 · 657 frame/s`
  * `Fetching N files: NN%|...|m/n [...]`          → `[모델] N 파일 중 m개 완료`
  * `Download complete: ...`                       → `[모델] 다운로드 완료`
  * `Detected language: XX`                        → `[언어] XX 감지`
  * 그 외 noise (warning, 빈 줄) → drop

사용
----
    from gurunote.progress_tee import install_tee
    with install_tee(lambda line: self._log(line)):
        download_audio(...)
        transcribe(...)
"""

from __future__ import annotations

import contextlib
import re
import sys
import time
from typing import Callable, Iterator, Optional

# ANSI CSI 시퀀스 (컬러, 커서 제어 등)
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")

# tqdm 의 전사 진행률 라인: "39%|████▌         | 239370/619235 [05:14<09:37, 657.42frames/s]"
# % 가 없는 경우 (용량 기반): "Download complete: : 3.08GB [00:44, 255MB/s]"
_TQDM_PCT_RE = re.compile(
    r"(\d+)%.*?\|.*?\|\s*(\d+)/(\d+)\s*\[(\d+:\d+(?::\d+)?)<(\d+:\d+(?::\d+)?)(?:,\s*(\d+\.?\d*)\s*(\S+?))?\]"
)
_TQDM_BYTES_RE = re.compile(
    r"(\d+\.?\d*[KMG]B)\s*\[(\d+:\d+(?::\d+)?)(?:,\s*(\d+\.?\d*)\s*(\S+?))?\]"
)

ProgressCallback = Callable[[str], None]


class _Tee:
    """stderr/stdout 교체용 writer."""

    def __init__(
        self,
        original,
        callback: ProgressCallback,
        throttle_ms: int = 500,
        prefix: str = "",
    ):
        self._original = original
        self._callback = callback
        self._throttle_ms = throttle_ms
        self._prefix = prefix
        self._buffer = ""
        self._last_emit = 0.0
        self._seen_hf_warning = False

    # 기존 stream 과 호환되도록 attribute pass-through
    def __getattr__(self, name):
        return getattr(self._original, name)

    def write(self, data: str) -> int:
        try:
            n = self._original.write(data)
        except Exception:  # noqa: BLE001
            n = len(data)
        self._buffer += data
        self._drain_lines()
        return n

    def flush(self) -> None:
        try:
            self._original.flush()
        except Exception:  # noqa: BLE001
            pass

    # -------------------------------------------------------------------------
    def _drain_lines(self) -> None:
        """버퍼에서 완전한 줄 (\\r 또는 \\n 으로 끝) 을 꺼내 _emit."""
        while True:
            r_idx = self._buffer.find("\r")
            n_idx = self._buffer.find("\n")
            positions = [i for i in (r_idx, n_idx) if i >= 0]
            if not positions:
                break
            cut = min(positions)
            line = self._buffer[:cut]
            self._buffer = self._buffer[cut + 1 :]
            line = line.rstrip()
            if line:
                self._try_emit(line)

    def _try_emit(self, raw_line: str) -> None:
        compact = _condense(raw_line, self)
        if not compact:
            return
        now = time.monotonic() * 1000
        # 중요한 일회성 이벤트 (모델 다운로드 완료, 언어 감지) 는 스로틀 무시
        priority = compact.startswith(("[언어]", "[모델] 다운로드 완료"))
        if not priority and now - self._last_emit < self._throttle_ms:
            return
        self._last_emit = now
        try:
            self._callback(f"{self._prefix}{compact}")
        except Exception:  # noqa: BLE001
            pass


# =============================================================================
# 압축 로직
# =============================================================================
def _condense(raw_line: str, state: _Tee) -> Optional[str]:
    """tqdm/HF 출력을 `[태그] 요약` 형태로 압축. 매칭 없으면 None."""
    clean = _ANSI_RE.sub("", raw_line).strip()
    if not clean:
        return None

    # Detected language: English  →  [언어] English 감지
    if clean.startswith("Detected language:"):
        lang = clean.split(":", 1)[1].strip()
        return f"[언어] {lang} 감지"

    # Download complete:  →  [모델] 다운로드 완료
    if clean.startswith("Download complete"):
        # 크기/시간/속도 함께 표시
        m = _TQDM_BYTES_RE.search(clean)
        if m:
            size, elapsed, rate, unit = m.groups()
            rate_str = f" · {rate} {unit}" if rate else ""
            return f"[모델] 다운로드 완료 ({size}, {elapsed}{rate_str})"
        return "[모델] 다운로드 완료"

    # HF 토큰 경고 — 1회만 노출
    if "unauthenticated requests to the HF Hub" in clean:
        if state._seen_hf_warning:
            return None
        state._seen_hf_warning = True
        return "[경고] HF_TOKEN 미설정 — rate limit 가 낮을 수 있습니다 (설정에서 HF_TOKEN 등록 권장)"

    # Fetching N files: 75%|...| 3/4 [00:33<00:11, 11.06s/it]
    if clean.startswith("Fetching"):
        m = _TQDM_PCT_RE.search(clean)
        if m:
            pct, cur, total, elapsed, eta, rate, unit = m.groups()
            head = clean.split(":", 1)[0]  # "Fetching N files"
            return f"[모델] {head} — {cur}/{total} ({pct}%) · 남음 ~{eta}"
        return None

    # STT frame progress: "39%|...| 239370/619235 [05:14<09:37, 657.42frames/s]"
    m = _TQDM_PCT_RE.search(clean)
    if m:
        pct, cur, total, elapsed, eta, rate, unit = m.groups()
        rate_str = f" · {rate} {unit}" if rate else ""
        return f"[STT] {pct}% ({cur}/{total}) · {elapsed} 경과 · ~{eta} 남음{rate_str}"

    # 나머지는 noise (empty progress bars, internal tqdm repaint 등) → drop
    return None


# =============================================================================
# Public entry point
# =============================================================================
@contextlib.contextmanager
def install_tee(
    callback: ProgressCallback,
    *,
    include_stdout: bool = False,
    throttle_ms: int = 500,
) -> Iterator[None]:
    """
    `sys.stderr` (선택적으로 `sys.stdout`) 를 교체해 tqdm 진행률을 callback 에 전달.

    사용 예:
        with install_tee(self._log):
            download_audio(url, out_dir)   # yt-dlp / ffmpeg 로그
            transcribe(audio_path, ...)    # mlx-whisper / whisperx tqdm

    주의:
      - `sys.stderr` 는 프로세스 전역이므로 다른 스레드의 stderr 도 영향을 받음.
        GuruNote 파이프라인이 단일 백그라운드 스레드이고 GUI 메인 스레드의
        stderr 는 사용하지 않으므로 실사용 상 충돌 없음.
      - 예외 시에도 원래 stream 으로 복원.
    """
    orig_err = sys.stderr
    tee_err = _Tee(orig_err, callback, throttle_ms=throttle_ms)
    sys.stderr = tee_err

    orig_out = None
    tee_out: Optional[_Tee] = None
    if include_stdout:
        orig_out = sys.stdout
        tee_out = _Tee(orig_out, callback, throttle_ms=throttle_ms)
        sys.stdout = tee_out

    try:
        yield
    finally:
        # flush pending buffer
        try:
            tee_err.flush()
        except Exception:  # noqa: BLE001
            pass
        if tee_out is not None:
            try:
                tee_out.flush()
            except Exception:  # noqa: BLE001
                pass
        # 방어적 restore: 우리가 설치한 tee 가 여전히 top-of-stack 일 때만 교체.
        # 다른 코드가 그 사이 또 다른 tee 를 걸었다면 함부로 덮지 않는다
        # (nested install_tee 호출 등 엣지 케이스에서 stderr 영구 오염 방지).
        if sys.stderr is tee_err:
            sys.stderr = orig_err
        if tee_out is not None and sys.stdout is tee_out:
            sys.stdout = orig_out
