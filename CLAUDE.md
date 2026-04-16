# Claude Code 작업 규칙

## 버전 정책 (Semantic Versioning)

[Semantic Versioning 2.0.0](https://semver.org/) 을 따른다: `MAJOR.MINOR.PATCH`

### 언제 올리나?

| 변경 종류 | 버전 | 예시 |
|---|---|---|
| **PATCH** (0.4.**1**) | 버그 수정, 경고 제거, 오타, API 호환성 수정, 문서 정비 | WhisperX diarize API 수정, AssemblyAI 파라미터 변경, 경고 억제 |
| **MINOR** (0.**5**.0) | 새 기능 추가, UI 변경, 신규 모듈, 엔진 교체, 설정 옵션 추가 | WhisperX 전환, GUI 리디자인, 히스토리 기능, 업데이트 체크 |
| **MAJOR** (**1**.0.0) | 하위 호환성이 깨지는 변경, 대규모 아키텍처 변경 | 1.0.0 전까지는 MINOR 로 대체 |

### 판단 기준

- **버전을 올려야 하는 경우:**
  - 사용자가 체감할 수 있는 변경 (기능, UI, 동작 방식)
  - 의존성 변경 (엔진 교체, 패키지 추가/제거)
  - 2개 이상의 버그 수정이 누적됐을 때
  - 설정 파일 (.env) 구조 변경

- **버전을 올리지 않아도 되는 경우:**
  - 코드 내부 리팩토링 (외부 동작 변화 없음)
  - 주석/문서만 수정
  - CI/CD 설정만 변경

### 커밋 메시지 접두사

| 접두사 | 의미 | 버전 영향 |
|---|---|---|
| `feat:` | 새 기능 | MINOR |
| `fix:` | 버그 수정 | PATCH |
| `docs:` | 문서만 | 보통 안 올림 |
| `chore:` | 의존성, 빌드, 설정 | PATCH (영향 있을 때) |
| `refactor:` | 리팩토링 (동작 불변) | 안 올림 |
| `style:` | UI/스타일 변경 | MINOR (사용자 체감) 또는 PATCH |

### 버전 업데이트 체크리스트

버전을 올릴 때 **반드시** 다음 5곳을 동시에 갱신:

1. `gurunote/__init__.py` → `__version__`
2. `gui.py` → 사이드바 버전 라벨
3. `scripts/package_desktop.py` → Inno Setup + pkgbuild 버전
4. `README.md` → "현재 버전" 문구
5. `CHANGELOG.md`:
   - `[Unreleased]` 내용을 `[X.Y.Z] - YYYY-MM-DD` 로 승격
   - 새 `[Unreleased]` 섹션 생성
   - 하단 비교 링크 갱신

## README 유지 규칙

- 새 기능이 추가되면 README 의 **주요 기능** / **FAQ** / **프로젝트 구조** 를 함께 갱신
- CLI 데모 로그 예시는 실제 출력 포맷과 일치하게 유지
- 이모지 사용 금지 (GUI 텍스트) — Windows 렌더링 호환성 위해 텍스트 라벨 사용

## CHANGELOG 규칙

- [Keep a Changelog](https://keepachangelog.com/) 형식 준수
- 모든 PR 의 변경 사항을 `[Unreleased]` 에 누적 (Added / Changed / Fixed / Removed)
- 릴리스 시 날짜와 함께 `[X.Y.Z] - YYYY-MM-DD` 로 승격
