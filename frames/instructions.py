"""
=============================================================
frames/instructions.py - Modal Hướng Dẫn Chơi (Đơn giản)
=============================================================
Toplevel modal có thể kéo được (drag header để di chuyển).
Nút "ĐÃ HIỂU" là tk.Button thông thường — dễ chỉnh sửa.

ĐỂ CHỈNH SỬA:
  - Màu sắc : thay đổi các hằng số BG, BORDER, v.v. bên dưới
  - Kích thước: thay đổi W, H
=============================================================
"""

import tkinter as tk


class InstructionsModal(tk.Toplevel):
    """
    Hộp thoại Hướng dẫn chơi.
    Kéo bằng cách giữ chuột vào phần header tiêu đề.
    Nhấn ✕ hoặc "ĐÃ HIỂU" để đóng.
    """

    # ── Màu sắc (Chỉnh sửa tại đây) ──────────────────────────
    BG        = "#1E1E3F"    # Nền chính
    BORDER    = "#EAB308"    # Viền vàng
    HDR_BG    = "#0D0D1A"    # Nền header
    TITLE_CLR = "#FACC15"    # Màu tiêu đề
    TEXT_CLR  = "#E5E7EB"    # Màu văn bản
    CLOSE_CLR = "#9CA3AF"    # Màu nút ✕ (bình thường)
    TIP_BG    = "#2A2200"    # Nền hộp mẹo
    TIP_BD    = "#A16207"    # Viền hộp mẹo
    TIP_TEXT  = "#FEF08A"    # Chữ trong hộp mẹo
    FOOTER_BG = "#0A0A16"    # Nền footer
    BTN_BG    = "#0284C7"    # Màu nút ĐÃ HIỂU
    BTN_HOV   = "#075985"    # Màu nút khi hover

    # Màu vòng tròn số thứ tự bước
    NUM_BG = ["#EF4444", "#374151", "#374151", "#22C55E"]

    # ── Kích thước (Chỉnh sửa tại đây) ───────────────────────
    W, H = 460, 530

    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)   # Ẩn thanh tiêu đề Windows
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
        """Đặt modal ở giữa màn hình."""
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
        outer = tk.Frame(self, bg=self.BORDER, padx=2, pady=2)
        outer.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(outer, bg=self.BG)
        inner.pack(fill=tk.BOTH, expand=True)

        self._build_header(inner)
        tk.Frame(inner, bg=self.BORDER, height=1).pack(fill=tk.X)
        self._build_content(inner)
        self._build_footer(inner)

    # ──────────────────────────────────────────────────────────
    #  HEADER (kéo được)
    # ──────────────────────────────────────────────────────────

    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=self.HDR_BG, pady=12)
        hdr.pack(fill=tk.X)
        hdr.bind("<ButtonPress-1>", self._drag_start)
        hdr.bind("<B1-Motion>",     self._drag_do)

        tk.Label(
            hdr, text=" ℹ ", bg=self.TITLE_CLR, fg=self.BG,
            font=("Arial", 12, "bold")
        ).pack(side=tk.LEFT, padx=(14, 8))

        tk.Label(
            hdr, text="HƯỚNG DẪN CHƠI",
            bg=self.HDR_BG, fg=self.TITLE_CLR,
            font=("Arial", 15, "bold")
        ).pack(side=tk.LEFT)

        # Nút đóng ✕
        xl = tk.Label(
            hdr, text=" ✕ ",
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
        content = tk.Frame(parent, bg=self.BG, padx=16, pady=10)
        content.pack(fill=tk.BOTH, expand=True)

        steps = [
            (
                "Bạn sẽ cầm xu ",
                [("Đỏ", "#F87171"), (", Máy (AI) cầm xu ", self.TEXT_CLR),
                 ("Vàng", "#FACC15"), (".", self.TEXT_CLR)]
            ),
            ("Mỗi lượt, click vào một cột trên bàn cờ để thả xu.", []),
            ("Xu tự động rơi xuống vị trí thấp nhất còn trống.", []),
            (
                "Người đầu tiên xếp được ",
                [("4 xu liên tiếp", "#4ADE80"),
                 (" (ngang, dọc, chéo) sẽ chiến thắng!", self.TEXT_CLR)]
            ),
        ]

        for idx, (base, extras) in enumerate(steps):
            self._add_step(content, idx + 1, base, extras)

        # ── Hộp mẹo ───────────────────────────────────────────
        border_box = tk.Frame(content, bg=self.TIP_BD, padx=1, pady=1)
        border_box.pack(fill=tk.X, pady=(10, 0))

        tip_inner = tk.Frame(border_box, bg=self.TIP_BG, padx=12, pady=10)
        tip_inner.pack(fill=tk.BOTH)

        row = tk.Frame(tip_inner, bg=self.TIP_BG)
        row.pack(fill=tk.X)

        tk.Label(
            row, text="💡", bg=self.TIP_BG,
            font=("Arial", 15)
        ).pack(side=tk.LEFT, padx=(0, 8), anchor=tk.N)

        tk.Label(
            row,
            text=("Mẹo: Thuật toán AI tính toán rất nhanh. Hãy liên tục "
                  "quan sát để chặn các đường chéo trước khi quá muộn!"),
            bg=self.TIP_BG, fg=self.TIP_TEXT,
            font=("Arial", 10, "italic"),
            wraplength=340, justify=tk.LEFT
        ).pack(side=tk.LEFT, expand=True)

    def _add_step(self, parent, num: int, base: str, extras: list):
        """Thêm một bước hướng dẫn với số thứ tự và văn bản inline."""
        row = tk.Frame(parent, bg=self.BG, pady=5)
        row.pack(fill=tk.X)

        # Vòng tròn số
        c = tk.Canvas(row, width=30, height=30,
                      bg=self.BG, highlightthickness=0)
        c.pack(side=tk.LEFT, padx=(0, 10), anchor=tk.N, pady=2)
        c.create_oval(1, 1, 29, 29,
                      fill=self.NUM_BG[num - 1], outline="", width=0)
        c.create_text(15, 15, text=str(num),
                      font=("Arial", 11, "bold"), fill="white")

        # Văn bản inline
        line = tk.Frame(row, bg=self.BG)
        line.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=2)

        def lbl(text, fg=None, bold=False):
            if not text:
                return
            tk.Label(
                line, text=text, bg=self.BG,
                fg=fg or self.TEXT_CLR,
                font=("Arial", 10, "bold" if bold else "normal"),
                wraplength=0
            ).pack(side=tk.LEFT)

        lbl(base)
        for txt, clr in extras:
            lbl(txt, fg=clr, bold=(clr != self.TEXT_CLR))

    # ──────────────────────────────────────────────────────────
    #  FOOTER — Nút ĐÃ HIỂU
    # ──────────────────────────────────────────────────────────

    def _build_footer(self, parent):
        footer = tk.Frame(parent, bg=self.FOOTER_BG, pady=14)
        footer.pack(fill=tk.X)

        btn = tk.Button(
            footer,
            text="ĐÃ HIỂU",
            command=self._close,
            bg=self.BTN_BG,
            fg="white",
            font=("Arial", 13, "bold"),
            width=16,
            pady=7,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground=self.BTN_HOV,
            activeforeground="white",
            bd=0,
        )
        btn.pack()

    # ──────────────────────────────────────────────────────────
    #  ĐÓNG MODAL
    # ──────────────────────────────────────────────────────────

    def _close(self):
        try:
            self.grab_release()
            self.destroy()
        except Exception:
            pass
