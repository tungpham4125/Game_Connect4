"""
=============================================================
frames/base_frame.py - Lớp cơ sở cho mọi Frame
=============================================================
Mọi Frame trong thư mục frames/ đều kế thừa từ BaseFrame.
BaseFrame nhận controller (Connect4App) và expose helper
methods tái sử dụng như rounded_rect_pts().
=============================================================
"""

import tkinter as tk
import math


class BaseFrame(tk.Frame):
    """
    Lớp cơ sở cho MainMenuFrame, GameFrame, v.v.

    __init__ nhận:
        parent     : widget cha (thường là container trong App)
        controller : instance của Connect4App (Controller)
    """

    def __init__(self, parent: tk.Widget, controller):
        super().__init__(parent, bg="#111122")
        self.controller = controller   # Tham chiếu tới App chính

    # ──────────────────────────────────────────────────────────
    #  HELPER: VẼ POLYGON BO GÓC (dùng chung toàn project)
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def rounded_rect_pts(x1: float, y1: float,
                         x2: float, y2: float, r: float) -> list:
        """
        Tạo danh sách điểm polygon bo góc.

        Không dùng alpha color — hoàn toàn tương thích Tkinter.
        """
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
                pts.extend([ax + r * math.cos(rad),
                             ay + r * math.sin(rad)])
        return pts

    @staticmethod
    def lighten(hex_color: str, amount: int = 30) -> str:
        """Làm sáng màu hex lên n đơn vị (dùng cho hover effect)."""
        hx = hex_color.lstrip("#")
        r = min(255, int(hx[0:2], 16) + amount)
        g = min(255, int(hx[2:4], 16) + amount)
        b = min(255, int(hx[4:6], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"
