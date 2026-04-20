"""
=============================================================
LOGIC.PY - Model: GameLogic class
=============================================================
Chứa toàn bộ logic game (numpy board) và AI (Minimax).
KHÔNG import bất kỳ thứ gì liên quan đến Tkinter.
=============================================================
"""

import math
import random
import numpy as np

from config import (
    ROWS, COLS, EMPTY, PLAYER_1, PLAYER_2, AI_DEPTH
)


class GameLogic:
    """
    Đóng gói toàn bộ trạng thái và luật chơi Connect 4.

    Trách nhiệm:
      - Quản lý bàn cờ numpy (ROWS x COLS)
      - Validate nước đi
      - Kiểm tra thắng / hòa
      - Cung cấp nước đi tốt nhất cho AI (Minimax + Alpha-Beta)
    """

    def __init__(self):
        self.board = self._create_board()

    # ──────────────────────────────────
    #  QUẢN LÝ BÀN CỜ
    # ──────────────────────────────────

    def _create_board(self) -> np.ndarray:
        """Khởi tạo bàn cờ 6x7 toàn 0 (ô trống)."""
        return np.zeros((ROWS, COLS), dtype=int)

    def reset(self):
        """Reset bàn cờ về trạng thái ban đầu."""
        self.board = self._create_board()

    def is_valid_column(self, col: int) -> bool:
        """Kiểm tra cột chưa đầy (hàng trên cùng row=0 còn trống)."""
        return 0 <= col < COLS and self.board[0][col] == EMPTY

    def get_next_open_row(self, col: int) -> int:
        """Tìm hàng trống thấp nhất trong cột."""
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                return row
        return -1

    def drop_piece(self, row: int, col: int, piece: int):
        """Thả xu vào ô [row][col]."""
        self.board[row][col] = piece

    def get_valid_columns(self) -> list:
        """Trả về danh sách cột hợp lệ (chưa đầy)."""
        return [c for c in range(COLS) if self.is_valid_column(c)]

    def is_board_full(self) -> bool:
        """Kiểm tra bàn cờ đã đầy (hòa)."""
        return all(self.board[0][c] != EMPTY for c in range(COLS))

    # ──────────────────────────────────
    #  KIỂM TRA THẮNG
    # ──────────────────────────────────

    def check_win(self, piece: int, board: np.ndarray = None) -> list:
        """
        Kiểm tra chiến thắng của người chơi piece.

        Trả về danh sách 4 tọa độ [(r,c),...] của ô thắng,
        hoặc [] nếu chưa thắng.

        Tham số board (tuỳ chọn): kiểm tra trên bàn cờ bất kỳ thay vì self.board.
        """
        b = board if board is not None else self.board

        # Ngang
        for r in range(ROWS):
            for c in range(COLS - 3):
                if all(b[r][c + i] == piece for i in range(4)):
                    return [(r, c + i) for i in range(4)]

        # Dọc
        for r in range(ROWS - 3):
            for c in range(COLS):
                if all(b[r + i][c] == piece for i in range(4)):
                    return [(r + i, c) for i in range(4)]

        # Chéo xuống phải ↘
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if all(b[r + i][c + i] == piece for i in range(4)):
                    return [(r + i, c + i) for i in range(4)]

        # Chéo xuống trái ↙
        for r in range(ROWS - 3):
            for c in range(3, COLS):
                if all(b[r + i][c - i] == piece for i in range(4)):
                    return [(r + i, c - i) for i in range(4)]

        return []

    # ──────────────────────────────────
    #  AI: HEURISTIC
    # ──────────────────────────────────

    def _evaluate_window(self, window: list, piece: int) -> int:
        """Đánh giá điểm một cửa sổ 4 ô."""
        opponent = PLAYER_1 if piece == PLAYER_2 else PLAYER_2
        score = 0
        pc = window.count(piece)
        ec = window.count(EMPTY)
        oc = window.count(opponent)

        if pc == 4:
            score += 100
        elif pc == 3 and ec == 1:
            score += 5
        elif pc == 2 and ec == 2:
            score += 2

        if oc == 3 and ec == 1:
            score -= 4

        return score

    def _score_position(self, board: np.ndarray, piece: int) -> int:
        """Heuristic đánh giá toàn bộ bàn cờ."""
        score = 0
        center = COLS // 2
        center_arr = [int(board[r][center]) for r in range(ROWS)]
        score += center_arr.count(piece) * 3

        for r in range(ROWS):
            row = [int(board[r][c]) for c in range(COLS)]
            for c in range(COLS - 3):
                score += self._evaluate_window(row[c:c + 4], piece)

        for c in range(COLS):
            col = [int(board[r][c]) for r in range(ROWS)]
            for r in range(ROWS - 3):
                score += self._evaluate_window(col[r:r + 4], piece)

        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                w = [board[r + i][c + i] for i in range(4)]
                score += self._evaluate_window(w, piece)

        for r in range(ROWS - 3):
            for c in range(3, COLS):
                w = [board[r + i][c - i] for i in range(4)]
                score += self._evaluate_window(w, piece)

        return score

    def _is_terminal(self, board: np.ndarray) -> bool:
        """Trả về True nếu ván đã kết thúc (có người thắng hoặc hòa)."""
        return (bool(self.check_win(PLAYER_1, board)) or
                bool(self.check_win(PLAYER_2, board)) or
                bool(all(board[0][c] != EMPTY for c in range(COLS))))

    # ──────────────────────────────────
    #  AI: MINIMAX + ALPHA-BETA
    # ──────────────────────────────────

    def _minimax(self, board: np.ndarray, depth: int,
                 alpha: float, beta: float, maximizing: bool) -> tuple:
        """
        Thuật toán Minimax với Alpha-Beta Pruning.

        Trả về (best_col, best_score).
        """
        valid_cols = [c for c in range(COLS) if board[0][c] == EMPTY]
        is_terminal = self._is_terminal(board)

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.check_win(PLAYER_2, board):
                    return (None, 10_000_000)
                elif self.check_win(PLAYER_1, board):
                    return (None, -10_000_000)
                else:
                    return (None, 0)
            return (None, self._score_position(board, PLAYER_2))

        if maximizing:
            value = -math.inf
            best_col = random.choice(valid_cols) if valid_cols else 0
            for col in valid_cols:
                row = self._get_row(board, col)
                temp = board.copy()
                temp[row][col] = PLAYER_2
                _, sc = self._minimax(temp, depth - 1, alpha, beta, False)
                if sc > value:
                    value = sc
                    best_col = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return best_col, value
        else:
            value = math.inf
            best_col = random.choice(valid_cols) if valid_cols else 0
            for col in valid_cols:
                row = self._get_row(board, col)
                temp = board.copy()
                temp[row][col] = PLAYER_1
                _, sc = self._minimax(temp, depth - 1, alpha, beta, True)
                if sc < value:
                    value = sc
                    best_col = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return best_col, value

    @staticmethod
    def _get_row(board: np.ndarray, col: int) -> int:
        """Hàng trống thấp nhất trong cột (dùng trong minimax)."""
        for row in range(ROWS - 1, -1, -1):
            if board[row][col] == EMPTY:
                return row
        return -1

    def get_best_move(self, depth: int = AI_DEPTH) -> int:
        """
        Lấy nước đi tốt nhất cho AI.

        Ưu tiên:
          1. AI thắng ngay → đánh
          2. Chặn người thắng ngay
          3. Minimax đầy đủ
        """
        valid = self.get_valid_columns()
        if not valid:
            return COLS // 2

        # Ưu tiên 1: thắng ngay
        for col in valid:
            row = self.get_next_open_row(col)
            temp = self.board.copy()
            temp[row][col] = PLAYER_2
            if self.check_win(PLAYER_2, temp):
                return col

        # Ưu tiên 2: chặn người thắng
        for col in valid:
            row = self.get_next_open_row(col)
            temp = self.board.copy()
            temp[row][col] = PLAYER_1
            if self.check_win(PLAYER_1, temp):
                return col

        # Ưu tiên 3: Minimax
        col, _ = self._minimax(self.board, depth, -math.inf, math.inf, True)
        return col if col is not None else random.choice(valid)
