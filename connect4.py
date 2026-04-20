"""
=============================================================
CONNECT 4 - Trò chơi Kết nối 4
=============================================================
Tác giả: AI Assistant
Mô tả : Trò chơi Connect 4 hoàn chỉnh với:
         - Giao diện đồ họa Tkinter hiện đại
         - Chế độ PVP (Người vs Người) và PVE (Người vs AI)
         - AI sử dụng thuật toán Minimax + Alpha-Beta Pruning
         - Đồng hồ đếm ngược (timer)
         - Highlight 4 ô chiến thắng
         - Menu Pause & Game Over
=============================================================
Yêu cầu : Python 3.7+, numpy, tkinter (có sẵn trong Python)
Chạy    : python connect4.py
=============================================================
"""

import tkinter as tk
from tkinter import font as tkfont
import numpy as np
import random
import time
import math
import threading

# ─────────────────────────────────────────────────────────────
#  HẰNG SỐ TOÀN CỤC (Global Constants)
# ─────────────────────────────────────────────────────────────
ROWS       = 6          # Số hàng bàn cờ
COLS       = 7          # Số cột bàn cờ
EMPTY      = 0          # Ô trống
PLAYER_1   = 1          # Người chơi 1 (Đỏ)
PLAYER_2   = 2          # Người chơi 2 / AI (Vàng)

# Kích thước giao diện
CELL_SIZE  = 75         # Kích thước mỗi ô (pixel)
RADIUS     = 30         # Bán kính hình tròn xu
PAD_X      = 40         # Padding ngang bàn cờ
PAD_Y      = 20         # Padding dọc bàn cờ
BOARD_W    = COLS * CELL_SIZE   # Chiều rộng bàn cờ
BOARD_H    = ROWS * CELL_SIZE   # Chiều cao bàn cờ

# Màu sắc Theme
COLOR_BG          = "#0D0D2B"   # Nền tổng (tím đen)
COLOR_BOARD       = "#1A1AE6"   # Nền bàn cờ (xanh dương đậm)
COLOR_BOARD_LIGHT = "#2222FF"   # Bàn cờ sáng hơn
COLOR_EMPTY       = "#0A0A3E"   # Ô trống (xanh đen)
COLOR_P1          = "#FF2222"   # Xu Người chơi 1 (Đỏ)
COLOR_P2          = "#F5D60A"   # Xu Người chơi 2 / AI (Vàng)
COLOR_WIN_GLOW    = "#00FF88"   # Viền highlight ô thắng (xanh lá)
COLOR_TEXT        = "#FFFFFF"   # Chữ trắng
COLOR_ACCENT      = "#F5A623"   # Vàng cam (accent)
COLOR_TIMER_BG    = "#FF4444"   # Nền timer (đỏ)
COLOR_BTN_PVP     = "#8AFF2A"   # Nút PVP (xanh lá vàng)
COLOR_BTN_PVE     = "#2AFFEE"   # Nút PVE (xanh ngọc)
COLOR_BTN_ONLINE  = "#555555"   # Nút Online (xám - disabled)
COLOR_BTN_EXIT    = "#CCFF00"   # Nút Exit (chanh)
COLOR_PAUSE_BG    = "#CC0077"   # Nền menu Pause (hồng)
COLOR_BTN_BLUE    = "#0055FF"   # Nút xanh trong pause

# Cài đặt AI
AI_DEPTH = 5            # Độ sâu Minimax (tăng = AI mạnh hơn nhưng chậm hơn)
TIMER_SECONDS = 60      # Thời gian mỗi lượt (giây)

# ─────────────────────────────────────────────────────────────
#  PHẦN 1: LOGIC BÀN CỜ (Board Logic)
# ─────────────────────────────────────────────────────────────

def create_board() -> np.ndarray:
    """Khởi tạo bàn cờ 6x7 toàn số 0 (ô trống)."""
    return np.zeros((ROWS, COLS), dtype=int)


def is_valid_column(board: np.ndarray, col: int) -> bool:
    """Kiểm tra cột có hợp lệ không (chưa đầy).
    
    Bàn cờ được điền từ dưới lên, nên nếu hàng trên cùng (row=0)
    của cột đó còn trống thì cột chưa đầy.
    """
    return board[0][col] == EMPTY


def get_next_open_row(board: np.ndarray, col: int) -> int:
    """Tìm hàng trống thấp nhất trong cột để đặt xu.
    
    Duyệt từ hàng đáy (ROWS-1) lên trên, trả về hàng đầu tiên còn trống.
    """
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return -1  # Cột đầy (không xảy ra nếu kiểm tra is_valid_column trước)


