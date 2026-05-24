"""
Phase 2 — HistoryDialog._render_card Drop-in Replacement
=========================================================

이 파일은 `gui.py` 의 `HistoryDialog._render_card` 메서드를 Google Light
테마 + 3가지 placeholder treatment + hover 재생 버튼 인터랙션을 반영한
새 버전으로 교체하는 패치입니다.

적용법
------
1. `gui.py` 의 `HistoryDialog` 클래스 내부에서 `_render_card` 메서드를
   찾아 전체(def _render_card 부터 다음 def 전까지) 를 이 파일의 본문으로
   교체합니다. 들여쓰기(4 space class method) 를 맞춰주세요.

2. `HistoryDialog.__init__` 근처에서 썸네일 스타일 rotation 용 캐시를
   초기화하는지 확인:
       self._thumb_style_cache: dict[str, int] = {}
   (없으면 `_render_card` 가 자동으로 생성 — 아래 코드가 setdefault 처리)

3. PIL 이 필요 — 기존 앱이 이미 썸네일에 PIL 을 쓰므로 추가 의존성 없음.

핵심 변경점 (vs. 기존)
----------------------
- **라이트 테마 호환**: `C_SURFACE=#ffffff`, `C_BORDER=#dadce0` 를 가정.
- **3-스타일 placeholder**: job_id 해시로 0/1/2 가 배정됨 (카드별 고정).
    0 → 대형 타이포 오버레이 + 태그 배지
    1 → 중앙 글래스 아바타 (업로더 이니셜)
    2 → 흰 배지 블록 + 업로더 pill
- **Hover 재생 버튼**: 썸네일 위로 마우스 진입 시 중앙에 ▶ 오버레이 등장,
  클릭 시 source_url 이 있으면 기본 브라우저로 오픈.
- **타이포/스페이싱**: Google Workspace 표준 (13/11, 12-16px padding).
"""

from __future__ import annotations

# -----------------------------------------------------------------------------
# 아래 함수 본문을 gui.py 의 HistoryDialog 클래스 메서드로 붙여넣으세요.
# -----------------------------------------------------------------------------

