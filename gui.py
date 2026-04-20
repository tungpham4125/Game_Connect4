"""
=============================================================
GUI.PY - View: Giao diện Tkinter (Classes & Event Handlers)
=============================================================
Import: tkinter, config.py, logic.py, ai.py
=============================================================
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import math

from config import (
    ROWS, COLS, EMPTY, PLAYER_1, PLAYER_2,
    CELL_SIZE, RADIUS, PAD_X, PAD_Y, BOARD_W, BOARD_H,
    COLOR_BG, COLOR_BOARD, COLOR_BOARD_LIGHT, COLOR_EMPTY,
    COLOR_P1, COLOR_P2, COLOR_WIN_GLOW, COLOR_TEXT, COLOR_ACCENT,
    COLOR_TIMER_BG, COLOR_BTN_PVP, COLOR_BTN_PVE, COLOR_BTN_ONLINE,
    COLOR_BTN_EXIT, COLOR_PAUSE_BG, COLOR_BTN_BLUE,
    AI_DEPTH, TIMER_SECONDS
)
from logic import (
    create_board, is_valid_column, get_next_open_row,
    drop_piece, check_win, is_board_full, get_valid_columns
)
from ai import get_best_ai_move


# ─────────────────────────────────────────────────────────────
#  HELPER: VẼ HÌNH CHỮ NHẬT BO GÓC (KHÔNG DÙNG ALPHA)
# ─────────────────────────────────────────────────────────────

def rounded_rect_pts(x1, y1, x2, y2, r):
    """Trả về danh sách điểm polygon bo góc (không cần alpha)."""
    pts = []
    corners = [
        (180, x1 + r, y1 + r),
        (270, x2 - r, y1 + r),
        (0,   x2 - r, y2 - r),
        (90,  x1 + r, y2 - r),
    ]
    for a_start, ax, ay in corners:
        for a in range(a_start, a_start + 91, 12):
            rad = math.radians(a)
            pts.extend([ax + r * math.cos(rad), ay + r * math.sin(rad)])
    return pts


# ─────────────────────────────────────────────────────────────
#  ỨNG DỤNG CHÍNH
# ─────────────────────────────────────────────────────────────

class Connect4App(tk.Tk):
    """Lớp ứng dụng chính - quản lý chuyển đổi giữa các màn hình."""

    def __init__(self):
        super().__init__()
        self.title("Connect 4")
        win_w = BOARD_W + PAD_X * 2 + 200
        win_h = BOARD_H + PAD_Y * 4 + 100
        self.geometry(f"{win_w}x{win_h}")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.current_frame = None
        self._load_fonts()
        self.show_main_menu()

    def _load_fonts(self):
        """Nạp các font chữ tùy chỉnh."""
        self.font_title  = tkfont.Font(family="Arial", size=32, weight="bold")
        self.font_btn    = tkfont.Font(family="Arial", size=14, weight="bold")
        self.font_label  = tkfont.Font(family="Arial", size=11, weight="bold")
        self.font_timer  = tkfont.Font(family="Courier", size=12, weight="bold")
        self.font_winner = tkfont.Font(family="Arial", size=14, weight="bold")

    def show_frame(self, FrameClass, **kwargs):
        """Chuyển sang màn hình FrameClass, hủy màn hình cũ."""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = FrameClass(self, **kwargs)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_main_menu(self):
        """Hiển thị màn hình Main Menu."""
        self.show_frame(MainMenuFrame)

    def start_game(self, mode: str):
        """Bắt đầu ván chơi với chế độ 'pvp' hoặc 'pve'."""
        self.show_frame(GameFrame, mode=mode)


# ─────────────────────────────────────────────────────────────
#  MÀN HÌNH 1: MAIN MENU - ARCADE STYLE
#  (Thiết kế theo React component đã cung cấp)
# ─────────────────────────────────────────────────────────────

class MainMenuFrame(tk.Frame):
    """
    Main Menu Arcade Style:
    - Nền #111122 (dark navy) + lưới chấm bi trắng mờ
    - Vòng tròn Đỏ và Vàng lơ lửng với hiệu ứng glow (animation)
    - Tiêu đề CONNECT (vàng-cam) / FOUR (đỏ sẫm) có shadow
    - 3 nút 3D nổi khối: CHƠI VỚI MÁY (xanh lá), HƯỚNG DẪN (xanh dương), THOÁT (đỏ)
    """

    # ── Màu sắc (khớp với React) ──────────────────────────────
    BG            = "#111122"

    # Nút xanh lá
    BTN_G_TOP     = "#4ADE80"
    BTN_G_BOT     = "#22C55E"
    BTN_G_SHADOW  = "#166534"

    # Nút xanh dương
    BTN_B_TOP     = "#38BDF8"
    BTN_B_BOT     = "#0284C7"
    BTN_B_SHADOW  = "#075985"

    # Nút đỏ
    BTN_R_TOP     = "#F87171"
    BTN_R_BOT     = "#DC2626"
    BTN_R_SHADOW  = "#7F1D1D"

    # Tiêu đề
    CONNECT_TOP   = "#FFD54F"
    CONNECT_BOT   = "#FF8F00"
    FOUR_TOP      = "#EF5350"
    FOUR_BOT      = "#B71C1C"

    # Vòng tròn lơ lửng: (cx_ratio, cy_ratio, radius, fill, glow_color, anim_type, phase, speed)
    # anim_type: "pulse" hoặc "bob"
    CIRCLES = [
        (0.10, 0.18, 48, "#DC2626", "#DC2626", "pulse", 0.0,  0.08),   # Top-left đỏ lớn
        (0.06, 0.35, 24, "#7F1D1D", "#7F1D1D", "bob",   1.2,  0.05),   # Top-left đỏ nhỏ
        (0.15, 0.75, 64, "#EAB308", "#EAB308", "bob",   2.1,  0.04),   # Bottom-left vàng
        (0.88, 0.18, 40, "#EAB308", "#EAB308", "bob",   0.7,  0.06),   # Top-right vàng
        (0.84, 0.12, 56, "#CA8A04", "#CA8A04", "pulse", 1.8,  0.05),   # Top-right vàng đậm
        (0.87, 0.72, 72, "#DC2626", "#DC2626", "pulse", 0.5,  0.07),   # Bottom-right đỏ
    ]

    def __init__(self, master: Connect4App):
        super().__init__(master, bg=self.BG)
        self.master = master

        # Trạng thái animation
        self._phases   = [c[6] for c in self.CIRCLES]
        self._pulse_sc = [1.0] * len(self.CIRCLES)   # scale factor cho pulse
        self._anim_id  = None

        self._build()
        # Vẽ ngay sau khi widget sẵn sàng
        self.after(20, self._first_render)

    # ── Build ──────────────────────────────────────────────────

    def _build(self):
        """Tạo canvas full-size để vẽ toàn bộ menu."""
        self.canvas = tk.Canvas(
            self, bg=self.BG,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

    def _first_render(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            self.after(30, self._first_render)
            return
        self._render_static(w, h)
        self._animate()

    def _on_resize(self, event):
        self._render_static(event.width, event.height)

    # ── Nền tĩnh (gradient + dotted grid + tiêu đề + nút) ────

    def _render_static(self, w, h):
        """Vẽ lại toàn bộ phần tĩnh."""
        self.canvas.delete("static")

        # 1. Gradient nền navy
        self._draw_gradient(w, h)

        # 2. Lưới chấm bi trắng mờ (spacing 24px như React)
        self._draw_dots(w, h)

        # 3. Tiêu đề CONNECT / FOUR
        cx = w // 2
        title_y_connect = int(h * 0.22)
        title_y_four    = title_y_connect + 68
        self._draw_title(cx, title_y_connect, title_y_four)

        # 4. Các nút 3D
        btn_w = int(w * 0.46)
        btn_w = max(btn_w, 260)
        btn_h = 52
        shadow_h = 6
        btn_cx = cx
        btn_y0 = int(h * 0.52)
        gap    = 72

        self._draw_button(
            btn_cx, btn_y0, btn_w, btn_h, shadow_h,
            "CHƠI VỚI MÁY",
            self.BTN_G_TOP, self.BTN_G_BOT, self.BTN_G_SHADOW,
            lambda: self.master.start_game("pve"),
            tag="btn_play"
        )
        self._draw_button(
            btn_cx, btn_y0 + gap, btn_w, btn_h, shadow_h,
            "HƯỚNG DẪN",
            self.BTN_B_TOP, self.BTN_B_BOT, self.BTN_B_SHADOW,
            self._show_instructions,
            tag="btn_help"
        )
        self._draw_button(
            btn_cx, btn_y0 + gap * 2, btn_w, btn_h, shadow_h,
            "THOÁT",
            self.BTN_R_TOP, self.BTN_R_BOT, self.BTN_R_SHADOW,
            self.master.quit,
            tag="btn_exit"
        )

    # ── Vẽ nền ────────────────────────────────────────────────

    def _draw_gradient(self, w, h):
        """Gradient nhẹ từ #111122 xuống #080814."""
        step = 6
        c1 = (0x11, 0x11, 0x22)
        c2 = (0x08, 0x08, 0x14)
        for i in range(0, h, step):
            t = i / h
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            self.canvas.create_rectangle(
                0, i, w, min(i + step, h),
                fill=f"#{r:02x}{g:02x}{b:02x}", outline="",
                tags="static"
            )

    def _draw_dots(self, w, h):
        """Lưới chấm bi trắng mờ — spacing 24px (như React backgroundSize)."""
        DOT_SPACING = 24
        DOT_COLOR   = "#1D1D3A"   # mờ hơn white để giống opacity-40 trong React
        for gx in range(0, w + DOT_SPACING, DOT_SPACING):
            for gy in range(0, h + DOT_SPACING, DOT_SPACING):
                self.canvas.create_oval(
                    gx - 1, gy - 1, gx + 1, gy + 1,
                    fill=DOT_COLOR, outline="",
                    tags="static"
                )

    # ── Tiêu đề ───────────────────────────────────────────────

    def _draw_title(self, cx, y_connect, y_four):
        """Vẽ CONNECT (vàng-cam) và FOUR (đỏ sẫm) với shadow."""

        font_c = ("Impact", 56, "bold")
        font_f = ("Impact", 46, "bold")

        # --- CONNECT ---
        # Shadow tối 3 lớp
        for dx, dy in [(4, 4), (3, 3), (2, 2)]:
            self.canvas.create_text(
                cx + dx, y_connect + dy, text="CONNECT",
                font=font_c, fill="#1A0800", tags="static"
            )
        # Lớp đáy (cam đậm) giả gradient bottom
        self.canvas.create_text(
            cx, y_connect + 6, text="CONNECT",
            font=font_c, fill=self.CONNECT_BOT, tags="static"
        )
        # Lớp top (vàng nhạt)
        self.canvas.create_text(
            cx, y_connect, text="CONNECT",
            font=font_c, fill=self.CONNECT_TOP, tags="static"
        )

        # --- FOUR ---
        for dx, dy in [(4, 4), (3, 3), (2, 2)]:
            self.canvas.create_text(
                cx + dx, y_four + dy, text="FOUR",
                font=font_f, fill="#1A0000", tags="static"
            )
        self.canvas.create_text(
            cx, y_four + 5, text="FOUR",
            font=font_f, fill=self.FOUR_BOT, tags="static"
        )
        self.canvas.create_text(
            cx, y_four, text="FOUR",
            font=font_f, fill=self.FOUR_TOP, tags="static"
        )

    # ── Nút 3D nổi khối ───────────────────────────────────────

    def _draw_button(self, cx, cy, w, h, sh,
                     label, c_top, c_bot, c_shadow,
                     command, tag):
        """
        Vẽ nút 3D bo góc (giống React: lớp bóng bên dưới + lớp mặt nổi).
        c_top   : màu gradient top (sáng)
        c_bot   : màu gradient bottom (tối hơn)
        c_shadow: màu đế bóng 3D (tối nhất)
        """
        x1 = cx - w // 2
        y1 = cy - h // 2
        x2 = cx + w // 2
        y2 = cy + h // 2
        r  = 12   # bo góc

        group = f"grp_{tag}"

        def render(pressed=False):
            self.canvas.delete(group)
            dy_face = sh - 2 if pressed else 0   # Lún xuống khi nhấn

            # --- Lớp bóng đế 3D (luôn cố định) ---
            if not pressed:
                s_pts = rounded_rect_pts(x1, y1 + sh, x2, y2 + sh, r)
                self.canvas.create_polygon(
                    s_pts, fill=c_shadow, outline="",
                    smooth=True, tags=(group, "static")
                )

            # --- Lớp mặt nút (gradient 2 lớp: top sáng + bottom tối) ---
            # Bottom (đậm hơn)
            f_pts_b = rounded_rect_pts(x1, y1 + dy_face, x2, y2 + dy_face, r)
            self.canvas.create_polygon(
                f_pts_b, fill=c_bot, outline="",
                smooth=True, tags=(group, "static")
            )
            # Top half: sáng hơn (giả gradient bằng cách che 1/2 trên)
            top_h = (y2 - y1) // 2
            f_pts_t = rounded_rect_pts(x1, y1 + dy_face, x2, y1 + dy_face + top_h, r)
            self.canvas.create_polygon(
                f_pts_t, fill=c_top, outline="",
                smooth=True, tags=(group, "static")
            )

            # --- Viền mỏng trên cùng (sáng hơn một chút) ---
            bdr_pts = rounded_rect_pts(x1, y1 + dy_face, x2, y2 + dy_face, r)
            self.canvas.create_polygon(
                bdr_pts, fill="", outline=c_shadow, width=1,
                smooth=True, tags=(group, "static")
            )

            # --- Chữ ---
            ty = cy + dy_face
            # Drop shadow chữ
            self.canvas.create_text(
                cx + 1, ty + 2, text=label,
                font=("Arial", 14, "bold"), fill="#333333",
                tags=(group, "static")
            )
            self.canvas.create_text(
                cx, ty, text=label,
                font=("Arial", 14, "bold"), fill="white",
                tags=(group, "static")
            )

        render(pressed=False)

        # ── Sự kiện hover / click ──
        def on_enter(e):
            # Làm sáng nhẹ: vẽ lại
            render(pressed=False)

        def on_press(e):
            render(pressed=True)

        def on_release(e):
            render(pressed=False)
            if command:
                self.master.after(80, command)

        self.canvas.tag_bind(group, "<Enter>",          on_enter)
        self.canvas.tag_bind(group, "<ButtonPress-1>",   on_press)
        self.canvas.tag_bind(group, "<ButtonRelease-1>", on_release)

    # ── Animation vòng tròn lơ lửng ───────────────────────────

    def _animate(self):
        """Vòng lặp animation ~30 FPS cho các đồng xu lơ lửng."""
        if not self.winfo_exists():
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            self._anim_id = self.after(50, self._animate)
            return

        self.canvas.delete("anim")

        for i, (cx_r, cy_r, radius, fill, glow, anim, phase0, speed) in enumerate(self.CIRCLES):
            self._phases[i] += speed
            ph = self._phases[i]

            # Glow (lớp ngoài to hơn, mờ bằng stipple)
            bx = cx_r * w + math.cos(ph * 0.6) * 10
            by = cy_r * h + math.sin(ph) * 14

            # Lớp glow ngoài lớn (dùng stipple để mô phỏng mờ)
            gr = int(radius * 1.45)
            self.canvas.create_oval(
                bx - gr, by - gr, bx + gr, by + gr,
                fill=glow, outline="", stipple="gray12",
                tags="anim"
            )

            # Lớp glow giữa
            mr = int(radius * 1.18)
            self.canvas.create_oval(
                bx - mr, by - mr, bx + mr, by + mr,
                fill=glow, outline="", stipple="gray25",
                tags="anim"
            )

            # Mặt chính
            self.canvas.create_oval(
                bx - radius, by - radius,
                bx + radius, by + radius,
                fill=fill, outline="",
                tags="anim"
            )

            # Highlight nhỏ trên
            hl = int(radius * 0.28)
            hx = bx - radius * 0.22
            hy = by - radius * 0.28
            self.canvas.create_oval(
                hx - hl, hy - hl, hx + hl, hy + hl,
                fill="white", outline="", stipple="gray50",
                tags="anim"
            )

        # Đưa animations xuống dưới nội dung tĩnh
        self.canvas.tag_lower("anim")

        self._anim_id = self.after(33, self._animate)

    def destroy(self):
        """Hủy animation khi frame bị destroy."""
        if self._anim_id:
            self.after_cancel(self._anim_id)
        super().destroy()

    # ── Mở modal hướng dẫn ────────────────────────────────────

    def _show_instructions(self):
        """Mở Custom Modal Hướng dẫn chơi đồng bộ Arcade theme."""
        InstructionsModal(self.master)


