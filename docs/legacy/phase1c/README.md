# Phase 1-C — Vanilla UI Archive

`index.html` (2,123 라인 vanilla HTML+CSS+JS) — Phase 2B 신축에서 폐기 결정 후
참조용으로 보존.

## 보존 이유

- 신축 시 비교 reference (Phase 1-C 의 동작 / DOM 구조 / vanilla JS 핸들러)
- 회귀 진단 시 Phase 1-C 가 어떻게 동작했는지 확인용
- bridge API 호출 패턴 (callApi) 의 기존 사용 사례

## 폐기 결정 (2026-04-27)

Phase 1-C vanilla 위에 material3.css + React shell 적층 한 결과:
- 생성 버튼 / 파일 선택 visibility 깨짐
- 로그창 layout shift, 완성 후 layout 깨짐
- 히스토리 점프, 히스토리 재열람 후 생성 탭 망가짐

모두 vanilla 와 React 의 cohabitation 문제 — patch 누적은 본질적 해결 아님.
Phase 2B 부터 React-only 신축 (레퍼런스 디자인 그대로).

## 마지막 작동 시점

- Branch: `redesign/tailwind-v2`
- Commit: `b1cd138` (Phase 2A Commit 3a Step 0 — 디자인 자산 재추출)
- Daily 도구는 `main` 브랜치 (Phase 1-C 그대로) 로 사용

## reference

- 추출된 디자인 자산: `docs/design/extracted/`
- 디자인 원본: `docs/design/v2-reference.html` (bundler template)
- 백업 branch: `archive/commit-2-aborted` (4d7222f), `backup/pre-tailwind-rewrite-20260425` (cedae0e)
