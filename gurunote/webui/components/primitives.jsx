/* GuruNote primitives — Phase 2A Step 3b
 * SPDX-License-Identifier: Elastic-2.0
 * Copyright (c) 2026 GuruNote contributors.
 *
 * 출처: docs/design/extracted/primitives.jsx 의 Icon / Btn / Chip 부분
 * Babel standalone 호환 (import/export 없음, top-level function 으로 글로벌 노출)
 *
 * Material Symbols 폰트는 아직 vendor 에 없음 — 아이콘 이름이 텍스트로 표시됨.
 * 폰트 추출은 후속 step.
 */

function Icon({ name, className = '', style }) {
  return (
    <span className={`msi ${className}`} style={style}>{name}</span>
  );
}

function Btn({ icon, children, variant = 'tonal', size, onClick, style, disabled, title }) {
  return (
    <button
      className={`btn ${variant}${size ? ' ' + size : ''}`}
      onClick={onClick}
      style={style}
      disabled={disabled}
      title={title}
    >
      {icon && <Icon name={icon} />}
      {children}
    </button>
  );
}

function Chip({ icon, children, selected, onClick, variant = 'filter', style }) {
  return (
    <button
      className={`chip ${variant} ${selected ? 'selected' : ''}`}
      onClick={onClick}
      style={style}
    >
      {icon && <Icon name={icon} />}
      {children}
    </button>
  );
}
