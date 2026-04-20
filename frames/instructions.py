"""
=============================================================
frames/instructions.py - Modal Hướng Dẫn Chơi (CTk style)
=============================================================
Toplevel modal kéo được (drag header).
Dùng CTkButton cho nút ĐÃ HIỂU.

ĐỂ CHỈNH SỬA:
  - Màu sắc: sửa các hằng số BG, BORDER, BTN_BG...
  - Kích thước: sửa W, H
=============================================================
"""

import tkinter as tk
import customtkinter as ctk


class InstructionsModal(tk.Toplevel):
    """
    Hộp thoại Hướng dẫn chơi - Arcade dark theme.
    Kéo bằng cách giữ chuột vào header.
    """

    # ── Màu sắc ───────────────────────────────────────────────
    BG        = "#1a1a2e"    # Màu nền (khớp với menu)
    CARD_BG   = "#16213e"    # Màu nền card (hơi sáng hơn)
    BORDER    = "#f9a825"    # Viền vàng gold
    HDR_BG    = "#0f0f2d"    # Nền header
    TITLE_CLR = "#f9a825"    # Màu tiêu đề vàng
    TEXT_CLR  = "#d0d0e8"    # Màu văn bản chính
    CLOSE_CLR = "#888899"    # Màu nút ✕ bình thường
    TIP_BG    = "#251e00"    # Nền hộp mẹo
    TIP_BD    = "#7a5c00"    # Viền hộp mẹo
    TIP_TEXT  = "#ffe082"    # Chữ trong hộp mẹo
    FOOTER_BG = "#0d0d20"    # Nền footer
    BTN_BG    = "#2196F3"    # Màu nút ĐÃ HIỂU (xanh sáng)
    BTN_HOV   = "#1565C0"    # Màu nút khi hover

    # Màu số thứ tự bước
    NUM_BG  = ["#e53935", "#37474f", "#37474f", "#43a047"]

    # ── Kích thước ────────────────────────────────────────────
    W, H = 480, 540

    # ──────────────────────────────────────────────────────────

    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg=self.BORDER)
        self.resizable(False, False)
        self._dx = self._dy = 0
        self._center()
        self._build()
        self.lift()
        self.grab_set()
        self.focus_set()

    # ──────────────────────────────────────────────────────────
    #  VỊ TRÍ & DRAG
    # ──────────────────────────────────────────────────────────

    def _center(self):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(
            f"{self.W}x{self.H}+{(sw - self.W) // 2}+{(sh - self.H) // 2}"
        )

    def _drag_start(self, e):
        self._dx = e.x_root - self.winfo_x()
        self._dy = e.y_root - self.winfo_y()

    def _drag_do(self, e):
        self.geometry(f"+{e.x_root - self._dx}+{e.y_root - self._dy}")

    # ──────────────────────────────────────────────────────────
    #  BUILD LAYOUT
    # ──────────────────────────────────────────────────────────

    def _build(self):
        # Outer border frame (viền vàng)
        outer = tk.Frame(self, bg=self.BORDER, padx=2, pady=2)
        outer.pack(fill=tk.BOTH, expand=True)

        # Inner card
        inner = tk.Frame(outer, bg=self.CARD_BG)
        inner.pack(fill=tk.BOTH, expand=True)

        self._build_header(inner)
        tk.Frame(inner, bg=self.BORDER, height=1).pack(fill=tk.X)
        self._build_content(inner)
        self._build_footer(inner)

    # ──────────────────────────────────────────────────────────
    #  HEADER (kéo được)
    # ──────────────────────────────────────────────────────────

    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=self.HDR_BG, pady=14)
        hdr.pack(fill=tk.X)
        hdr.bind("<ButtonPress-1>", self._drag_start)
        hdr.bind("<B1-Motion>",     self._drag_do)

        # Icon ℹ
        tk.Label(
            hdr, text=" ⓘ ", bg=self.TITLE_CLR, fg=self.HDR_BG,
            font=("Arial", 12, "bold")
        ).pack(side=tk.LEFT, padx=(14, 10))

        # Tiêu đề
        tk.Label(
            hdr, text="HƯỚNG DẪN CHƠI",
            bg=self.HDR_BG, fg=self.TITLE_CLR,
            font=("Arial", 15, "bold")
        ).pack(side=tk.LEFT)

        # Nút đóng ✕
        xl = tk.Label(
            hdr, text="  ✕  ",
            bg=self.HDR_BG, fg=self.CLOSE_CLR,
            font=("Arial", 14, "bold"), cursor="hand2"
        )
        xl.pack(side=tk.RIGHT, padx=10)
        xl.bind("<Button-1>", lambda e: self._close())
        xl.bind("<Enter>",    lambda e: xl.config(fg="white",        bg="#7F1D1D"))
        xl.bind("<Leave>",    lambda e: xl.config(fg=self.CLOSE_CLR, bg=self.HDR_BG))

    # ──────────────────────────────────────────────────────────
    #  NỘI DUNG (4 bước + hộp mẹo)
    # ──────────────────────────────────────────────────────────

    def _build_content(self, parent):
        content = tk.Frame(parent, bg=self.CARD_BG, padx=18, pady=12)
        content.pack(fill=tk.BOTH, expand=True)

        steps = [
            (
                "Bạn sẽ cầm xu ",
                [("Đỏ", "#F87171", True),
                 (", Máy (AI) cầm xu ", self.TEXT_CLR, False),
                 ("Vàng", "#FACC15", True), (".", self.TEXT_CLR, False)]
            ),
            ("Mỗi lượt, click vào một cột trên bàn cờ để thả xu.", []),
            ("Xu tự động rơi xuống vị trí thấp nhất còn trống.", []),
            (
                "Người đầu tiên xếp được ",
                [("4 xu liên tiếp", "#4ADE80", True),
                 (" (ngang, dọc, chéo) sẽ chiến thắng!", self.TEXT_CLR, False)]
            ),
        ]

        for idx, (base, extras) in enumerate(steps):
            self._add_step(content, idx + 1, base, extras)

        # ── Hộp mẹo ───────────────────────────────────────────
        bd_box = tk.Frame(content, bg=self.TIP_BD, padx=1, pady=1)
        bd_box.pack(fill=tk.X, pady=(12, 0))

        tip = tk.Frame(bd_box, bg=self.TIP_BG, padx=14, pady=12)
        tip.pack(fill=tk.BOTH)

        row = tk.Frame(tip, bg=self.TIP_BG)
        row.pack(fill=tk.X)

        tk.Label(row, text="💡", bg=self.TIP_BG,
                 font=("Arial", 16)).pack(side=tk.LEFT, padx=(0, 10), anchor=tk.N)

        tk.Label(
            row,
            text=("Mẹo: Thuật toán AI tính toán rất nhanh. Hãy liên tục "
                  "quan sát để chặn các đường chéo trước khi quá muộn!"),
            bg=self.TIP_BG, fg=self.TIP_TEXT,
            font=("Arial", 10, "italic"),
            wraplength=340, justify=tk.LEFT
        ).pack(side=tk.LEFT, expand=True)

    def _add_step(self, parent, num: int, base: str, extras: list):
        """Thêm một bước hướng dẫn có số thứ tự trong vòng tròn."""
        row = tk.Frame(parent, bg=self.CARD_BG, pady=6)
        row.pack(fill=tk.X)

        # Vòng tròn số
        c = tk.Canvas(row, width=32, height=32,
                      bg=self.CARD_BG, highlightthickness=0)
        c.pack(side=tk.LEFT, padx=(0, 12), anchor=tk.N, pady=2)
        c.create_oval(1, 1, 31, 31, fill=self.NUM_BG[num - 1], outline="", width=0)
        c.create_text(16, 16, text=str(num),
                      font=("Arial", 12, "bold"), fill="white")

        # Văn bản
        line = tk.Frame(row, bg=self.CARD_BG)
        line.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=2)

        def lbl(text, fg=None, bold=False):
            if not text:
                return
            tk.Label(
                line, text=text, bg=self.CARD_BG,
                fg=fg or self.TEXT_CLR,
                font=("Arial", 10, "bold" if bold else "normal"),
                wraplength=0
            ).pack(side=tk.LEFT)

        lbl(base)
        for item in extras:
            txt, clr, is_bold = (item if len(item) == 3
                                 else (item[0], item[1], False))
            lbl(txt, fg=clr, bold=is_bold)

    # ──────────────────────────────────────────────────────────
    #  FOOTER — Nút ĐÃ HIỂU (CTkButton)
    # ──────────────────────────────────────────────────────────

    def _build_footer(self, parent):
        footer = tk.Frame(parent, bg=self.FOOTER_BG, pady=16)
        footer.pack(fill=tk.X)

        ctk.CTkButton(
            footer,
            text="ĐÃ HIỂU",
            command=self._close,
            width=190,
            height=46,
            fg_color=self.BTN_BG,
            hover_color=self.BTN_HOV,
            text_color="white",
            font=("Arial", 13, "bold"),
            corner_radius=25,
            border_width=0,
            bg_color=self.FOOTER_BG,
        ).pack()

    # ──────────────────────────────────────────────────────────

    def _close(self):
        try:
            self.grab_release()
            self.destroy()
        except Exception:
            pass
