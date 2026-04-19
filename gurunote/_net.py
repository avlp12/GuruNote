"""
Network helpers — 공통 `urllib` 헬퍼.

macOS python.org 설치본(예: Python 3.13 installer) 은 기본적으로 시스템
루트 CA 스토어에 접근하지 않아 `urlopen("https://...")` 이
`SSL: CERTIFICATE_VERIFY_FAILED` 로 실패한다. 사용자가 `Install
Certificates.command` 를 수동 실행하면 해결되지만, 앱 측에서 `certifi`
번들을 명시해 주면 해당 수동 단계가 필요 없어진다.

`certifi` 는 `yt-dlp`/`requests`/`pip` 등 흔한 Python 패키지의 전이적
의존성으로 거의 모든 환경에 이미 설치돼 있으므로 `ImportError` 는 드문
폴백 경로. 그래도 방어적으로 system default 로 폴백해 Linux/Windows 의
표준 동작을 깨지 않음.
"""
from __future__ import annotations

import ssl
from functools import lru_cache


@lru_cache(maxsize=1)
def default_ssl_context() -> ssl.SSLContext:
    """SSL context — `certifi` 번들 우선, 없으면 system default.

    `@lru_cache` 로 동일 프로세스 내 재호출 비용 제거. context 는
    thread-safe (Python 3.2+) 하므로 모든 urlopen 호출에 공유 가능.
    """
    try:
        import certifi  # type: ignore[import-untyped]
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


__all__ = ["default_ssl_context"]