def drop_piece(board: np.ndarray, row: int, col: int, piece: int) -> None:
    """Thả xu của người chơi (piece) vào ô [row][col]."""
    board[row][col] = piece


def check_win(board: np.ndarray, piece: int) -> list:
    """Kiểm tra chiến thắng của người chơi piece.
    
    Trả về danh sách 4 tọa độ [(r,c), ...] của ô thắng,
    hoặc [] nếu chưa thắng.
    
    Kiểm tra 4 hướng:
      - Ngang (horizontal)
      - Dọc  (vertical)
      - Chéo xuống phải (diagonal /)
      - Chéo xuống trái (diagonal \\)
    """
    # Kiểm tra chiều NGANG
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return [(r, c + i) for i in range(4)]

    # Kiểm tra chiều DỌC
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r + i][c] == piece for i in range(4)):
                return [(r + i, c) for i in range(4)]

    # Kiểm tra ĐƯỜNG CHÉO xuống phải (↘)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return [(r + i, c + i) for i in range(4)]

    # Kiểm tra ĐƯỜNG CHÉO xuống trái (↙)
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if all(board[r + i][c - i] == piece for i in range(4)):
                return [(r + i, c - i) for i in range(4)]

    return []  # Chưa có ai thắng


def is_board_full(board: np.ndarray) -> bool:
    """Kiểm tra bàn cờ đã đầy chưa (hòa)."""
    return all(board[0][c] != EMPTY for c in range(COLS))


def get_valid_columns(board: np.ndarray) -> list:
    """Trả về danh sách các cột còn hợp lệ (chưa đầy)."""
    return [c for c in range(COLS) if is_valid_column(board, c)]


# ─────────────────────────────────────────────────────────────
#  PHẦN 2: ĐỘNG CƠ AI - MINIMAX + ALPHA-BETA PRUNING
# ─────────────────────────────────────────────────────────────

def evaluate_window(window: list, piece: int) -> int:
    """Đánh giá điểm số của một cửa sổ 4 ô.
    
    Tham số:
        window : Danh sách 4 giá trị ô trong cửa sổ
        piece  : Mã người chơi đang được đánh giá (PLAYER_1 hoặc PLAYER_2)
    
    Logic tính điểm:
        +100  : Đã có 4 xu liên tiếp (thắng) - thực ra xử lý ở check_win
        +5    : Có 3 xu + 1 ô trống (gần thắng)
        +2    : Có 2 xu + 2 ô trống (có tiềm năng)
        -4    : Đối thủ có 3 xu + 1 ô trống (phải chặn gấp)
    """
    opponent = PLAYER_1 if piece == PLAYER_2 else PLAYER_2
    score = 0

    piece_count   = window.count(piece)
    empty_count   = window.count(EMPTY)
    opp_count     = window.count(opponent)

    if piece_count == 4:
        score += 100
    elif piece_count == 3 and empty_count == 1:
        score += 5    # Gần thắng
    elif piece_count == 2 and empty_count == 2:
        score += 2    # Có tiềm năng

    if opp_count == 3 and empty_count == 1:
        score -= 4    # Đối thủ chuẩn bị thắng → phải chặn!

    return score


