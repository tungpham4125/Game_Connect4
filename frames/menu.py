"""
=============================================================
frames/menu.py - Main Menu (Dark Theme + Glow Orbs + CTk)
=============================================================
Sử dụng:
  - tk.Canvas  : nền tối + lưới chấm + glow orbs (PIL blur)
  - CTkButton  : nút bấm bo góc đẹp với hover effect

ĐỂ CHỈNH SỬA:
  - Màu nền / chấm / tiêu đề / nút: sửa các hằng số bên dưới
  - Vị trí tiêu đề: chỉnh TITLE_Y_RATIO (0.0 → 1.0)
  - Vị trí nút đầu: chỉnh BTN_Y_RATIO
  - Khoảng cách nút: chỉnh BTN_GAP
=============================================================
"""

import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter, ImageTk

from frames.base_frame import BaseFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ─────────────────────────────────────────────────────────────
#  HELPER: Tạo glow orb bằng PIL GaussianBlur
# ─────────────────────────────────────────────────────────────

def _make_glow_orb(radius: int, color: str, bg_hex: str) -> ImageTk.PhotoImage:
    """
    Tạo ảnh vòng sáng mờ (glow) dùng PIL.
    Composite trực tiếp lên màu nền để hiển thị đúng trên Canvas.

    Tham số:
        radius  : bán kính vòng tròn chính (px)
        color   : màu hex vòng sáng (vd '#dd2200')
        bg_hex  : màu nền canvas để composite
    """
    size = radius * 4
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    h = color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    margin = radius
    draw.ellipse(
        [margin, margin, margin + radius * 2, margin + radius * 2],
        fill=(r, g, b, 230)
    )
    img = img.filter(ImageFilter.GaussianBlur(radius * 0.65))

    # Composite RGBA trên màu nền
    h2 = bg_hex.lstrip("#")
    br, bg_, bb = int(h2[0:2], 16), int(h2[2:4], 16), int(h2[4:6], 16)
    bg_img = Image.new("RGB", (size, size), (br, bg_, bb))
    bg_img.paste(img, mask=img.getchannel("A"))

    return ImageTk.PhotoImage(bg_img)


# ─────────────────────────────────────────────────────────────
#  MainMenuFrame
# ─────────────────────────────────────────────────────────────

