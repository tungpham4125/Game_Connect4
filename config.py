"""
=============================================================
CONFIG.PY - Hằng số & Cấu hình toàn cục (Global Constants)
=============================================================
File này KHÔNG import bất kỳ file nào khác trong project.
Tất cả các file còn lại đều import từ file này.
=============================================================
"""

# ─────────────────────────────────────────────────────────────
#  KÍCH THƯỚC BÀN CỜ
# ─────────────────────────────────────────────────────────────
ROWS       = 6          # Số hàng bàn cờ
COLS       = 7          # Số cột bàn cờ

# ─────────────────────────────────────────────────────────────
#  MÃ NGƯỜI CHƠI
# ─────────────────────────────────────────────────────────────
EMPTY      = 0          # Ô trống
PLAYER_1   = 1          # Người chơi 1 (Đỏ)
PLAYER_2   = 2          # Người chơi 2 / AI (Vàng)

# ─────────────────────────────────────────────────────────────
#  KÍCH THƯỚC GIAO DIỆN
# ─────────────────────────────────────────────────────────────
CELL_SIZE  = 75         # Kích thước mỗi ô (pixel)
RADIUS     = 30         # Bán kính hình tròn xu
PAD_X      = 40         # Padding ngang bàn cờ
PAD_Y      = 20         # Padding dọc bàn cờ
BOARD_W    = COLS * CELL_SIZE   # Chiều rộng bàn cờ
BOARD_H    = ROWS * CELL_SIZE   # Chiều cao bàn cờ

# ─────────────────────────────────────────────────────────────
#  MÀU SẮC THEME
# ─────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────
#  CÀI ĐẶT AI & TIMER
# ─────────────────────────────────────────────────────────────
AI_DEPTH      = 5    # Độ sâu Minimax (tăng = AI mạnh hơn nhưng chậm hơn)
TIMER_SECONDS = 60   # Thời gian mỗi lượt (giây)