def score_position(board: np.ndarray, piece: int) -> int:
    """Hàm đánh giá (Heuristic) toàn bộ bàn cờ cho AI.
    
    Chiến lược:
      1. Ưu tiên cao nhất cho cột GIỮA (cột 3) - vị trí trung tâm
         cho phép tạo nhiều kết hợp nhất.
      2. Quét tất cả cửa sổ 4 ô theo 4 hướng và cộng/trừ điểm.
    """
    score = 0

    # 1. Cộng điểm cho MỌI xu ở cột giữa (cột 3)
    center_col = COLS // 2
    center_array = [int(board[r][center_col]) for r in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * 3  # Mỗi xu ở giữa = +3 điểm

    # 2. Quét theo chiều NGANG
    for r in range(ROWS):
        row_array = [int(board[r][c]) for c in range(COLS)]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # 3. Quét theo chiều DỌC
    for c in range(COLS):
        col_array = [int(board[r][c]) for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # 4. Quét ĐƯỜNG CHÉO xuống phải (↘)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # 5. Quét ĐƯỜNG CHÉO xuống trái (↙)
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            window = [board[r + i][c - i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board: np.ndarray) -> bool:
    """Kiểm tra xem trạng thái bàn cờ có phải node cuối không.
    
    Node cuối = bàn cờ đầy HOẶC một bên đã thắng.
    """
    return (bool(check_win(board, PLAYER_1)) or
            bool(check_win(board, PLAYER_2)) or
            is_board_full(board))


def minimax(board: np.ndarray, depth: int, alpha: float, beta: float,
            maximizing_player: bool) -> tuple:
    """Thuật toán Minimax với Alpha-Beta Pruning.
    
    Nguyên lý hoạt động:
    ─────────────────────────────────────────────────
    • Minimax mô phỏng cây quyết định: AI (MAX) muốn tối đa hóa điểm,
      Người chơi (MIN) muốn tối thiểu hóa điểm của AI.
    • Tìm kiếm theo độ sâu 'depth' bước đi tương lai.
    
    Alpha-Beta Pruning (Cắt tỉa):
    ─────────────────────────────────────────────────
    • alpha = điểm tốt nhất mà MAX đảm bảo được (ban đầu = -∞)
    • beta  = điểm tốt nhất mà MIN đảm bảo được (ban đầu = +∞)
    • Khi alpha >= beta → cắt tỉa (không cần xét tiếp nhánh đó)
    • Điều này giảm đáng kể số node cần duyệt, tăng tốc độ AI
    
    Tham số:
        board             : Trạng thái bàn cờ hiện tại
        depth             : Độ sâu còn lại để tìm kiếm
        alpha             : Giá trị alpha (best cho MAX)
        beta              : Giá trị beta (best cho MIN)
        maximizing_player : True nếu lượt AI (MAX), False nếu lượt Người (MIN)
    
    Trả về:
        (best_col, best_score) : Cột tốt nhất và điểm số tương ứng
    """
    valid_cols = get_valid_columns(board)
    is_terminal = is_terminal_node(board)

    # TRƯỜNG HỢP CƠ SỞ (Base Case):
    # ─────────────────────────────────────────────────
    if depth == 0 or is_terminal:
        if is_terminal:
            # Thắng hoặc thua → trả điểm rất lớn/nhỏ
            if check_win(board, PLAYER_2):
                return (None, 10_000_000)   # AI thắng → điểm vô cực dương
            elif check_win(board, PLAYER_1):
                return (None, -10_000_000)  # Người thắng → điểm vô cực âm
            else:
                return (None, 0)            # Hòa → điểm 0
        else:
            # Hết độ sâu → dùng hàm heuristic đánh giá bàn cờ
            return (None, score_position(board, PLAYER_2))

    # LƯỢT AI - NGƯỜI CHƠI TỐI ĐA HÓA (Maximizing Player = AI)
    # ─────────────────────────────────────────────────
    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_cols)  # Mặc định chọn ngẫu nhiên

        for col in valid_cols:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER_2)

            # Gọi đệ quy: tiếp tục với lượt MIN, giảm depth
            _, new_score = minimax(temp_board, depth - 1, alpha, beta, False)

            if new_score > value:
                value = new_score
                best_col = col

            # Cập nhật alpha = max(alpha, value hiện tại)
            alpha = max(alpha, value)

            # CẮT TỈA BETA: Nếu alpha >= beta → MIN sẽ không chọn nhánh này
            if alpha >= beta:
                break  # Prune (cắt tỉa)!

        return best_col, value

    # LƯỢT NGƯỜI - NGƯỜI CHƠI TỐI THIỂU HÓA (Minimizing Player = Người)
    # ─────────────────────────────────────────────────
    else:
        value = math.inf
        best_col = random.choice(valid_cols)

        for col in valid_cols:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER_1)

            # Gọi đệ quy: tiếp tục với lượt MAX, giảm depth
            _, new_score = minimax(temp_board, depth - 1, alpha, beta, True)

            if new_score < value:
                value = new_score
                best_col = col

            # Cập nhật beta = min(beta, value hiện tại)
            beta = min(beta, value)

            # CẮT TỈA ALPHA: Nếu alpha >= beta → MAX sẽ không chọn nhánh này
            if alpha >= beta:
                break  # Prune (cắt tỉa)!

        return best_col, value


def get_best_ai_move(board: np.ndarray, depth: int = AI_DEPTH) -> int:
    """Giao diện đơn giản để lấy nước đi tốt nhất của AI.
    
    Kiểm tra nhanh (trước khi chạy Minimax đầy đủ):
      1. Nếu AI có thể thắng ngay → đánh ngay
      2. Nếu Người sắp thắng → phải chặn ngay
      3. Nếu không → chạy Minimax để tính toán
    """
    valid_cols = get_valid_columns(board)

    # Ưu tiên 1: Kiểm tra AI có thể thắng ngay không
    for col in valid_cols:
        row = get_next_open_row(board, col)
        temp = board.copy()
        drop_piece(temp, row, col, PLAYER_2)
        if check_win(temp, PLAYER_2):
            return col

    # Ưu tiên 2: Chặn Người chơi thắng ngay
    for col in valid_cols:
        row = get_next_open_row(board, col)
        temp = board.copy()
        drop_piece(temp, row, col, PLAYER_1)
        if check_win(temp, PLAYER_1):
            return col

    # Ưu tiên 3: Chạy Minimax đầy đủ
    col, _ = minimax(board, depth, -math.inf, math.inf, True)
    return col if col is not None else random.choice(valid_cols)


