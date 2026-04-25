# Phase 2A Design 추출 자산

`docs/design/v2-reference.html` (Claude Design bundler 템플릿) 에서 
추출한 raw 자산. **참조용 영구 보존**.

## 파일 구성

| 파일 | 출처 | 설명 |
|---|---|---|
| `v2-extracted.html` | template JSON 디코드 | 1,699 라인 — head + style + root + bootstrap |
| `primitives.jsx` | bundle 10b5b24f... | Icon, Btn, Chip, StepIndicator, FacetTree (288 라인) |
| `main_screen.jsx` | bundle a03bd33a... | MainScreen idle/running/done + Result tabs + History + JobCard (424 라인) |
| `editor.jsx` | bundle 274955f4... | EditorScreen + DashboardScreen + SettingsScreen + SettingsLLM (444 라인) |

## 추출 방식

원본 v2-reference.html 의 `<script type="__bundler/manifest">` 블록에 
gzip+base64 로 임베드된 14개 자산 중 컴포넌트 JSX 3개 + JSON template 1개 
를 디코드.

원본 stack:
- React 18 + ReactDOM 18
- Babel standalone (JSX 런타임 컴파일)
- Material 3 hand-rolled CSS (--gn-* 토큰, .gn-* 클래스)

## 사용 정책

- 이 폴더의 파일은 **참조용** — `gurunote/webui/components/` 에 손질된 
  버전을 두고, 디자인 의도 확인 시 원본 비교용으로 사용.
- 디자인 변경이 필요할 때 v2-reference.html 의 source of truth 로 거슬러 
  올라감.
- Elastic License 2.0 적용 (Phase 2A 의 일부).
