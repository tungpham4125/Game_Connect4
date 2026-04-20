"""
=============================================================
frames/pause.py - Overlay Menu Tạm Dừng
=============================================================
PauseOverlay: một tk.Frame đặt chồng lên GameFrame
khi người chơi nhấn nút Pause.
=============================================================
"""

import tkinter as tk

from config import COLOR_TEXT, COLOR_BTN_BLUE, COLOR_PAUSE_BG, BOARD_W, BOARD_H


class PauseOverlay:
    """
    Menu tạm dừng đặt chồng lên bàn cờ.

    Không phải Frame riêng biệt — là overlay (tk.Frame.place)
    được tạo bên trong GameFrame khi cần và xóa khi resume.

    Giao tiếp:
        on_resume : callback → tiếp tục game
        on_reset  : callback → reset ván mới
        on_menu   : callback → về Main Menu
    """

    # ── Màu sắc ───────────────────────────────────────────────
    OVERLAY_BG = "#CC007799"   # Tạm dùng hex hợp lệ (không alpha)
    PANEL_BG   = "#DD0066"
    BTN_BG     = COLOR_BTN_BLUE
    BTN_FG     = COLOR_TEXT

    def __init__(self, parent: tk.Frame,
                 x: int, y: int, w: int, h: int,
                 on_resume, on_reset, on_menu):
        """
        Tạo overlay pause.

        Tham số:
            parent    : Frame cha (GameFrame)
            x, y      : Vị trí đặt overlay (tọa độ trong parent)
            w, h      : Kích thước overlay
            on_resume : Hàm gọi khi nhấn Resume
            on_reset  : Hàm gọi khi nhấn Reset
            on_menu   : Hàm gọi khi nhấn về Menu
        """
        self.on_resume = on_resume
        self.on_reset  = on_reset
        self.on_menu   = on_menu

        # Nền mờ đỏ hồng (stipple để tạo cảm giác trong suốt)
        self.overlay = tk.Frame(parent, bg=COLOR_PAUSE_BG)
        self.overlay.place(x=x, y=y, width=w, height=h)

        # Panel menu trung tâm
        panel = tk.Frame(self.overlay, bg=self.PANEL_BG, bd=3, relief=tk.RAISED)
        panel.place(relx=0.5, rely=0.4, anchor=tk.CENTER, width=220, height=200)

        # Tiêu đề PAUSE
        tk.Label(
            panel, text="PAUSE",
            bg=self.PANEL_BG, fg=COLOR_TEXT,
            font=("Arial", 22, "bold"), pady=10
        ).pack()

        # Các nút
        self._btn(panel, "▶  Resume", on_resume)
        self._btn(panel, "↺  Reset",  on_reset)
        self._btn(panel, "⌂  Menu",   on_menu)

    def _btn(self, parent: tk.Widget, text: str, command):
        """Tạo nút trong panel Pause."""
        tk.Button(
            parent, text=text, command=command,
            bg=self.BTN_BG, fg=self.BTN_FG,
            font=("Arial", 11, "bold"),
            relief=tk.FLAT, padx=30, pady=5,
            activebackground="#0088FF",
            cursor="hand2"
        ).pack(pady=3)

    def destroy(self):
        """Xóa overlay khỏi màn hình."""
        if self.overlay.winfo_exists():
            self.overlay.destroy()
