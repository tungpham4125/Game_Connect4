"""
=============================================================
frames/menu.py - Màn hình Main Menu (Đơn giản, Dễ chỉnh sửa)
=============================================================
Giao diện menu sử dụng Tkinter widgets thuần túy.

ĐỂ CHỈNH SỬA:
  - Màu sắc : thay đổi các hằng số BG, TITLE1_FG, BTN_* bên dưới
  - Font    : thay đổi F_TITLE1, F_TITLE2, F_BTN
  - Thêm nút: gọi thêm self._make_btn(...) trong _build()
=============================================================
"""

import tkinter as tk

from frames.base_frame import BaseFrame


class MainMenuFrame(BaseFrame):
    """
    Main Menu đơn giản với Frame/Label/Button Tkinter thuần túy.
    Không dùng Canvas hay animation — dễ chỉnh sửa tùy ý.
    """

    # ── Màu sắc (Chỉnh sửa tại đây) ──────────────────────────
    BG         = "#111122"   # Màu nền toàn màn hình

    TITLE1_FG  = "#FFD54F"   # Màu chữ "CONNECT"
    TITLE2_FG  = "#EF5350"   # Màu chữ "FOUR"

    # Mỗi nút là (màu_nền, màu_chữ)
    BTN_PVE    = ("#22C55E", "white")   # Nút Chơi với Máy  (xanh lá)
    BTN_HELP   = ("#38BDF8", "white")   # Nút Hướng dẫn     (xanh dương)
    BTN_EXIT   = ("#EF4444", "white")   # Nút Thoát          (đỏ)

    # ── Font (Chỉnh sửa tại đây) ──────────────────────────────
    F_TITLE1   = ("Impact", 56, "bold")
    F_TITLE2   = ("Impact", 46, "bold")
    F_BTN      = ("Arial",  14, "bold")

    # ── Kích thước nút ────────────────────────────────────────
    BTN_WIDTH  = 22    # Số ký tự chiều ngang
    BTN_PADY   = 9     # Padding dọc bên trong nút
    BTN_SPACE  = 7     # Khoảng cách giữa các nút (pixel)

    def __init__(self, parent: tk.Widget, controller):
        super().__init__(parent, controller)
        self.configure(bg=self.BG)
        self._build()

    # ──────────────────────────────────────────────────────────
    #  BUILD LAYOUT
    # ──────────────────────────────────────────────────────────

    def _build(self):
        """Xây dựng layout: tiêu đề + 3 nút."""

        # Container căn giữa màn hình
        box = tk.Frame(self, bg=self.BG)
        box.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # ── Tiêu đề ───────────────────────────────────────────
        tk.Label(
            box, text="CONNECT",
            bg=self.BG, fg=self.TITLE1_FG,
            font=self.F_TITLE1
        ).pack()

        tk.Label(
            box, text="FOUR",
            bg=self.BG, fg=self.TITLE2_FG,
            font=self.F_TITLE2
        ).pack()

        # Khoảng cách giữa tiêu đề và nút
        tk.Frame(box, bg=self.BG, height=30).pack()

        # ── Nút ───────────────────────────────────────────────
        self._make_btn(
            box, "CHƠI VỚI MÁY", self.BTN_PVE,
            lambda: self.controller.start_game("pve")
        )
        self._make_btn(
            box, "HƯỚNG DẪN", self.BTN_HELP,
            self.controller.show_instructions
        )
        self._make_btn(
            box, "THOÁT", self.BTN_EXIT,
            self.controller.quit
        )

    # ──────────────────────────────────────────────────────────
    #  HELPER: TẠO NÚT
    # ──────────────────────────────────────────────────────────

    def _make_btn(self, parent: tk.Widget,
                  text: str, colors: tuple, command):
        """
        Tạo một nút bấm chuẩn.

        Tham số:
            parent  : widget cha
            text    : nhãn nút
            colors  : (màu_nền, màu_chữ)
            command : hàm gọi khi bấm
        """
        bg, fg = colors
        tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            font=self.F_BTN,
            width=self.BTN_WIDTH,
            pady=self.BTN_PADY,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground=self._darken(bg),
            activeforeground=fg,
            bd=0,
        ).pack(pady=self.BTN_SPACE)

    # ──────────────────────────────────────────────────────────
    #  HELPER: LÀM TỐI MÀU (cho activebackground)
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _darken(hex_color: str, amount: int = 30) -> str:
        """Làm tối màu hex đi một lượng nhất định."""
        hx = hex_color.lstrip("#")
        r = max(0, int(hx[0:2], 16) - amount)
        g = max(0, int(hx[2:4], 16) - amount)
        b = max(0, int(hx[4:6], 16) - amount)
        return f"#{r:02x}{g:02x}{b:02x}"
