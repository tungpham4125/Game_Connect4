"""
=============================================================
MAIN.PY - Controller: Ứng dụng chính (Connect4App)
=============================================================
• Kế thừa tk.Tk
• Giữ instance duy nhất của GameLogic
• Quản lý chuyển đổi giữa các Frame qua show_frame()
• Mọi Frame giao tiếp với game qua self.controller (= App này)

Chạy: python main.py
=============================================================
"""

import tkinter as tk
from tkinter import font as tkfont

from config import (
    BOARD_W, BOARD_H, PAD_X, PAD_Y,
    COLOR_BG
)
from logic import GameLogic

# Import tất cả Frame từ package frames/
from frames.menu         import MainMenuFrame
from frames.gameplay     import GameFrame
from frames.instructions import InstructionsModal


# ─────────────────────────────────────────────────────────────
#  MAP TÊN → CLASS (dùng trong show_frame)
# ─────────────────────────────────────────────────────────────
FRAME_MAP = {
    "MainMenuFrame": MainMenuFrame,
    "GameFrame":     GameFrame,
}


class Connect4App(tk.Tk):
    """
    Controller trung tâm của game Connect 4.

    Trách nhiệm:
      ┌──────────────────────────────────────────────┐
      │  1. Khởi tạo cửa sổ và font                 │
      │  2. Giữ 1 instance GameLogic (self.logic)   │
      │  3. Chứa container (tk.Frame) full-size       │
      │     để đặt các Frame con lên đó              │
      │  4. show_frame(name) → tkraise() Frame đó    │
      │  5. start_game(mode) → tạo GameFrame mới     │
      │  6. show_instructions() → mở modal           │
      └──────────────────────────────────────────────┘

    Các Frame liên lạc ngược bằng cách gọi:
        self.controller.show_frame("MainMenuFrame")
        self.controller.start_game("pve")
        self.controller.logic.drop_piece(...)
    """

    def __init__(self):
        super().__init__()
        self.title("Connect 4 — Arcade Edition")

        # Kích thước cửa sổ
        win_w = BOARD_W + PAD_X * 2 + 200
        win_h = BOARD_H + PAD_Y * 4 + 100
        self.geometry(f"{win_w}x{win_h}")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)

        # ── Font hệ thống ──
        self._load_fonts()

        # ── Model duy nhất: GameLogic ──
        self.logic = GameLogic()

        # ── Container chứa tất cả Frame ──
        self._container = tk.Frame(self, bg=COLOR_BG)
        self._container.pack(fill=tk.BOTH, expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        # Lưu các frame đã tạo (không tạo lại nếu đã có)
        self._frames: dict[str, tk.Frame] = {}

        # Khởi đầu tại Main Menu
        self.show_frame("MainMenuFrame")

    # ──────────────────────────────────────────────────────────
    #  FONT
    # ──────────────────────────────────────────────────────────

    def _load_fonts(self):
        """Nạp các font dùng chung toàn app."""
        self.font_title  = tkfont.Font(family="Arial", size=32, weight="bold")
        self.font_btn    = tkfont.Font(family="Arial", size=14, weight="bold")
        self.font_label  = tkfont.Font(family="Arial", size=11, weight="bold")
        self.font_timer  = tkfont.Font(family="Courier", size=12, weight="bold")

    # ──────────────────────────────────────────────────────────
    #  ĐIỀU PHỐI FRAME (Controller Pattern)
    # ──────────────────────────────────────────────────────────

    def show_frame(self, name: str):
        """
        Chuyển sang Frame có tên name (string).

        Nếu Frame chưa tồn tại → tạo mới và đặt vào grid.
        Nếu đã tồn tại → tkraise() để đưa lên trước.

        Lưu ý: MainMenuFrame được tạo lại mỗi lần (để reset animation).
                GameFrame được tạo bởi start_game() với tham số mode.
        """
        # Luôn tạo lại MainMenuFrame khi quay về (để reset animation coin)
        if name == "MainMenuFrame" and name in self._frames:
            old = self._frames.pop(name)
            old.destroy()

        if name not in self._frames:
            FrameClass = FRAME_MAP[name]
            frame = FrameClass(parent=self._container, controller=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self._frames[name] = frame

        self._frames[name].tkraise()

    def start_game(self, mode: str = "pve"):
        """
        Bắt đầu ván chơi mới.
        Tạo lại GameFrame mỗi lần để reset hoàn toàn.
        """
        self.logic.reset()

        # Hủy GameFrame cũ nếu có
        if "GameFrame" in self._frames:
            old = self._frames.pop("GameFrame")
            old.destroy()

        frame = GameFrame(parent=self._container,
                          controller=self,
                          mode=mode)
        frame.grid(row=0, column=0, sticky="nsew")
        self._frames["GameFrame"] = frame
        frame.tkraise()

    def show_instructions(self):
        """Mở modal Hướng dẫn chơi."""
        InstructionsModal(parent=self)


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = Connect4App()
    app.mainloop()