# ─────────────────────────────────────────────────────────────
#  CUSTOM MODAL: HƯỚNG DẪN CHƠI (ARCADE THEME)
#  Không dùng messagebox mặc định.
#  Toplevel + overrideredirect(True) để ẩn thanh tiêu đề Windows.
# ─────────────────────────────────────────────────────────────

class InstructionsModal(tk.Toplevel):
    """
    Hộp thoại Hướng dẫn chơi tùy chỉnh — đồng bộ Arcade theme.
    Thiết kế khớp với React modal đã cung cấp:
      - Nền gradient from #1E1E3F to #111122
      - Viền vàng (yellow-500)
      - Header: icon ℹ + tiêu đề vàng + nút X
      - 4 bước với số thứ tự màu (1=đỏ, 2-3=xám viền, 4=xanh lá)
      - Tip box: nền vàng nhạt, chữ nghiêng
      - Nút "ĐÃ HIỂU" 3D xanh dương ở footer
    """

    # Palette
    BG_TOP     = "#1E1E3F"
    BG_BOT     = "#111122"
    BORDER     = "#EAB308"        # yellow-500
    HEADER_BG  = "#0D0D1A"        # black/30 xấp xỉ
    TITLE_CLR  = "#FACC15"        # yellow-400
    TEXT_CLR   = "#E5E7EB"        # gray-200
    SEP_CLR    = "#1E1E3F"      # white/10 → dùng màu gần nhất
    TIP_BG     = "#2A2200"        # yellow-500/10 xấp xỉ
    TIP_BORDER = "#A16207"        # yellow-500/30
    TIP_TEXT   = "#FEF08A"        # yellow-200
    CLOSE_CLR  = "#9CA3AF"        # gray-400
    FOOTER_BG  = "#0A0A16"        # black/40

    # Số thứ tự
    NUM_BG  = ["#EF4444", "#1E1E3F", "#1E1E3F", "#22C55E"]
    NUM_BD  = ["",        "#6B7280", "#6B7280", ""]

    # Kích thước
    W, H = 460, 530

    def __init__(self, parent: Connect4App):
        super().__init__(parent)
        self.parent = parent

        # Ẩn thanh tiêu đề Windows
        self.overrideredirect(True)

        self.configure(bg=self.BORDER)   # Viền vàng bên ngoài
        self.resizable(False, False)

        self._center()
        self._build()

        self.lift()
        self.grab_set()
        self.focus_set()

        # Cho phép kéo modal
        self._dx = self._dy = 0

    def _center(self):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - self.W) // 2
        y = (sh - self.H) // 2
        self.geometry(f"{self.W}x{self.H}+{x}+{y}")

    # ── Layout ────────────────────────────────────────────────

    def _build(self):
        """Xây dựng toàn bộ giao diện modal."""

        # Viền ngoài (vàng) = frame to nhất; inner = nội dung
        outer = tk.Frame(self, bg=self.BORDER, padx=2, pady=2)
        outer.pack(fill=tk.BOTH, expand=True)

        # Canvas cho gradient nền
        self.bg_canvas = tk.Canvas(outer, bg=self.BG_BOT,
                                   highlightthickness=0,
                                   width=self.W - 4, height=self.H - 4)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Vẽ gradient trên canvas nền sau khi visible
        self.after(10, self._draw_bg_gradient)

        # Inner container (trong suốt bg – dùng bg=BG_BOT để đồng màu)
        inner = tk.Frame(outer, bg=self.BG_TOP)
        inner.pack(fill=tk.BOTH, expand=True)

        # ── Header ──
        self._build_header(inner)

        # Đường kẻ ngang
        tk.Frame(inner, bg=self.BORDER, height=1).pack(fill=tk.X)

        # ── Nội dung ──
        self._build_content(inner)

        # ── Footer ──
        self._build_footer(inner)

        # Kéo modal bằng header
        inner.bind("<ButtonPress-1>",   self._drag_start)
        inner.bind("<B1-Motion>",       self._drag_motion)

    def _draw_bg_gradient(self):
        """Vẽ gradient nền trên canvas."""
        try:
            w = self.bg_canvas.winfo_width()
            h = self.bg_canvas.winfo_height()
            if w < 2 or h < 2:
                self.after(20, self._draw_bg_gradient)
                return
            c1 = (0x1E, 0x1E, 0x3F)
            c2 = (0x11, 0x11, 0x22)
            step = 4
            for i in range(0, h, step):
                t = i / h
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                self.bg_canvas.create_rectangle(
                    0, i, w, i + step,
                    fill=f"#{r:02x}{g:02x}{b:02x}", outline=""
                )
        except Exception:
            pass

    def _drag_start(self, e):
        self._dx = e.x_root - self.winfo_x()
        self._dy = e.y_root - self.winfo_y()

    def _drag_motion(self, e):
        self.geometry(f"+{e.x_root - self._dx}+{e.y_root - self._dy}")

    # ── Header ────────────────────────────────────────────────

    def _build_header(self, parent):
        """Header: icon ℹ + tiêu đề HƯỚNG DẪN CHƠI + nút X."""
        hdr = tk.Frame(parent, bg=self.HEADER_BG, pady=12)
        hdr.pack(fill=tk.X, padx=0)

        # Kéo modal từ header
        hdr.bind("<ButtonPress-1>",   self._drag_start)
        hdr.bind("<B1-Motion>",       self._drag_motion)

        # Icon ℹ (nền vàng, chữ tối)
        icon = tk.Label(
            hdr, text=" ℹ ",
            bg=self.TITLE_CLR, fg=self.BG_BOT,
            font=("Arial", 12, "bold")
        )
        icon.pack(side=tk.LEFT, padx=(14, 8))

        # Tiêu đề
        tk.Label(
            hdr, text="HƯỚNG DẪN CHƠI",
            bg=self.HEADER_BG, fg=self.TITLE_CLR,
            font=("Arial", 15, "bold")
        ).pack(side=tk.LEFT)

        # Nút X đóng
        x_lbl = tk.Label(
            hdr, text=" ✕ ",
            bg=self.HEADER_BG, fg=self.CLOSE_CLR,
            font=("Arial", 14, "bold"),
            cursor="hand2"
        )
        x_lbl.pack(side=tk.RIGHT, padx=10)
        x_lbl.bind("<Button-1>",  lambda e: self._close())
        x_lbl.bind("<Enter>",     lambda e: x_lbl.config(fg="white",   bg="#7F1D1D"))
        x_lbl.bind("<Leave>",     lambda e: x_lbl.config(fg=self.CLOSE_CLR, bg=self.HEADER_BG))

    # ── Nội dung ──────────────────────────────────────────────

    def _build_content(self, parent):
        """4 bước hướng dẫn + tip box."""
        content = tk.Frame(parent, bg=self.BG_TOP, padx=16, pady=10)
        content.pack(fill=tk.BOTH, expand=True)

        steps = [
            # (phần_text_1,  [("chữ_highlight", màu), ...],  phần_text_2)
            (
                "Bạn sẽ cầm xu ",
                [("Đỏ", "#F87171"), (", ", self.TEXT_CLR),
                 ("Máy (AI) cầm xu ", self.TEXT_CLR),
                 ("Vàng", "#FACC15"), (".", self.TEXT_CLR)],
                ""
            ),
            (
                "Mỗi lượt, bạn click vào một cột trên bàn cờ để thả xu.",
                [], ""
            ),
            (
                "Xu sẽ tự động rơi xuống vị trí thấp nhất còn trống trong cột đó.",
                [], ""
            ),
            (
                "Người đầu tiên xếp được ",
                [("4 xu liên tiếp", "#4ADE80"),
                 (" (ngang, dọc, hoặc chéo) sẽ chiến thắng!", self.TEXT_CLR)],
                ""
            ),
        ]

        for idx, (base, extras, _) in enumerate(steps):
            num = idx + 1
            self._add_step(content, num, base, extras)

        # ── Tip Box ──
        self._build_tip(content)

    def _add_step(self, parent, num, base_text, extras):
        """Thêm một bước hướng dẫn với số thứ tự màu sắc."""
        row = tk.Frame(parent, bg=self.BG_TOP, pady=5)
        row.pack(fill=tk.X)

        # Hình tròn số thứ tự
        num_bg = self.NUM_BG[num - 1]
        num_bd = self.NUM_BD[num - 1]

        c = tk.Canvas(row, width=30, height=30,
                      bg=self.BG_TOP, highlightthickness=0)
        c.pack(side=tk.LEFT, padx=(0, 10), anchor=tk.N, pady=2)

        if num_bd:
            c.create_oval(1, 1, 29, 29, fill=num_bg, outline=num_bd, width=1)
        else:
            c.create_oval(1, 1, 29, 29, fill=num_bg, outline="")
        c.create_text(15, 15, text=str(num),
                      font=("Arial", 11, "bold"), fill="white")

        # Phần chữ inline (hỗ trợ màu highlight)
        txt_frame = tk.Frame(row, bg=self.BG_TOP)
        txt_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=2)

        line = tk.Frame(txt_frame, bg=self.BG_TOP)
        line.pack(anchor=tk.W, fill=tk.X)

        def add(text, fg=None, bold=False):
            if not text:
                return
            tk.Label(
                line, text=text,
                bg=self.BG_TOP, fg=fg or self.TEXT_CLR,
                font=("Arial", 10, "bold" if bold else "normal"),
                wraplength=0, anchor=tk.W
            ).pack(side=tk.LEFT)

        add(base_text)
        for part_text, part_clr in extras:
            is_bold = part_clr not in (self.TEXT_CLR,)
            add(part_text, part_clr, bold=is_bold)

    def _build_tip(self, parent):
        """Khung Mẹo (Tip Box) — nền vàng nhạt, chữ nghiêng."""
        outer = tk.Frame(parent, bg=self.TIP_BORDER, padx=1, pady=1)
        outer.pack(fill=tk.X, pady=(10, 0))

        inner = tk.Frame(outer, bg=self.TIP_BG, padx=12, pady=10)
        inner.pack(fill=tk.BOTH)

        row = tk.Frame(inner, bg=self.TIP_BG)
        row.pack(fill=tk.X)

        tk.Label(row, text="💡", bg=self.TIP_BG,
                 font=("Arial", 15)).pack(side=tk.LEFT, padx=(0, 8), anchor=tk.N)

        tk.Label(
            row,
            text=(
                "Mẹo: Thuật toán AI tính toán rất nhanh. Hãy liên tục "
                "quan sát xung quanh để chặn các đường chéo của nó "
                "trước khi quá muộn nhé!"
            ),
            bg=self.TIP_BG, fg=self.TIP_TEXT,
            font=("Arial", 10, "italic"),
            wraplength=340, justify=tk.LEFT
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    # ── Footer / Nút ĐÃ HIỂU ─────────────────────────────────

    def _build_footer(self, parent):
        """Footer: nền tối + nút ĐÃ HIỂU 3D màu xanh dương."""
        footer = tk.Frame(parent, bg=self.FOOTER_BG, pady=14)
        footer.pack(fill=tk.X)

        # Canvas để vẽ nút 3D
        BTN_W, BTN_H, SH = 170, 46, 4
        R = 10
        C_TOP    = "#38BDF8"
        C_BOT    = "#0284C7"
        C_SHADOW = "#075985"

        c = tk.Canvas(footer,
                      width=BTN_W + 4,
                      height=BTN_H + SH + 4,
                      bg=self.FOOTER_BG,
                      highlightthickness=0)
        c.pack()

        def draw(pressed=False):
            c.delete("all")
            dy = SH - 2 if pressed else 0

            # Bóng đế
            if not pressed:
                sp = rounded_rect_pts(0, SH, BTN_W, BTN_H + SH, R)
                c.create_polygon(sp, fill=C_SHADOW, outline="", smooth=True)

            # Mặt dưới (tối hơn)
            bp = rounded_rect_pts(0, dy, BTN_W, BTN_H + dy, R)
            c.create_polygon(bp, fill=C_BOT, outline="", smooth=True)

            # Mặt trên (sáng hơn — nửa trên)
            mid = BTN_H // 2
            tp = rounded_rect_pts(0, dy, BTN_W, dy + mid, R)
            c.create_polygon(tp, fill=C_TOP, outline="", smooth=True)

            # Chữ
            tx, ty = BTN_W // 2, BTN_H // 2 + dy
            c.create_text(tx + 1, ty + 2, text="ĐÃ HIỂU",
                          font=("Arial", 13, "bold"), fill="#222222")
            c.create_text(tx, ty, text="ĐÃ HIỂU",
                          font=("Arial", 13, "bold"), fill="white")

        draw()
        c.bind("<ButtonPress-1>",   lambda e: draw(True))
        c.bind("<ButtonRelease-1>", lambda e: [draw(False), self.after(80, self._close)])
        c.bind("<Enter>",           lambda e: c.configure(cursor="hand2"))

    # ── Đóng ─────────────────────────────────────────────────

    def _close(self):
        """Đóng và giải phóng grab."""
        try:
            self.grab_release()
            self.destroy()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  MÀN HÌNH 2: GAMEPLAY
# ─────────────────────────────────────────────────────────────

class GameFrame(tk.Frame):
    """Màn hình gameplay chính: bàn cờ, timer, pause, game-over."""

    def __init__(self, master: Connect4App, mode: str):
        super().__init__(master, bg=COLOR_BG)
        self.master    = master
        self.mode      = mode
        self.board     = create_board()
        self.turn      = PLAYER_1
        self.game_over = False
        self.paused    = False
        self.timer_val = TIMER_SECONDS
        self.timer_job = None

        self._build_layout()
        self._draw_board()
        self._start_timer()

    # ──────────────────────────────────
    #  XÂY DỰNG LAYOUT
    # ──────────────────────────────────

    def _build_layout(self):
        """Tạo layout: [P1 panel] [Board canvas] [P2 panel]."""
        self.lbl_turn = tk.Label(
            self, text="Player 1 turn",
            bg=COLOR_BG, fg=COLOR_TEXT,
            font=("Arial", 13, "bold")
        )
        self.lbl_turn.pack(pady=(10, 0))

        self.row_frame = tk.Frame(self, bg=COLOR_BG)
        self.row_frame.pack()

        self.p1_panel = self._build_player_panel(
            self.row_frame, "P1", COLOR_P1, is_active=True
        )
        self.p1_panel.pack(side=tk.LEFT, padx=10, pady=10)

        board_frame = tk.Frame(self.row_frame, bg=COLOR_BG)
        board_frame.pack(side=tk.LEFT)

        top_bar = tk.Frame(board_frame, bg=COLOR_BG)
        top_bar.pack(fill=tk.X)

        self.lbl_timer = tk.Label(
            top_bar, text=f"0:{self.timer_val:02d}",
            bg=COLOR_TIMER_BG, fg=COLOR_TEXT,
            font=("Courier", 11, "bold"),
            padx=6, pady=2
        )
        self.lbl_timer.pack(side=tk.LEFT, padx=5)

        self.btn_pause = tk.Button(
            top_bar, text="☰", bg="#333366", fg=COLOR_TEXT,
            font=("Arial", 14), bd=0, padx=5,
            command=self._toggle_pause
        )
        self.btn_pause.pack(side=tk.RIGHT, padx=5)

        self.canvas = tk.Canvas(
            board_frame,
            width=BOARD_W,
            height=BOARD_H,
            bg=COLOR_BOARD,
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)

        self.p2_panel = self._build_player_panel(
            self.row_frame, "P2", COLOR_P2, is_active=False
        )
        self.p2_panel.pack(side=tk.LEFT, padx=10, pady=10)

        self.panels = {PLAYER_1: self.p1_panel, PLAYER_2: self.p2_panel}

    def _build_player_panel(self, parent, label, color, is_active):
        """Tạo panel hiển thị thông tin người chơi."""
        border_color = COLOR_TEXT if is_active else "#333355"
        panel = tk.Frame(parent, bg=border_color,
                         width=70, height=90, pady=2, padx=2)
        panel.pack_propagate(False)

        inner = tk.Frame(panel, bg="#1A1A4E", width=66, height=86)
        inner.pack_propagate(False)
        inner.pack(fill=tk.BOTH, expand=True)

        disc = tk.Canvas(inner, width=50, height=50,
                         bg="#1A1A4E", highlightthickness=0)
        disc.pack(pady=(8, 0))
        disc.create_oval(5, 5, 45, 45, fill=color, outline="white", width=2)

        tk.Label(inner, text=label, bg="#1A1A4E", fg=COLOR_TEXT,
                 font=("Arial", 11, "bold")).pack()

        panel._inner = inner
        return panel

    def _set_active_player(self, player):
        """Cập nhật viền panel theo lượt."""
        for p, panel in self.panels.items():
            panel.configure(bg=COLOR_TEXT if p == player else "#333355")

        if player == PLAYER_1:
            self.lbl_turn.configure(text="Player 1 turn", fg=COLOR_TEXT)
        else:
            name = "AI turn" if self.mode == "pve" else "Player 2 turn"
            self.lbl_turn.configure(text=name, fg=COLOR_TEXT)

    # ──────────────────────────────────
    #  VẼ BÀN CỜ
    # ──────────────────────────────────

    def _draw_board(self, winning_cells=None):
        """Vẽ lại toàn bộ bàn cờ trên Canvas."""
        self.canvas.delete("all")
        win_set = set(winning_cells) if winning_cells else set()

        for r in range(ROWS):
            for c in range(COLS):
                cx = c * CELL_SIZE + CELL_SIZE // 2
                cy = r * CELL_SIZE + CELL_SIZE // 2
                piece = int(self.board[r][c])

                if piece == PLAYER_1:
                    fill = COLOR_P1
                elif piece == PLAYER_2:
                    fill = COLOR_P2
                else:
                    fill = COLOR_EMPTY

                is_win = (r, c) in win_set
                outline = COLOR_WIN_GLOW if is_win else "#0000AA"
                width   = 4 if is_win else 1

                self.canvas.create_oval(
                    cx - RADIUS, cy - RADIUS,
                    cx + RADIUS, cy + RADIUS,
                    fill=fill, outline=outline, width=width
                )

    def _draw_preview(self, col):
        """Vẽ preview xu mờ khi hover."""
        self._draw_board()
        if 0 <= col < COLS and is_valid_column(self.board, col):
            cx = col * CELL_SIZE + CELL_SIZE // 2
            cy = CELL_SIZE // 2
            color = COLOR_P1 if self.turn == PLAYER_1 else COLOR_P2
            self.canvas.create_oval(
                cx - RADIUS, cy - RADIUS,
                cx + RADIUS, cy + RADIUS,
                fill="#663333" if self.turn == PLAYER_1 else "#666600",
                outline=color, width=2, dash=(4, 4)
            )

    # ──────────────────────────────────
    #  XỬ LÝ SỰ KIỆN CLICK CHUỘT
    # ──────────────────────────────────

    def _on_click(self, event):
        """Xử lý click vào bàn cờ."""
        if self.game_over or self.paused:
            return
        if self.mode == "pve" and self.turn != PLAYER_1:
            return

        col = event.x // CELL_SIZE
        if not (0 <= col < COLS):
            return
        if not is_valid_column(self.board, col):
            self._flash_column_full(col)
            return

        self._make_move(col, self.turn)

    def _make_move(self, col, player):
        """Thực hiện nước đi: thả xu, kiểm tra thắng/hòa."""
        row = get_next_open_row(self.board, col)
        drop_piece(self.board, row, col, player)
        self._draw_board()

        winning = check_win(self.board, player)
        if winning:
            self._draw_board(winning_cells=winning)
            self._end_game(winner=player)
            return

        if is_board_full(self.board):
            self._end_game(winner=None)
            return

        self.turn = PLAYER_2 if player == PLAYER_1 else PLAYER_1
        self._set_active_player(self.turn)
        self._reset_timer()

        if self.mode == "pve" and self.turn == PLAYER_2:
            self.after(400, self._ai_move)

    def _ai_move(self):
        """Gọi AI tính toán và thực hiện nước đi."""
        if self.game_over or self.paused:
            return
        best_col = get_best_ai_move(self.board, depth=AI_DEPTH)
        self._make_move(best_col, PLAYER_2)

    # ──────────────────────────────────
    #  TIMER
    # ──────────────────────────────────

    def _start_timer(self):
        self._tick()

    def _tick(self):
        if self.game_over or self.paused:
            return
        self.lbl_timer.configure(text=f"0:{self.timer_val:02d}")
        if self.timer_val <= 0:
            self._on_timer_expired()
            return
        self.timer_val -= 1
        self.timer_job = self.after(1000, self._tick)

    def _reset_timer(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.timer_val = TIMER_SECONDS
        self.timer_job = self.after(1000, self._tick)

    def _on_timer_expired(self):
        if self.game_over:
            return
        valid = get_valid_columns(self.board)
        if not valid:
            return
        col = COLS // 2 if is_valid_column(self.board, COLS // 2) else random.choice(valid)
        self._make_move(col, self.turn)

    # ──────────────────────────────────
    #  PAUSE MENU
    # ──────────────────────────────────

    def _toggle_pause(self):
        if self.game_over:
            return
        if self.paused:
            self._resume_game()
        else:
            self._pause_game()

    def _pause_game(self):
        self.paused = True
        if self.timer_job:
            self.after_cancel(self.timer_job)

        self.pause_overlay = tk.Frame(self, bg=COLOR_PAUSE_BG)
        self.pause_overlay.place(
            x=self.canvas.winfo_x() + self.row_frame.winfo_x(),
            y=self.canvas.winfo_y() + self.row_frame.winfo_y() + 30,
            width=BOARD_W, height=BOARD_H
        )

        menu_frame = tk.Frame(self.pause_overlay, bg="#DD0066",
                               bd=3, relief=tk.RAISED)
        menu_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER,
                         width=200, height=180)

        tk.Label(menu_frame, text="PAUSE", bg="#DD0066", fg=COLOR_TEXT,
                  font=("Arial", 22, "bold"), pady=10).pack()

        self._pause_btn(menu_frame, "Resume", self._resume_game)
        self._pause_btn(menu_frame, "Reset",  self._reset_game)
        self._pause_btn(menu_frame, "Exit",   self.master.show_main_menu)

    def _pause_btn(self, parent, text, command):
        tk.Button(
            parent, text=text, command=command,
            bg=COLOR_BTN_BLUE, fg=COLOR_TEXT,
            font=("Arial", 11, "bold"),
            relief=tk.FLAT, padx=30, pady=4,
            activebackground="#0088FF",
            cursor="hand2"
        ).pack(pady=3)

    def _resume_game(self):
        if hasattr(self, "pause_overlay"):
            self.pause_overlay.destroy()
        self.paused = False
        self.timer_job = self.after(1000, self._tick)
        if self.mode == "pve" and self.turn == PLAYER_2:
            self.after(400, self._ai_move)

    # ──────────────────────────────────
    #  KẾT THÚC GAME
    # ──────────────────────────────────

    def _end_game(self, winner):
        """Kết thúc game: dừng timer, hiển thị kết quả."""
        self.game_over = True
        if self.timer_job:
            self.after_cancel(self.timer_job)

        if winner == PLAYER_1:
            msg = "P1 win!" if self.mode == "pvp" else "You win!"
            msg_color = COLOR_P1
        elif winner == PLAYER_2:
            msg = "P2 win!" if self.mode == "pvp" else "AI win!"
            msg_color = COLOR_P2
        else:
            msg = "Draw!"
            msg_color = "#AAAAAA"

        top  = self.canvas.winfo_y() + self.row_frame.winfo_y() + 25
        left = self.canvas.winfo_x() + self.row_frame.winfo_x()

        result_frame = tk.Frame(self, bg=COLOR_BG)
        result_frame.place(x=left, y=top - 30, width=BOARD_W)

        tk.Button(
            result_frame, text="Reset",
            command=self._reset_game,
            bg=COLOR_ACCENT, fg="black",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT, padx=10, cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)

        tk.Label(
            result_frame, text=msg,
            bg=msg_color, fg=COLOR_TEXT,
            font=("Arial", 12, "bold"),
            padx=10, pady=2
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            result_frame, text="Exit",
            command=self.master.show_main_menu,
            bg="#555555", fg=COLOR_TEXT,
            font=("Arial", 10, "bold"),
            relief=tk.FLAT, padx=10, cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)

        self.result_frame = result_frame

    def _reset_game(self):
        """Reset bàn cờ, bắt đầu ván mới."""
        if hasattr(self, "result_frame") and self.result_frame.winfo_exists():
            self.result_frame.destroy()
        if hasattr(self, "pause_overlay") and self.pause_overlay.winfo_exists():
            self.pause_overlay.destroy()

        self.board     = create_board()
        self.turn      = PLAYER_1
        self.game_over = False
        self.paused    = False
        self._set_active_player(PLAYER_1)
        self._draw_board()

        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.timer_val = TIMER_SECONDS
        self._start_timer()

    # ──────────────────────────────────
    #  HIỆU ỨNG PHỤ
    # ──────────────────────────────────

    def _flash_column_full(self, col):
        """Nhấp nháy đỏ khi cột đầy."""
        flash_id = self.canvas.create_rectangle(
            col * CELL_SIZE, 0,
            (col + 1) * CELL_SIZE, BOARD_H,
            fill="#FF0000", stipple="gray25", outline=""
        )
        self.after(300, lambda: self.canvas.delete(flash_id))
