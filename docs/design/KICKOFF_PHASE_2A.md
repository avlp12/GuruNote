# Phase 2A — Kickoff Plan

다음 세션 시작 시 이 파일을 먼저 확인.

## Pre-work decisions needed (다음 세션 초반에 결정)

### Decision 1: License 전환
- 현재: MIT (Copyright 2026 Alis Volat Propriis)
- 후보:
  - Source-available 커스텀 (가장 제어권 강함)
  - Elastic License 2.0 (호스팅/재판매 제한)
  - BSL 4-year (시간제 제한)
- 결정 후: LICENSE 파일 교체 + 첫 commit 에 반영

### Decision 2: Tailwind 도입 방식
- CDN (즉시 시작 가능, production 권장 안 됨, MVP OK)
- npm install + build (시간 들임, packaging 이득)
- 추천: CDN 으로 MVP → Phase 3 packaging 시 build 전환

### Decision 3: Editor 선택 (노트 편집 화면)
- EasyMDE (마크다운 전용, ~150 KB)
- CodeMirror 6 (범용, ~100 KB)
- ContentEditable + marked.js (최소)
- 추천: EasyMDE (Obsidian 으로 대부분 편집 가정, GuruNote 는 경량)

### Decision 4: Design HTML 커밋 여부
- 옵션 A: `docs/design/` 전체 커밋 (참조 자산 영구 보존)
- 옵션 B: 로컬만 유지 (현재 상태)
- License 전환 후 결정

## First commits (예상 순서)

### Commit 1: Branch 초기화
- LICENSE 교체 (Decision 1 결과)
- README.md 업데이트 (Phase 2A 선언, 목표)
- .gitignore 정리

### Commit 2: Tailwind CDN 도입
- `index.html` 의 기본 구조 Tailwind 로 재작성
- 기존 vanilla CSS 주석 처리 or 삭제
- `bridge.py` JS 연결 확인 (모든 `callApi` 호출 작동)

### Commit 3: 생성 화면 (idle) 포팅
- Design HTML 의 "생성 idle" 섹션 가져와서 Tailwind 클래스 유지
- bridge 연결 (`start_pipeline` 등)
- 작동 확인: `python3 app_webview.py`

### Commit 4~: 나머지 화면 순차 포팅
- 생성 (running/complete)
- 히스토리 → 대시보드 → 설정 → 노트 편집 순

## 재사용 자산 (Phase 1-C 에서)

- `gurunote/webui/bridge.py` (전체)
- `gurunote/settings.py` (`get_settings`, `save_settings`, `_KNOWN_SETTINGS`, `_SECRET_KEYS`)
- `gurunote/history.py` (전체)
- `gurunote/llm.py` (Commit #5 fix 반영됨)
- `gurunote/pipeline.py` (전체)

## 폐기될 자산

- `gurunote/webui/index.html` (vanilla CSS 기반, Tailwind 로 대체)
- `gui.py` (CTk 기반, Phase 2A 는 WebView 전용)

## 예상 소요 (본인 페이스 기준)

- Kickoff 결정들: 30분 ~ 1시간 (첫 세션 초반)
- Commit 1~2: 각 30분 ~ 1시간
- Commit 3~10 (화면별): 각 1~2시간
- 통합 테스트 + 버그 fix: 수 시간
- 총: ~2주 (하루 2~4시간 기준)

## 작업 안 할 것 (Phase 2A 스코프 밖)

- claude-obsidian 통합 → Phase 2B
- 의미 검색 인덱스 → Phase 2B
- PyInstaller packaging → Phase 3
- YouTube 썸네일 저장 → Phase 2B
