# GuruNote WebView Vendor 자산

오프라인 운영을 위해 외부 CDN 의존성을 로컬화한 폴더.

## 파일 구성

| 파일 | 버전 | 용도 |
|---|---|---|
| `react.production.min.js` | React 18 | UI 라이브러리 (production 빌드) |
| `react-dom.production.min.js` | ReactDOM 18 | DOM 렌더러 |
| `babel.min.js` | @babel/standalone | JSX 런타임 컴파일러 (~2.7 MB) |

## 사용 정책

- `index.html` 에서 **로컬 경로**로 import (CDN URL 직접 참조 금지)
- 업데이트 필요 시 `curl` 로 재다운로드
- Phase 3 packaging (PyInstaller) 시 그대로 번들에 포함됨
- pywebview 가 오프라인에서도 정상 작동

## 다운로드 출처

- React/ReactDOM: https://unpkg.com/react@18/umd/
- Babel: https://unpkg.com/@babel/standalone/
- 모두 MIT/BSD 호환 라이센스 (재배포 가능)

## 향후 최적화 (Phase 3)

- Babel standalone 제거 → 빌드 타임에 JSX 사전 컴파일 (~2.7 MB 절감)
- React production CDN 사용 검토 (오프라인 의존 시점에 따라)
