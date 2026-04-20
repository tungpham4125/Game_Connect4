"""
=============================================================
AI.PY - Module AI standalone (wrapper cho GameLogic)
=============================================================
Cung cấp hàm get_best_ai_move() để sử dụng độc lập
nếu cần gọi AI từ bên ngoài mà không cần connect4App.

Ghi chú: GameFrame dùng controller.logic.get_best_move()
trực tiếp — file này là phần mở rộng tùy chọn.
=============================================================
"""

import numpy as np
from logic import GameLogic
from config import AI_DEPTH


def get_best_ai_move(board: np.ndarray, depth: int = AI_DEPTH) -> int:
    """
    Lấy nước đi tốt nhất cho AI.

    Tham số:
        board : bàn cờ numpy (6x7)
        depth : độ sâu Minimax (mặc định = AI_DEPTH từ config)

    Trả về:
        Chỉ số cột tốt nhất (0-6)
    """
    tmp = GameLogic()
    tmp.board = board.copy()
    return tmp.get_best_move(depth)