def _render_card(self, row: int, col: int, job: dict) -> None:
    """단일 히스토리 카드 — 3가지 썸네일 스타일 중 하나 + hover 재생 버튼.

    스타일 선택은 job_id 해시로 결정돼 동일 카드가 항상 동일 스타일을 씀
    (세션마다 깜빡이지 않음).
    """
    import webbrowser
    from tkinter import Frame, Canvas, Label  # 저수준 — hover 바인딩용

    # ── 스타일 배정 (안정적 해시) ────────────────────────────────────────
    self._thumb_style_cache = getattr(self, "_thumb_style_cache", {})
    job_id = job.get("job_id", "") or ""
    if job_id not in self._thumb_style_cache:
        self._thumb_style_cache[job_id] = abs(hash(job_id)) % 3
    thumb_style = self._thumb_style_cache[job_id]

    # ── 외곽 카드 컨테이너 ────────────────────────────────────────────────
    card = ctk.CTkFrame(
        self._scroll,
        fg_color=C_SURFACE,            # 흰 배경
        border_color=C_BORDER,
        border_width=1,
        corner_radius=12,
    )
    card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
    card.grid_columnconfigure(0, weight=1)

    # ── 1) Thumbnail 영역 (Canvas — hover 오버레이 배치) ─────────────────
    thumb_frame = ctk.CTkFrame(
        card, fg_color="transparent", corner_radius=12,
        width=self._THUMB_W, height=self._THUMB_H,
    )
    thumb_frame.grid(row=0, column=0, padx=10, pady=(10, 8), sticky="ew")
    thumb_frame.grid_propagate(False)
    thumb_frame.grid_columnconfigure(0, weight=1)
    thumb_frame.grid_rowconfigure(0, weight=1)

    # 실제 썸네일 이미지 or placeholder
    source_url = job.get("source_url") or ""
    yt_id = extract_youtube_id(source_url) if source_url else None
    cached = cached_thumbnail_path(yt_id) if yt_id else None
    uploader = (job.get("uploader") or "").strip()
    title = (job.get("organized_title") or job.get("title") or "").strip()

    thumb_lbl = ctk.CTkLabel(thumb_frame, text="", fg_color="transparent")
    thumb_lbl.grid(row=0, column=0, sticky="nsew")

    if cached and Path(cached).exists():
        # 이미지 로드
        try:
            from PIL import Image as _PIL
            im = _PIL.open(cached).convert("RGB").resize(
                (self._THUMB_W, self._THUMB_H), _PIL.LANCZOS,
            )
            photo = ctk.CTkImage(light_image=im, dark_image=im,
                                 size=(self._THUMB_W, self._THUMB_H))
            self._thumb_refs[job_id] = photo
            thumb_lbl.configure(image=photo)
        except Exception:  # noqa: BLE001
            _render_placeholder(thumb_lbl, thumb_style, title, uploader)
    else:
        _render_placeholder(thumb_lbl, thumb_style, title, uploader)
        # 비동기 다운로드 요청 — 완성되면 큐에 푸시
        if yt_id and job_id not in self._pending_thumb_ids:
            self._pending_thumb_ids.add(job_id)
            def _on_done(path, _jid=job_id):
                if path:
                    self._thumb_queue.put((_jid, path))
            download_thumbnail_async(yt_id, _on_done)

    # Hover 재생 버튼 — 중앙에 ▶ (투명도 대신 on/off)
    play_btn = ctk.CTkLabel(
        thumb_frame,
        text="▶",
        fg_color="#000000",           # 반투명 불가 — 단색
        text_color="#ffffff",
        font=ctk.CTkFont(size=22, weight="bold"),
        corner_radius=999,
        width=44, height=44,
    )

    def _on_enter(_e=None):
        play_btn.place(relx=0.5, rely=0.5, anchor="center")
    def _on_leave(_e=None):
        play_btn.place_forget()
    def _on_click(_e=None):
        if source_url:
            try:
                webbrowser.open(source_url)
            except Exception:  # noqa: BLE001
                pass

    for w in (thumb_frame, thumb_lbl, play_btn):
        w.bind("<Enter>", _on_enter)
        w.bind("<Leave>", _on_leave)
        w.bind("<Button-1>", _on_click)

    # ── 2) 메타 영역 (제목 + 업로더 + 분야/태그) ─────────────────────────
    meta = ctk.CTkFrame(card, fg_color="transparent")
    meta.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
    meta.grid_columnconfigure(0, weight=1)

    # 제목 — 2줄 ellipsis
    display_title = title[:60] + ("…" if len(title) > 60 else "")
    ctk.CTkLabel(
        meta, text=display_title or "(제목 없음)",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color=C_TEXT, anchor="w", justify="left",
        wraplength=self._CARD_W - 24,
    ).grid(row=0, column=0, sticky="ew", pady=(4, 2))

    # 업로더 · 시각
    ts = _format_ts(job.get("created_at") or "")
    sub_bits = []
    if uploader:
        sub_bits.append(uploader)
    if ts:
        sub_bits.append(ts)
    if sub_bits:
        ctk.CTkLabel(
            meta, text="  ·  ".join(sub_bits),
            font=ctk.CTkFont(size=11),
            text_color=C_TEXT_DIM, anchor="w", justify="left",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 4))

    # 스니펫 (본문 / 의미 검색)
    snippet = job.get("_body_snippet")
    if snippet:
        ctk.CTkLabel(
            meta, text=snippet[:120] + ("…" if len(snippet) > 120 else ""),
            font=ctk.CTkFont(size=11),
            text_color=C_TEXT_DIM, anchor="w", justify="left",
            wraplength=self._CARD_W - 24,
        ).grid(row=2, column=0, sticky="ew", pady=(0, 4))

    # 상태 pill + 분야 chip
    chips = ctk.CTkFrame(meta, fg_color="transparent")
    chips.grid(row=3, column=0, sticky="ew", pady=(6, 0))
    status = job.get("status", "completed")
    status_label = {"completed": "완료", "failed": "실패",
                    "running": "처리 중"}.get(status, status)
    bg, fg = ut.STATUS_COLORS.get(status_label, ("#f1f3f4", "#5f6368"))
    ctk.CTkLabel(
        chips, text=status_label,
        fg_color=bg, text_color=fg, corner_radius=999,
        font=ctk.CTkFont(size=10, weight="bold"),
        padx=10, pady=2, height=20,
    ).pack(side="left", padx=(0, 6))

    field = (job.get("field") or "").strip()
    if field:
        ctk.CTkLabel(
            chips, text=field,
            fg_color="#e8f0fe", text_color="#1a73e8", corner_radius=999,
            font=ctk.CTkFont(size=10),
            padx=10, pady=2, height=20,
        ).pack(side="left")

    # 전체 카드 클릭 — 노트 에디터 오픈
    def _open_editor(_e=None):
        try:
            md = get_job_markdown(job_id) or ""
        except Exception:  # noqa: BLE001
            md = ""
        NoteEditorDialog(
            self, job_id=job_id, title=title, initial_md=md,
            on_saved=self._reload_and_refresh,
        )
    for w in (card, meta):
        w.bind("<Button-3>", _open_editor)   # 우클릭 — 썸네일 클릭과 분리


