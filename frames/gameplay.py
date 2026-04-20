"""
=============================================================
frames/gameplay.py - Màn hình Gameplay (Bàn cờ)
=============================================================
GameFrame vẽ bàn cờ, xử lý click, hiển thị kết quả.
KHÔNG chứa logic game — tất cả gọi qua self.controller.logic
=============================================================
"""

import tkinter as tk
import random
from typing import Optional

from frames.base_frame import BaseFrame
from frames.pause import PauseOverlay
from config import (
    ROWS, COLS, PLAYER_1, PLAYER_2,
    CELL_SIZE, RADIUS, BOARD_W, BOARD_H,
    COLOR_BG, COLOR_BOARD, COLOR_EMPTY,
    COLOR_P1, COLOR_P2, COLOR_WIN_GLOW,
    COLOR_TEXT, COLOR_ACCENT, COLOR_TIMER_BG,
    TIMER_SECONDS, AI_DEPTH
)


class GameFrame(BaseFrame):
    """
    Màn hình gameplay: bàn cờ, timer, panel người chơi, pause.

    Giao tiếp với controller:
        self.controller.logic      → GameLogic instance
        self.controller.show_frame("MainMenuFrame") → về menu
    """

    def __init__(self, parent: tk.Widget, controller, mode: str = "pve"):
        super().__init__(parent, controller)
        self.configure(bg=COLOR_BG)
        self.mode      = mode           # "pve" hoặc "pvp"
        self.turn      = PLAYER_1
        self.game_over = False
        self.paused    = False
        self.timer_val = TIMER_SECONDS
        self.timer_job = None
        self._pause_overlay: Optional[PauseOverlay] = None

        # Reset bàn cờ qua controller.logic
        self.controller.logic.reset()

        self._build_layout()
        self._draw_board()
        self._start_timer()

    # ────────────────────────────────────────────────────────
    #  XÂY DỰNG LAYOUT
    # ────────────────────────────────────────────────────────

    def _build_layout(self):
        """Layout: [P1 panel] | [Board + TopBar] | [P2 panel]"""

        # Nhãn lượt đi
        self.lbl_turn = tk.Label(
            self, text="Lượt: Người chơi 1",
            bg=COLOR_BG, fg=COLOR_TEXT,
            font=("Arial", 13, "bold")
        )
        self.lbl_turn.pack(pady=(10, 0))

        # Hàng ngang chính
        self.row_frame = tk.Frame(self, bg=COLOR_BG)
        self.row_frame.pack()

        # Panel P1 (trái)
        self.p1_panel = self._build_player_panel(
            self.row_frame, "P1", COLOR_P1, active=True
        )
        self.p1_panel.pack(side=tk.LEFT, padx=10, pady=10)

        # Khu vực bàn cờ
        board_col = tk.Frame(self.row_frame, bg=COLOR_BG)
        board_col.pack(side=tk.LEFT)
        self.board_col = board_col   # Lưu ref để tính tọa độ chính xác

        # Thanh trên: Timer + Nút Pause
        top_bar = tk.Frame(board_col, bg=COLOR_BG)
        top_bar.pack(fill=tk.X)

        self.lbl_timer = tk.Label(
            top_bar, text=f"0:{self.timer_val:02d}",
            bg=COLOR_TIMER_BG, fg=COLOR_TEXT,
            font=("Courier", 11, "bold"), padx=6, pady=2
        )
        self.lbl_timer.pack(side=tk.LEFT, padx=5)

        self.btn_pause = tk.Button(
            top_bar, text="☰",
            bg="#333366", fg=COLOR_TEXT,
            font=("Arial", 14), bd=0, padx=5,
            command=self._toggle_pause
        )
        self.btn_pause.pack(side=tk.RIGHT, padx=5)

        # Canvas bàn cờ chính
        self.canvas = tk.Canvas(
            board_col, width=BOARD_W, height=BOARD_H,
            bg=COLOR_BOARD, highlightthickness=0, cursor="hand2"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)

        # Panel P2 (phải)
        self.p2_panel = self._build_player_panel(
            self.row_frame, "P2", COLOR_P2, active=False
        )
        self.p2_panel.pack(side=tk.LEFT, padx=10, pady=10)

        self.panels = {PLAYER_1: self.p1_panel, PLAYER_2: self.p2_panel}

    def _build_player_panel(self, parent, label, color, active):
        """Tạo panel thông tin người chơi (hình tròn xu + nhãn)."""
        border = COLOR_TEXT if active else "#333355"
        panel = tk.Frame(parent, bg=border, width=70, height=90, pady=2, padx=2)
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

        return panel

    def _set_active_player(self, player):
        """Cập nhật viền panel và nhãn lượt theo player hiện tại."""
        for p, panel in self.panels.items():
            panel.configure(bg=COLOR_TEXT if p == player else "#333355")

        if player == PLAYER_1:
            self.lbl_turn.configure(text="Lượt: Người chơi 1")
        else:
            name = "Lượt: AI" if self.mode == "pve" else "Lượt: Người chơi 2"
            self.lbl_turn.configure(text=name)

    # ────────────────────────────────────────────────────────
    #  VẼ BÀN CỜ
    # ────────────────────────────────────────────────────────

    def _draw_board(self, winning_cells=None):
        """Vẽ lại toàn bộ bàn cờ trên Canvas."""
        board   = self.controller.logic.board
        win_set = set(winning_cells) if winning_cells else set()
        self.canvas.delete("all")

        for r in range(ROWS):
            for c in range(COLS):
                cx = c * CELL_SIZE + CELL_SIZE // 2
                cy = r * CELL_SIZE + CELL_SIZE // 2
                piece = int(board[r][c])

                fill = (COLOR_P1 if piece == PLAYER_1 else
                        COLOR_P2 if piece == PLAYER_2 else
                        COLOR_EMPTY)

                is_win = (r, c) in win_set
                outline = COLOR_WIN_GLOW if is_win else "#0000AA"
                width   = 4 if is_win else 1

                self.canvas.create_oval(
                    cx - RADIUS, cy - RADIUS,
                    cx + RADIUS, cy + RADIUS,
                    fill=fill, outline=outline, width=width
                )

    # ────────────────────────────────────────────────────────
    #  XỬ LÝ CLICK CHUỘT (Gọi logic qua controller)
    # ────────────────────────────────────────────────────────

    def _on_click(self, event):
        """Người chơi click vào bàn cờ → tính cột → gọi _make_move."""
        if self.game_over or self.paused:
            return
        if self.mode == "pve" and self.turn != PLAYER_1:
            return

        col = event.x // CELL_SIZE
        logic = self.controller.logic

        if not (0 <= col < COLS) or not logic.is_valid_column(col):
            if 0 <= col < COLS:
                self._flash_column(col)
            return

        self._make_move(col, self.turn)

    def _make_move(self, col: int, player: int):
        """
        Thực hiện nước đi:
          1. Gọi logic.drop_piece()
          2. Vẽ lại bàn cờ
          3. Kiểm tra thắng/hòa qua logic
          4. Chuyển lượt hoặc kích hoạt AI
        """
        logic = self.controller.logic
        row   = logic.get_next_open_row(col)
        logic.drop_piece(row, col, player)
        self._draw_board()

        # ── Kiểm tra thắng ──
        winning = logic.check_win(player)
        if winning:
            self._draw_board(winning_cells=winning)
            self._end_game(winner=player)
            return

        # ── Kiểm tra hòa ──
        if logic.is_board_full():
            self._end_game(winner=None)
            return

        # ── Chuyển lượt ──
        self.turn = PLAYER_2 if player == PLAYER_1 else PLAYER_1
        self._set_active_player(self.turn)
        self._reset_timer()

        # ── Lượt AI (chế độ PVE) ──
        if self.mode == "pve" and self.turn == PLAYER_2:
            self.after(400, self._ai_move)

    def _ai_move(self):
        """Lấy nước đi tốt nhất từ logic và thực hiện."""
        if self.game_over or self.paused:
            return
        best_col = self.controller.logic.get_best_move(depth=AI_DEPTH)
        self._make_move(best_col, PLAYER_2)

    # ────────────────────────────────────────────────────────
    #  TIMER
    # ────────────────────────────────────────────────────────

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
        self.timer_job  = self.after(1000, self._tick)

    def _reset_timer(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.timer_val = TIMER_SECONDS
        self.timer_job = self.after(1000, self._tick)

    def _on_timer_expired(self):
        if self.game_over:
            return
        logic = self.controller.logic
        valid = logic.get_valid_columns()
        if not valid:
            return
        col = (COLS // 2
               if logic.is_valid_column(COLS // 2)
               else random.choice(valid))
        self._make_move(col, self.turn)

    # ────────────────────────────────────────────────────────
    #  PAUSE
    # ────────────────────────────────────────────────────────

    def _toggle_pause(self):
        if self.game_over:
            return
        if self.paused:
            self._resume()
        else:
            self._pause()

    def _pause(self):
        """Hiển thị PauseOverlay."""
        self.paused = True
        if self.timer_job:
            self.after_cancel(self.timer_job)

        # Tọa độ canvas so với GameFrame (dùng rootx/y để tránh lỗi hệ tọa độ)
        x = self.canvas.winfo_rootx() - self.winfo_rootx()
        y = self.canvas.winfo_rooty() - self.winfo_rooty()

        self._pause_overlay = PauseOverlay(
            parent   = self,
            x=x, y=y, w=BOARD_W, h=BOARD_H,
            on_resume = self._resume,
            on_reset  = self._reset_game,
            on_menu   = lambda: self.controller.show_frame("MainMenuFrame"),
        )

    def _resume(self):
        """Xóa PauseOverlay, tiếp tục game."""
        if self._pause_overlay:
            self._pause_overlay.destroy()
            self._pause_overlay = None
        self.paused    = False
        self.timer_job = self.after(1000, self._tick)

        if self.mode == "pve" and self.turn == PLAYER_2:
            self.after(400, self._ai_move)

    # ────────────────────────────────────────────────────────
    #  KẾT THÚC GAME
    # ────────────────────────────────────────────────────────

    def _end_game(self, winner):
        """Dừng timer, hiển thị thanh kết quả."""
        self.game_over = True
        if self.timer_job:
            self.after_cancel(self.timer_job)

        if winner == PLAYER_1:
            msg, mc = ("P1 thắng!" if self.mode == "pvp" else "Bạn thắng!"), COLOR_P1
        elif winner == PLAYER_2:
            msg, mc = ("P2 thắng!" if self.mode == "pvp" else "AI thắng!"), COLOR_P2
        else:
            msg, mc = "Hòa!", "#AAAAAA"

        # Đặt thanh kết quả ở đầu board_col (tránh lỗi tọa độ)
        rf = tk.Frame(self.board_col, bg=COLOR_BG)
        rf.place(x=0, y=0, width=BOARD_W, height=40)

        tk.Button(rf, text="Chơi lại", command=self._reset_game,
                  bg=COLOR_ACCENT, fg="black",
                  font=("Arial", 10, "bold"),
                  relief=tk.FLAT, padx=10, cursor="hand2"
                  ).pack(side=tk.LEFT, padx=2)

        tk.Label(rf, text=msg, bg=mc, fg=COLOR_TEXT,
                 font=("Arial", 12, "bold"), padx=10, pady=2
                 ).pack(side=tk.LEFT, padx=2)

        tk.Button(rf, text="Menu", command=lambda: self.controller.show_frame("MainMenuFrame"),
                  bg="#555555", fg=COLOR_TEXT,
                  font=("Arial", 10, "bold"),
                  relief=tk.FLAT, padx=10, cursor="hand2"
                  ).pack(side=tk.LEFT, padx=2)

        self._result_frame = rf

    def _reset_game(self):
        """Reset bàn cờ qua controller.logic, bắt đầu ván mới."""
        if hasattr(self, "_result_frame") and self._result_frame.winfo_exists():
            self._result_frame.destroy()
        if self._pause_overlay:
            self._pause_overlay.destroy()
            self._pause_overlay = None

        self.controller.logic.reset()
        self.turn      = PLAYER_1
        self.game_over = False
        self.paused    = False
        self._set_active_player(PLAYER_1)
        self._draw_board()

        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.timer_val = TIMER_SECONDS
        self._start_timer()

    # ────────────────────────────────────────────────────────
    #  HIỆU ỨNG PHỤ
    # ────────────────────────────────────────────────────────

    def _flash_column(self, col: int):
        """Nhấp nháy đỏ khi cột đầy."""
        fid = self.canvas.create_rectangle(
            col * CELL_SIZE, 0,
            (col + 1) * CELL_SIZE, BOARD_H,
            fill="#FF0000", stipple="gray25", outline=""
        )
        self.after(300, lambda: self.canvas.delete(fid))
