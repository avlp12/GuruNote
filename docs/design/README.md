# GuruNote v2 Design Reference

## Origin
- Author: Alis Volat Propriis (self-generated via Claude Design)
- Date: 2026-04-23
- License: Private, 프로젝트 Phase 2A 참조 전용

## Files
- `v2-reference.html`: 10 화면 단일 HTML 파일 (Tailwind CDN 기반)

## Screens (v2-reference.html 내 섹션)
1. 생성 (idle) — 유튜브 URL 입력 + STT/LLM pill + 하드웨어 프리셋
2. 생성 (running) — 파이프라인 5단계 스테퍼 + 진행률
3. 생성 (complete) — 결과 + 탭 (요약/한국어/영어/Log) + Export
4. 히스토리 — YouTube 썸네일 카드 갤러리 + 필터 + 분류 집계
5. 노트 편집 — Raw Markdown + Preview 2-column
6. 대시보드 — 4 KPI + 분야별 분포 + 월별 추이 + 의미 검색 인덱스
7. 설정 — LLM Provider (6-tab 사이드바, provider 카드)
8. 설정 — STT 엔진
9. 설정 — Obsidian
10. 설정 — Notion / 고급 / GuruNote 정보

## Phase 2A scope (이 문서는 참조용, 결정 아님)
- 전부 재구현 예정
- 기존 `bridge.py` / `settings.py` / `history.py` 재사용
- Tailwind CSS CDN (MVP) → build pipeline (packaging 시점)
- Monaco 대신 EasyMDE / CodeMirror 6 / ContentEditable 중 택
- Obsidian 통합 backend 는 Phase 2B