def _render_placeholder(label_widget, style: int, title: str, uploader: str) -> None:
    """PIL 로 3가지 placeholder 이미지 중 하나를 생성해 label_widget 에 부착.

    style 0 — 대형 타이포 오버레이 + "AUDIO" 배지
    style 1 — 중앙 원형 글래스 아바타 (업로더 이니셜)
    style 2 — 흰 블록 + 업로더 pill
    """
    from PIL import Image, ImageDraw, ImageFont
    W, H = 256, 144

    # 배경 색조 — job 에 따라 3톤 로테이션 (라이트 테마에 맞는 soft 파스텔)
    palettes = [
        ("#e8f0fe", "#1a73e8"),   # Google Blue soft
        ("#e6f4ea", "#1e8e3e"),   # Google Green soft
        ("#fef7e0", "#f9ab00"),   # Google Yellow soft
    ]
    bg_hex, accent_hex = palettes[style]

    im = Image.new("RGB", (W, H), bg_hex)
    draw = ImageDraw.Draw(im)

    try:
        font_big = ImageFont.truetype("Arial Bold.ttf", 22)
        font_sm = ImageFont.truetype("Arial.ttf", 11)
    except Exception:  # noqa: BLE001
        font_big = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    # 대각선 스트라이프 패턴 (아주 은은하게)
    for i in range(-H, W, 14):
        draw.line([(i, 0), (i + H, H)], fill=bg_hex, width=1)

    initial = (uploader or title or "G")[0].upper()

    if style == 0:
        # 대형 타이포 오버레이
        t = (title or "NOTE").upper()[:18]
        draw.text((14, 14), t, fill=accent_hex, font=font_big)
        # 배지
        draw.rounded_rectangle([14, H - 28, 70, H - 10],
                               radius=9, fill=accent_hex)
        draw.text((22, H - 26), "AUDIO", fill="#ffffff", font=font_sm)
    elif style == 1:
        # 중앙 원형 아바타
        cx, cy, r = W // 2, H // 2, 28
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#ffffff",
                     outline=accent_hex, width=2)
        # 이니셜
        draw.text((cx - 8, cy - 14), initial, fill=accent_hex, font=font_big)
    else:
        # 흰 배지 블록 + uploader pill
        draw.rounded_rectangle([20, 30, W - 20, H - 46],
                               radius=10, fill="#ffffff",
                               outline=accent_hex, width=1)
        u = (uploader or "GuruNote")[:22]
        draw.rounded_rectangle([20, H - 34, 20 + 10 * len(u), H - 14],
                               radius=10, fill=accent_hex)
        draw.text((26, H - 32), u, fill="#ffffff", font=font_sm)

    photo = ctk.CTkImage(light_image=im, dark_image=im, size=(W, H))
    # GC 방지 — 위젯에 attach
    label_widget._placeholder_ref = photo
    label_widget.configure(image=photo)
