# Claude Code 작업 규칙

## 버전업 정책

주요 기능 추가 또는 중요 버그 수정이 포함된 PR 을 만들 때 **반드시** 버전을 올린다:

- **PATCH** (0.x.Y): 버그 수정, 문서 정비, 경고 제거 등
- **MINOR** (0.X.0): 새 기능 추가, UI 변경, 신규 모듈 등
- **MAJOR** (X.0.0): 하위 호환성이 깨지는 변경 (1.0.0 전까지는 MINOR 로 대체)

### 버전 업데이트 체크리스트

1. `gurunote/__init__.py` → `__version__`
2. `gui.py` → 사이드바 버전 라벨
3. `scripts/package_desktop.py` → Inno Setup + pkgbuild 버전
4. `README.md` → "현재 버전" 문구
5. `CHANGELOG.md` → `[Unreleased]` 내용을 `[X.Y.Z] - YYYY-MM-DD` 로 승격 + 새 `[Unreleased]` 섹션 생성 + 하단 비교 링크 갱신

## README 유지 규칙

- 새 기능이 추가되면 README 의 **주요 기능** / **FAQ** / **프로젝트 구조** 를 함께 갱신
- CLI 데모 로그 예시는 실제 출력 포맷과 일치하게 유지
- 이모지 사용 금지 (GUI 텍스트) — Windows 렌더링 호환성 위해 텍스트 라벨 사용

## CHANGELOG 규칙

- [Keep a Changelog](https://keepachangelog.com/) + [Semantic Versioning](https://semver.org/) 준수
- 모든 PR 의 변경 사항을 `[Unreleased]` 에 누적
- 릴리스 시 날짜와 함께 `[X.Y.Z] - YYYY-MM-DD` 로 승격