class MainMenuFrame(BaseFrame):
    """
    Main Menu với nền dark navy, glow orbs, lưới chấm và CTkButton.

    Giao tiếp với controller:
      - self.controller.start_game("pve")   → bắt đầu game
      - self.controller.show_instructions() → mở hướng dẫn
      - self.controller.quit()              → thoát
    """

    # ── Màu sắc nền ───────────────────────────────────────────
    BG         = "#1a1a2e"    # Màu nền chính (dark navy)
    DOT_COLOR  = "#252545"    # Màu chấm lưới
    DOT_GAP    = 28           # Khoảng cách giữa các chấm (px)

    # ── Tiêu đề ───────────────────────────────────────────────
    TITLE1_CLR = "#f0a500"    # "CONNECT" - vàng cam
    TITLE1_SHD = "#6B4400"    # Bóng đổ CONNECT
    TITLE2_CLR = "#c0392b"    # "FOUR"    - đỏ đậm
    TITLE2_SHD = "#5a0000"    # Bóng đổ FOUR
    TITLE_Y_RATIO = 0.22      # Vị trí Y tiêu đề (0.0 = trên, 1.0 = dưới)

    # ── Glow Orbs: (rel_x, rel_y, radius, color) ──────────────
    ORBS = [
        (0.09, 0.20, 80,  "#dd2200"),   # Đỏ — góc trên trái
        (0.86, 0.13, 65,  "#cc8800"),   # Vàng — góc trên phải
        (0.12, 0.76, 72,  "#cc8800"),   # Vàng — góc dưới trái
        (0.88, 0.70, 88,  "#dd2200"),   # Đỏ — góc dưới phải
        (0.79, 0.40, 50,  "#dd2200"),   # Đỏ — phải giữa
    ]

    # ── Nút: (nhãn, fg_color, hover_color) ────────────────────
    BUTTONS = [
        ("CHƠI VỚI MÁY", "#2ecc71", "#27ae60"),
        ("HƯỚNG DẪN",     "#3498db", "#2980b9"),
        ("THOÁT",         "#e74c3c", "#c0392b"),
    ]
    BTN_W        = 300          # Chiều rộng nút (px)
    BTN_H        = 54           # Chiều cao nút  (px)
    BTN_GAP      = 70           # Khoảng cách giữa các nút
    BTN_RADIUS   = 30           # Độ bo góc
    BTN_Y_RATIO  = 0.52         # Vị trí Y nút đầu tiên

    # ──────────────────────────────────────────────────────────

    def __init__(self, parent: tk.Widget, controller):
        super().__init__(parent, controller)
        self.configure(bg=self.BG)

        self._orb_cache:   list = []   # [(cx, cy, PhotoImage), ...]
        self._btn_widgets: list = []   # [CTkButton, ...]
        self._btn_win_ids: list = []   # [canvas window item id, ...]
        self._last_size = (0, 0)

        self._build()
        self.after(30, self._first_render)

    # ──────────────────────────────────────────────────────────
    #  SETUP
    # ──────────────────────────────────────────────────────────

    def _build(self):
        """Tạo Canvas toàn màn hình."""
        self.canvas = tk.Canvas(self, bg=self.BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind(
            "<Configure>",
            lambda e: self._on_resize(e.width, e.height)
        )

    def _first_render(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 10 or h < 10:
            self.after(30, self._first_render)
            return
        self._last_size = (w, h)
        self._build_orbs(w, h)
        self._render(w, h)

    def _on_resize(self, w: int, h: int):
        if w < 10 or h < 10 or (w, h) == self._last_size:
            return
        self._last_size = (w, h)
        self._build_orbs(w, h)
        self._render(w, h)

    # ──────────────────────────────────────────────────────────
    #  PIL: TẠO GLOW ORBS
    # ──────────────────────────────────────────────────────────

    def _build_orbs(self, w: int, h: int):
        """Tạo ảnh glow orb cho từng orb, scale theo cửa sổ."""
        scale = max(w, h) / 700
        self._orb_cache = []
        for rx, ry, base_r, color in self.ORBS:
            r = max(25, int(base_r * scale))
            img = _make_glow_orb(r, color, self.BG)
            self._orb_cache.append((rx * w, ry * h, img))

    # ──────────────────────────────────────────────────────────
    #  VẼ
    # ──────────────────────────────────────────────────────────

    def _render(self, w: int, h: int):
        """Xóa và vẽ lại toàn bộ canvas (trừ button windows)."""
        self.canvas.delete("bg", "orb", "title")

        self._draw_dots(w, h)

        for cx, cy, img in self._orb_cache:
            self.canvas.create_image(
                cx, cy, image=img, anchor=tk.CENTER, tags="orb"
            )

        self._draw_title(w, h)
        self._sync_buttons(w, h)

        # Đảm bảo nút luôn ở trên
        self.canvas.tag_raise("btn_win")

    def _draw_dots(self, w: int, h: int):
        """Vẽ lưới chấm nhỏ trên nền."""
        g = self.DOT_GAP
        for x in range(0, w + g, g):
            for y in range(0, h + g, g):
                self.canvas.create_oval(
                    x - 1.5, y - 1.5, x + 1.5, y + 1.5,
                    fill=self.DOT_COLOR, outline="", tags="bg"
                )

    def _draw_title(self, w: int, h: int):
        """Vẽ tiêu đề CONNECT / FOUR với bóng đổ."""
        cx = w // 2
        y1 = int(h * self.TITLE_Y_RATIO)
        y2 = y1 + 68

        s1 = max(30, min(58, int(w / 13)))
        s2 = max(24, min(46, int(w / 17)))

        for dx, dy in [(3, 4), (2, 3)]:
            self.canvas.create_text(
                cx + dx, y1 + dy, text="CONNECT",
                font=("Impact", s1, "bold"),
                fill=self.TITLE1_SHD, tags="title"
            )
            self.canvas.create_text(
                cx + dx, y2 + dy, text="FOUR",
                font=("Impact", s2, "bold"),
                fill=self.TITLE2_SHD, tags="title"
            )

        self.canvas.create_text(
            cx, y1, text="CONNECT",
            font=("Impact", s1, "bold"),
            fill=self.TITLE1_CLR, tags="title"
        )
        self.canvas.create_text(
            cx, y2, text="FOUR",
            font=("Impact", s2, "bold"),
            fill=self.TITLE2_CLR, tags="title"
        )

    # ──────────────────────────────────────────────────────────
    #  NÚT (CTkButton)
    # ──────────────────────────────────────────────────────────

    def _sync_buttons(self, w: int, h: int):
        """
        Lần đầu: tạo CTkButton và nhúng vào canvas.
        Lần sau: chỉ di chuyển vị trí.
        """
        cx = w // 2
        y0 = int(h * self.BTN_Y_RATIO)

        commands = [
            lambda: self.controller.start_game("pve"),
            self.controller.show_instructions,
            self.controller.quit,
        ]

        if not self._btn_widgets:
            # Tạo nút lần đầu
            for i, (text, fg, hov) in enumerate(self.BUTTONS):
                btn = ctk.CTkButton(
                    self.canvas,
                    text=text,
                    command=commands[i],
                    width=self.BTN_W,
                    height=self.BTN_H,
                    fg_color=fg,
                    hover_color=hov,
                    text_color="white",
                    font=("Arial", 15, "bold"),
                    corner_radius=self.BTN_RADIUS,
                    border_width=0,
                    bg_color=self.BG,
                )
                wid = self.canvas.create_window(
                    cx, y0 + i * self.BTN_GAP,
                    window=btn, tags="btn_win",
                    width=self.BTN_W, height=self.BTN_H,
                )
                self._btn_widgets.append(btn)
                self._btn_win_ids.append(wid)
        else:
            # Chỉ dịch chuyển
            for i, wid in enumerate(self._btn_win_ids):
                self.canvas.coords(wid, cx, y0 + i * self.BTN_GAP)

    # ──────────────────────────────────────────────────────────

    def destroy(self):
        super().destroy()