# ─────────────────────────────────────────────────────────────
#  PHẦN 3: GIAO DIỆN TKINTER (Tkinter GUI)
# ─────────────────────────────────────────────────────────────

class Connect4App(tk.Tk):
    """Lớp ứng dụng chính - quản lý chuyển đổi giữa các màn hình."""

    def __init__(self):
        super().__init__()
        self.title("Connect 4")
        # Tính kích thước cửa sổ dựa trên bàn cờ
        win_w = BOARD_W + PAD_X * 2 + 200  # Thêm 200px cho panel P1/P2
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
#  MÀNN HÌNH 1: MAIN MENU
# ─────────────────────────────────────────────────────────────

class MainMenuFrame(tk.Frame):
    """Màn hình chính: Logo + 4 nút (PVP, PVE, Online, Exit)."""

    def __init__(self, master: Connect4App):
        super().__init__(master, bg=COLOR_BG)
        self.master = master
        self._build()

    def _build(self):
        """Xây dựng layout Main Menu."""
        # ── Container trung tâm với gradient giả ──
        canvas_w = 480
        canvas_h = 400
        self.canvas = tk.Canvas(self, width=canvas_w, height=canvas_h,
                                bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(pady=40)

        # Nền gradient (tím → xanh đậm) dùng các hình chữ nhật xếp chồng
        for i in range(canvas_h):
            ratio = i / canvas_h
            r = int(0x1A + ratio * (0x0A - 0x1A))
            g = int(0x00 + ratio * (0x00 - 0x00))
            b = int(0xAA + ratio * (0x88 - 0xAA))
            self.canvas.create_rectangle(0, i, canvas_w, i + 1,
                                         fill=f"#{r:02x}{g:02x}{b:02x}",
                                         outline="")

        # Viền cửa sổ
        self.canvas.create_rectangle(2, 2, canvas_w - 2, canvas_h - 2,
                                     outline="#333388", width=2)

        # Logo icon (Python snake giả)
        self.canvas.create_oval(canvas_w - 55, 10, canvas_w - 10, 55,
                                fill="#F5A623", outline="#CC7700", width=2)
        self.canvas.create_text(canvas_w - 33, 33, text="🐍",
                                font=("Arial", 16), fill="white")

        # Tiêu đề "Connect 4" với hiệu ứng LED
        self._draw_led_title(canvas_w // 2, 90, "Connect 4")

        # ── Các nút menu ──
        btn_y_start = 170
        btn_gap     = 60
        btn_w       = 160
        btn_h       = 38

        # Nút PVP
        self._draw_button(canvas_w // 2, btn_y_start,
                          btn_w, btn_h, "PVP",
                          COLOR_BTN_PVP, "black",
                          lambda: self.master.start_game("pvp"))

        # Nút PVE
        self._draw_button(canvas_w // 2, btn_y_start + btn_gap,
                          btn_w, btn_h, "PVE",
                          COLOR_BTN_PVE, "black",
                          lambda: self.master.start_game("pve"))

        # Nút Online (disabled - xám)
        self._draw_button(canvas_w // 2, btn_y_start + btn_gap * 2,
                          btn_w, btn_h, "Online",
                          COLOR_BTN_ONLINE, "#888888",
                          None)  # None = không có hành động

        # Nút Exit
        self._draw_button(canvas_w // 2, btn_y_start + btn_gap * 3,
                          btn_w, btn_h, "Exit",
                          COLOR_BTN_EXIT, "black",
                          self.master.quit)

    def _draw_led_title(self, cx: int, cy: int, text: str):
        """Vẽ tiêu đề với hiệu ứng chữ LED cam sáng."""
        # Shadow đen
        self.canvas.create_text(cx + 2, cy + 2, text=text,
                                font=("Arial", 34, "bold"),
                                fill="#000000")
        # Chữ chính màu cam
        self.canvas.create_text(cx, cy, text=text,
                                font=("Arial", 34, "bold"),
                                fill=COLOR_ACCENT)
        # Glow nhỏ (phiên bản sáng hơn)
        self.canvas.create_text(cx, cy, text=text,
                                font=("Arial", 34, "bold"),
                                fill=COLOR_ACCENT,
                                stipple="gray50")

    def _draw_button(self, cx: int, cy: int, w: int, h: int,
                     text: str, bg: str, fg: str, command):
        """Vẽ nút bo góc trên Canvas và gắn sự kiện click."""
        x1, y1 = cx - w // 2, cy - h // 2
        x2, y2 = cx + w // 2, cy + h // 2

        # Viền nút (xanh ngọc sáng)
        border_id = self.canvas.create_rectangle(
            x1 - 2, y1 - 2, x2 + 2, y2 + 2,
            fill="#00FFFF" if command else "#333333",
            outline="", width=0
        )
        # Nền nút
        rect_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=bg, outline="", width=0
        )
        # Chữ nút
        text_id = self.canvas.create_text(
            cx, cy, text=text,
            font=("Arial", 14, "bold"),
            fill=fg
        )

        # Chỉ gắn sự kiện nếu có command (không phải nút disabled)
        if command:
            for item_id in (border_id, rect_id, text_id):
                self.canvas.tag_bind(item_id, "<Button-1>",
                                     lambda e, cmd=command: cmd())
                self.canvas.tag_bind(item_id, "<Enter>",
                                     lambda e, rid=rect_id: self.canvas.itemconfig(
                                         rid, fill=self._lighten(bg)))
                self.canvas.tag_bind(item_id, "<Leave>",
                                     lambda e, rid=rect_id, orig_bg=bg:
                                         self.canvas.itemconfig(rid, fill=orig_bg))

    @staticmethod
    def _lighten(hex_color: str) -> str:
        """Làm sáng màu hex lên một chút cho hiệu ứng hover."""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, r + 40)
        g = min(255, g + 40)
        b = min(255, b + 40)
        return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────────────────────
#  MÀNN HÌNH 2: GAMEPLAY
# ─────────────────────────────────────────────────────────────

class GameFrame(tk.Frame):
    """Màn hình gameplay chính: bàn cờ, timer, pause, game-over."""

    def __init__(self, master: Connect4App, mode: str):
        super().__init__(master, bg=COLOR_BG)
        self.master   = master
        self.mode     = mode        # 'pvp' hoặc 'pve'
        self.board    = create_board()
        self.turn     = PLAYER_1    # Lượt hiện tại
        self.game_over = False
        self.paused    = False
        self.timer_val = TIMER_SECONDS
        self.timer_job = None       # ID job after() của timer

        # Vẽ layout
        self._build_layout()
        self._draw_board()
        self._start_timer()

        # Nếu chế độ PVE và AI đi trước → không cần (Người luôn đi trước)

    # ──────────────────────────────────
    #  XÂY DỰNG LAYOUT
    # ──────────────────────────────────

    def _build_layout(self):
        """Tạo layout: [P1 panel] [Board canvas] [P2 panel]."""
        # Dòng nhãn lượt đi ở trên cùng
        self.lbl_turn = tk.Label(
            self, text="Player 1 turn",
            bg=COLOR_BG, fg=COLOR_TEXT,
            font=("Arial", 13, "bold")
        )
        self.lbl_turn.pack(pady=(10, 0))

        # Container ngang: P1 panel + Board + P2 panel
        self.row_frame = tk.Frame(self, bg=COLOR_BG)
        self.row_frame.pack()

        # ── Panel Người chơi 1 (trái) ──
        self.p1_panel = self._build_player_panel(
            self.row_frame, "P1", COLOR_P1, is_active=True
        )
        self.p1_panel.pack(side=tk.LEFT, padx=10, pady=10)

        # ── Canvas bàn cờ ──
        board_frame = tk.Frame(self.row_frame, bg=COLOR_BG)
        board_frame.pack(side=tk.LEFT)

        # Thanh trên: Timer + Nút Pause
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

        # Canvas chính (bàn cờ)
        self.canvas = tk.Canvas(
            board_frame,
            width=BOARD_W,
            height=BOARD_H,
            bg=COLOR_BOARD,
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack()

        # Gắn sự kiện click chuột vào canvas
        self.canvas.bind("<Button-1>", self._on_click)

        # ── Panel Người chơi 2 (phải) ──
        self.p2_panel = self._build_player_panel(
            self.row_frame, "P2", COLOR_P2, is_active=False
        )
        self.p2_panel.pack(side=tk.LEFT, padx=10, pady=10)

        # Lưu reference tới panel để cập nhật active/inactive
        self.panels = {PLAYER_1: self.p1_panel, PLAYER_2: self.p2_panel}

    def _build_player_panel(self, parent, label: str, color: str,
                            is_active: bool) -> tk.Frame:
        """Tạo panel hiển thị thông tin người chơi (trái/phải).
        
        Panel gồm: hình tròn màu xu + nhãn P1/P2
        Border trắng nếu đang active, tối nếu không.
        """
        border_color = COLOR_TEXT if is_active else "#333355"
        panel = tk.Frame(parent, bg=border_color,
                         width=70, height=90, pady=2, padx=2)
        panel.pack_propagate(False)

        inner = tk.Frame(panel, bg="#1A1A4E", width=66, height=86)
        inner.pack_propagate(False)
        inner.pack(fill=tk.BOTH, expand=True)

        # Hình tròn xu
        disc_canvas = tk.Canvas(inner, width=50, height=50,
                                bg="#1A1A4E", highlightthickness=0)
        disc_canvas.pack(pady=(8, 0))
        disc_canvas.create_oval(5, 5, 45, 45, fill=color, outline="white", width=2)

        # Nhãn P1/P2
        tk.Label(inner, text=label, bg="#1A1A4E", fg=COLOR_TEXT,
                 font=("Arial", 11, "bold")).pack()

        # Lưu inner frame để set màu viền sau
        panel._inner = inner
        panel._border_color_active   = COLOR_TEXT
        panel._border_color_inactive = "#333355"
        panel._is_active = is_active

        return panel

    def _set_active_player(self, player: int):
        """Cập nhật viền panel để chỉ ra người đang đến lượt."""
        for p, panel in self.panels.items():
            active = (p == player)
            panel.configure(bg=COLOR_TEXT if active else "#333355")

        # Cập nhật nhãn lượt
        if player == PLAYER_1:
            self.lbl_turn.configure(text="Player 1 turn", fg=COLOR_TEXT)
        else:
            name = "AI turn" if self.mode == "pve" else "Player 2 turn"
            self.lbl_turn.configure(text=name, fg=COLOR_TEXT)

    # ──────────────────────────────────
    #  VẼ BÀN CỜ
    # ──────────────────────────────────

    def _draw_board(self, winning_cells: list = None):
        """Vẽ lại toàn bộ bàn cờ trên Canvas.
        
        Tham số:
            winning_cells : [(r,c), ...] - Các ô chiến thắng cần highlight
        
        Cách vẽ:
          - Nền xanh dương (COLOR_BOARD)
          - Mỗi ô là hình tròn tô màu theo giá trị board[r][c]
          - Ô thắng có viền xanh lá sáng (COLOR_WIN_GLOW)
        """
        self.canvas.delete("all")
        win_set = set(winning_cells) if winning_cells else set()

        for r in range(ROWS):
            for c in range(COLS):
                # Tọa độ tâm hình tròn
                cx = c * CELL_SIZE + CELL_SIZE // 2
                cy = r * CELL_SIZE + CELL_SIZE // 2

                piece = int(self.board[r][c])

                # Xác định màu xu
                if piece == PLAYER_1:
                    fill_color = COLOR_P1
                elif piece == PLAYER_2:
                    fill_color = COLOR_P2
                else:
                    fill_color = COLOR_EMPTY

                # Xác định màu viền
                is_win_cell = (r, c) in win_set
                if is_win_cell:
                    outline_color = COLOR_WIN_GLOW
                    outline_width = 4
                else:
                    outline_color = "#0000AA"
                    outline_width = 1

                # Vẽ hình tròn
                self.canvas.create_oval(
                    cx - RADIUS, cy - RADIUS,
                    cx + RADIUS, cy + RADIUS,
                    fill=fill_color,
                    outline=outline_color,
                    width=outline_width
                )

    def _draw_preview(self, col: int):
        """Vẽ preview xu mờ ở hàng đầu khi chuột hover (chưa thả).
        
        Chức năng: Cho người chơi biết xu sẽ rơi vào cột nào.
        """
        self._draw_board()
        if 0 <= col < COLS and is_valid_column(self.board, col):
            cx = col * CELL_SIZE + CELL_SIZE // 2
            cy = CELL_SIZE // 2
            color = COLOR_P1 if self.turn == PLAYER_1 else COLOR_P2
            # Vẽ với opacity giả (màu nhạt hơn)
            self.canvas.create_oval(
                cx - RADIUS, cy - RADIUS,
                cx + RADIUS, cy + RADIUS,
                fill="#663333" if self.turn == PLAYER_1 else "#666600",
                outline=color, width=2,
                dash=(4, 4)
            )

    # ──────────────────────────────────
    #  XỬ LÝ SỰ KIỆN CLICK CHUỘT
    # ──────────────────────────────────

    def _on_click(self, event):
        """Xử lý khi người dùng click vào bàn cờ.
        
        Quy trình:
          1. Nếu game đã kết thúc / đang pause / đang lượt AI → bỏ qua
          2. Tính cột từ tọa độ X của chuột: col = x // CELL_SIZE
          3. Kiểm tra cột hợp lệ
          4. Thả xu Người chơi, cập nhật bàn cờ
          5. Kiểm tra thắng/hòa
          6. Nếu chưa kết thúc → lượt AI (chế độ PVE) hoặc chuyển lượt (PVP)
        """
        if self.game_over or self.paused:
            return

        # Trong PVE, chỉ xử lý click khi đến lượt PLAYER_1
        if self.mode == "pve" and self.turn != PLAYER_1:
            return

        # Tính cột từ tọa độ X
        col = event.x // CELL_SIZE

        # Kiểm tra tọa độ hợp lệ
        if not (0 <= col < COLS):
            return

        # Kiểm tra cột chưa đầy
        if not is_valid_column(self.board, col):
            self._flash_column_full(col)  # Hiệu ứng cảnh báo
            return

        # Thả xu người chơi hiện tại
        self._make_move(col, self.turn)

    def _make_move(self, col: int, player: int):
        """Thực hiện nước đi: thả xu, cập nhật board, kiểm tra thắng/hòa."""
        row = get_next_open_row(self.board, col)
        drop_piece(self.board, row, col, player)
        self._draw_board()

        # Kiểm tra thắng
        winning = check_win(self.board, player)
        if winning:
            self._draw_board(winning_cells=winning)
            self._end_game(winner=player)
            return

        # Kiểm tra hòa
        if is_board_full(self.board):
            self._end_game(winner=None)
            return

        # Chuyển lượt
        self.turn = PLAYER_2 if player == PLAYER_1 else PLAYER_1
        self._set_active_player(self.turn)
        self._reset_timer()

        # Trong PVE, lượt AI → gọi AI sau 400ms để không block UI
        if self.mode == "pve" and self.turn == PLAYER_2:
            self.after(400, self._ai_move)

    def _ai_move(self):
        """Gọi AI tính toán và thực hiện nước đi.
        
        Chạy trong luồng chính (main thread) sau delay nhỏ.
        AI sử dụng hàm get_best_ai_move() đã được tối ưu.
        """
        if self.game_over or self.paused:
            return

        # Lấy nước đi tốt nhất từ AI
        best_col = get_best_ai_move(self.board, depth=AI_DEPTH)

        # Thực hiện nước đi
        self._make_move(best_col, PLAYER_2)

    # ──────────────────────────────────
    #  TIMER (ĐÔI HỒ ĐẾM NGƯỢC)
    # ──────────────────────────────────

    def _start_timer(self):
        """Bắt đầu đồng hồ đếm ngược."""
        self._tick()

    def _tick(self):
        """Mỗi giây trừ 1, hiển thị lên label.
        
        Khi hết giờ → lượt bị bỏ qua (chuyển lượt hoặc AI đi).
        """
        if self.game_over or self.paused:
            return

        self.lbl_timer.configure(text=f"0:{self.timer_val:02d}")

        if self.timer_val <= 0:
            # Hết giờ → xử lý tùy chế độ
            self._on_timer_expired()
            return

        self.timer_val -= 1
        self.timer_job = self.after(1000, self._tick)

    def _reset_timer(self):
        """Reset đồng hồ về TIMER_SECONDS."""
        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.timer_val = TIMER_SECONDS
        self.timer_job = self.after(1000, self._tick)

    def _on_timer_expired(self):
        """Khi hết giờ: tự động chọn cột tốt nhất (hoặc ngẫu nhiên)."""
        if self.game_over:
            return

        valid = get_valid_columns(self.board)
        if not valid:
            return

        # Chọn cột giữa nếu còn, nếu không chọn ngẫu nhiên
        col = COLS // 2 if is_valid_column(self.board, COLS // 2) else random.choice(valid)
        self._make_move(col, self.turn)

    # ──────────────────────────────────
    #  PAUSE MENU
    # ──────────────────────────────────

    def _toggle_pause(self):
        """Bật/tắt menu Pause."""
        if self.game_over:
            return
        if self.paused:
            self._resume_game()
        else:
            self._pause_game()

    def _pause_game(self):
        """Hiển thị overlay Pause Menu."""
        self.paused = True
        if self.timer_job:
            self.after_cancel(self.timer_job)

        # Overlay nền mờ
        self.pause_overlay = tk.Frame(self, bg=COLOR_PAUSE_BG)
        self.pause_overlay.place(
            x=self.canvas.winfo_x() + self.row_frame.winfo_x(),
            y=self.canvas.winfo_y() + self.row_frame.winfo_y() + 30,
            width=BOARD_W, height=BOARD_H
        )

        # Container menu chính (bo viền)
        menu_frame = tk.Frame(self.pause_overlay, bg="#DD0066",
                               bd=3, relief=tk.RAISED)
        menu_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER,
                         width=200, height=180)

        tk.Label(menu_frame, text="PAUSE", bg="#DD0066", fg=COLOR_TEXT,
                  font=("Arial", 22, "bold"), pady=10).pack()

        # Nút Resume
        self._pause_btn(menu_frame, "Resume", self._resume_game)
        # Nút Reset
        self._pause_btn(menu_frame, "Reset",  self._reset_game)
        # Nút Exit
        self._pause_btn(menu_frame, "Exit",   self.master.show_main_menu)

    def _pause_btn(self, parent, text: str, command):
        """Tạo nút trong Pause Menu."""
        tk.Button(
            parent, text=text, command=command,
            bg=COLOR_BTN_BLUE, fg=COLOR_TEXT,
            font=("Arial", 11, "bold"),
            relief=tk.FLAT, padx=30, pady=4,
            activebackground="#0088FF",
            cursor="hand2"
        ).pack(pady=3)

    def _resume_game(self):
        """Tiếp tục game sau khi Pause."""
        if hasattr(self, "pause_overlay"):
            self.pause_overlay.destroy()
        self.paused = False
        self.timer_job = self.after(1000, self._tick)

        # Nếu đang lượt AI trong PVE --> tiếp tục AI đánh
        if self.mode == "pve" and self.turn == PLAYER_2:
            self.after(400, self._ai_move)

    # ──────────────────────────────────
    #  KẾT THÚC GAME
    # ──────────────────────────────────

    def _end_game(self, winner):
        """Kết thúc game: dừng timer, hiển thị Game Over bar.
        
        Tham số:
            winner : PLAYER_1, PLAYER_2, hoặc None (hòa)
        """
        self.game_over = True
        if self.timer_job:
            self.after_cancel(self.timer_job)

        # Xác định text thông báo
        if winner == PLAYER_1:
            msg = "P1 win!" if self.mode == "pvp" else "You win!"
            msg_color = COLOR_P1
        elif winner == PLAYER_2:
            msg = "P2 win!" if self.mode == "pvp" else "AI win!"
            msg_color = COLOR_P2
        else:
            msg = "Draw!"
            msg_color = "#AAAAAA"

        # Thanh kết quả hiển thị trên bàn cờ
        top = self.canvas.winfo_y() + self.row_frame.winfo_y() + 25
        left = self.canvas.winfo_x() + self.row_frame.winfo_x()

        result_frame = tk.Frame(self, bg=COLOR_BG)
        result_frame.place(x=left, y=top - 30, width=BOARD_W)

        # Nút Reset
        tk.Button(
            result_frame, text="Reset",
            command=self._reset_game,
            bg=COLOR_ACCENT, fg="black",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT, padx=10, cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)

        # Nhãn winner
        tk.Label(
            result_frame, text=msg,
            bg=msg_color, fg=COLOR_TEXT,
            font=("Arial", 12, "bold"),
            padx=10, pady=2
        ).pack(side=tk.LEFT, padx=2)

        # Nút Exit
        tk.Button(
            result_frame, text="Exit",
            command=self.master.show_main_menu,
            bg="#555555", fg=COLOR_TEXT,
            font=("Arial", 10, "bold"),
            relief=tk.FLAT, padx=10, cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)

        self.result_frame = result_frame  # Lưu để destroy khi reset

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

    def _flash_column_full(self, col: int):
        """Hiệu ứng nhấp nháy cột đầy để báo lỗi."""
        cx = col * CELL_SIZE + CELL_SIZE // 2
        flash_id = self.canvas.create_rectangle(
            col * CELL_SIZE, 0,
            (col + 1) * CELL_SIZE, BOARD_H,
            fill="#FF0000", stipple="gray25", outline=""
        )
        # Tự xóa sau 300ms
        self.after(300, lambda: self.canvas.delete(flash_id))


# ─────────────────────────────────────────────────────────────
#  ĐIỂM KHỞI CHẠY (Entry Point)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = Connect4App()
    app.mainloop()
