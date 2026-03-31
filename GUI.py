# GUI.py
import tkinter as tk
from tkinter import PhotoImage, font as tkfont
import chess
import threading
import time

STATE_FILE = "board_state.txt"  # Written by gameProcessing.py

BOARD_SIZE = 560
SQUARE     = BOARD_SIZE // 8
SIDEBAR    = 300
WIN_W      = BOARD_SIZE + 20 + SIDEBAR
WIN_H      = BOARD_SIZE + 20

DARK_SQ    = "#4a7c59"
LIGHT_SQ   = "#f0d9b5"
BG         = "#1a1a2e"
SIDEBAR_BG = "#16213e"
ACCENT     = "#e94560"
TEXT_CLR   = "#eaeaea"
DIM_TEXT   = "#7a8a99"
LAST_MOVE  = "#f6f66955"

# --- State ---
current_board     = chess.Board()
last_move_squares = []
selected_square   = None
move_history      = []   # list of (uci, side)

win = tk.Tk()
win.title("ACR — Chess Robot Viewer")
win.configure(bg=BG)
win.resizable(False, False)
win.geometry(f"{WIN_W}x{WIN_H}")

title_font = tkfont.Font(family="Courier", size=13, weight="bold")
label_font = tkfont.Font(family="Courier", size=9)
move_font  = tkfont.Font(family="Courier", size=11)
side_font  = tkfont.Font(family="Courier", size=10, weight="bold")
hint_font  = tkfont.Font(family="Courier", size=14, weight="bold")
small_font = tkfont.Font(family="Courier", size=8)

# ── Board canvas ───────────────────────────────────────────────────────────
board_canvas = tk.Canvas(win, width=BOARD_SIZE + 20, height=WIN_H,
                          bg=BG, highlightthickness=0)
board_canvas.place(x=0, y=0)

# ── Sidebar ────────────────────────────────────────────────────────────────
sidebar = tk.Frame(win, bg=SIDEBAR_BG, width=SIDEBAR, height=WIN_H)
sidebar.place(x=BOARD_SIZE + 20, y=0)
sidebar.pack_propagate(False)

tk.Label(sidebar, text="◈ ACR CHESS ENGINE", font=title_font,
         bg=SIDEBAR_BG, fg=ACCENT).pack(pady=(18, 2))
tk.Label(sidebar, text="Autonomous Chess Robot", font=small_font,
         bg=SIDEBAR_BG, fg=DIM_TEXT).pack(pady=(0, 10))
tk.Frame(sidebar, bg=ACCENT, height=1).pack(fill=tk.X, padx=16)

tk.Label(sidebar, text="STOCKFISH LAST MOVE", font=small_font,
         bg=SIDEBAR_BG, fg=DIM_TEXT).pack(pady=(12, 2))
hint_frame = tk.Frame(sidebar, bg="#0f3460")
hint_frame.pack(padx=16, fill=tk.X)
hint_var = tk.StringVar(value="—")
tk.Label(hint_frame, textvariable=hint_var, font=hint_font,
         bg="#0f3460", fg="#00d4ff", pady=10).pack()

status_var = tk.StringVar(value="Waiting for game...")
tk.Label(sidebar, textvariable=status_var, font=side_font,
         bg=SIDEBAR_BG, fg=TEXT_CLR, wraplength=260).pack(pady=(12, 2))
turn_var = tk.StringVar(value="⬜ White to move")
tk.Label(sidebar, textvariable=turn_var, font=label_font,
         bg=SIDEBAR_BG, fg=DIM_TEXT).pack(pady=(0, 8))
tk.Frame(sidebar, bg=ACCENT, height=1).pack(fill=tk.X, padx=16)

tk.Label(sidebar, text="MOVE HISTORY", font=small_font,
         bg=SIDEBAR_BG, fg=DIM_TEXT).pack(pady=(10, 4))
hist_frame = tk.Frame(sidebar, bg=SIDEBAR_BG)
hist_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
hist_scroll = tk.Scrollbar(hist_frame, bg=SIDEBAR_BG)
hist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
hist_list = tk.Listbox(hist_frame, font=move_font, bg=SIDEBAR_BG,
                        fg=TEXT_CLR, selectbackground=ACCENT,
                        relief=tk.FLAT, bd=0, highlightthickness=0,
                        yscrollcommand=hist_scroll.set)
hist_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
hist_scroll.config(command=hist_list.yview)

# ── Piece images ───────────────────────────────────────────────────────────
piece_images = {}
try:
    names = {
        'white_pawn':'white-pawn','white_bishop':'white-bishop',
        'white_rook':'white-rook','white_king':'white-king',
        'white_queen':'white-queen','white_knight':'white-knight',
        'black_pawn':'black-pawn','black_bishop':'black-bishop',
        'black_rook':'black-rook','black_king':'black-king',
        'black_queen':'black-queen','black_knight':'black-knight',
    }
    for key, fname in names.items():
        piece_images[key] = PhotoImage(file=f"pieces-png/{fname}.png")
except tk.TclError as e:
    print(f"Image load error: {e}")

symbol_map = {
    'r':'black_rook','q':'black_queen','k':'black_king',
    'n':'black_knight','p':'black_pawn','b':'black_bishop',
    'R':'white_rook','Q':'white_queen','K':'white_king',
    'N':'white_knight','P':'white_pawn','B':'white_bishop',
}
cols_labels = ['a','b','c','d','e','f','g','h']
OFFSET_X = 20

# ── Draw ───────────────────────────────────────────────────────────────────
def sq_xy(col, row):
    return OFFSET_X + col * SQUARE, row * SQUARE

def draw_board(board_state):
    board_canvas.delete("all")

    # Highlight selected square
    if selected_square is not None:
        col, row = chess.square_file(selected_square), chess.square_rank(selected_square)
        x, y = sq_xy(col, row)
        board_canvas.create_rectangle(x, y, x + SQUARE, y + SQUARE,
                                       fill="#26a69a", outline="")

    for row in range(8):
        board_canvas.create_text(OFFSET_X - 10, row * SQUARE + SQUARE // 2,
                                  text=str(8 - row), font=label_font, fill=DIM_TEXT)
    for col in range(8):
        board_canvas.create_text(OFFSET_X + col * SQUARE + SQUARE // 2,
                                  8 * SQUARE + 8, text=cols_labels[col],
                                  font=label_font, fill=DIM_TEXT)

    for row_disp in range(8):
        for col in range(8):
            row_chess = 7 - row_disp # chess lib has rank 1 at the bottom
            x, y = sq_xy(col, row_disp)
            color = LIGHT_SQ if (row_disp + col) % 2 == 0 else DARK_SQ
            board_canvas.create_rectangle(x, y, x+SQUARE, y+SQUARE,
                                           fill=color, outline="")

            sq_idx = chess.square(col, row_chess)
            if sq_idx in last_move_squares:
                board_canvas.create_rectangle(x, y, x+SQUARE, y+SQUARE,
                                               fill=LAST_MOVE, outline="",
                                               stipple="gray50")

            piece = board_state.piece_at(sq_idx)
            key   = symbol_map.get(str(piece) if piece else "")
            if key and key in piece_images:
                board_canvas.create_image(x + SQUARE//2, y + SQUARE//2,
                                           anchor=tk.CENTER,
                                           image=piece_images[key])

    board_canvas.create_rectangle(OFFSET_X, 0,
                                   OFFSET_X + 8*SQUARE, 8*SQUARE,
                                   outline=ACCENT, width=2)

def update_sidebar(last_uci, last_side, board_state):
    if board_state.is_game_over():
        outcome = board_state.outcome()
        if outcome and outcome.winner == chess.WHITE:
            status_var.set("🏆 Human wins!")
        elif outcome and outcome.winner == chess.BLACK:
            status_var.set("🤖 Stockfish wins!")
        else:
            status_var.set("🤝 Draw!")
        turn_var.set("")
    else:
        if board_state.turn == chess.WHITE:
            turn_var.set("⬜ White to move (Human)")
            status_var.set("Waiting for your move...")
        else:
            turn_var.set("⬛ Black to move (Stockfish)")
            status_var.set("Stockfish is thinking...")

    if last_side == "Stockfish" and last_uci:
        hint_var.set(last_uci)

# ── File watcher ───────────────────────────────────────────────────────────
last_fen = ""

def watch_state():
    global current_board, last_move_squares, last_fen

    while True:
        try:
            with open(STATE_FILE, 'r') as f:
                lines = f.read().splitlines()

            if len(lines) >= 1:
                fen      = lines[0].strip()
                last_uci = lines[1].strip() if len(lines) > 1 else ""
                last_side= lines[2].strip() if len(lines) > 2 else ""

                if fen and fen != last_fen:
                    last_fen = fen
                    new_board = chess.Board(fen)

                    # Highlight last move squares
                    if last_uci:
                        try:
                            m = chess.Move.from_uci(last_uci)
                            last_move_squares = [m.from_square, m.to_square]
                        except Exception:
                            last_move_squares = []

                    # Add to history if there's a new move
                    if last_uci and (not move_history or move_history[-1][0] != last_uci):
                        move_history.append((last_uci, last_side))
                        move_num = (len(move_history) + 1) // 2
                        prefix = f"{move_num}." if last_side == "Human" else "   "
                        label  = f"{prefix} {'W' if last_side == 'Human' else 'B'}  {last_uci}"
                        win.after(0, _add_history_item, label, last_side)

                    current_board = new_board
                    win.after(0, draw_board, current_board)
                    win.after(0, update_sidebar, last_uci, last_side, current_board)

        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"State watcher error: {e}")

        time.sleep(0.3)

def _add_history_item(label, side):

    hist_list.insert(tk.END, label)

    idx = hist_list.size() - 1

    hist_list.itemconfig(idx, fg=TEXT_CLR if side == "Human" else "#00d4ff")

    hist_list.see(tk.END)



def on_board_click(event):

    global selected_square

    if current_board.turn != chess.WHITE:

        return # Not human's turn



    col = (event.x - OFFSET_X) // SQUARE

    row_disp = event.y // SQUARE

    row_chess = 7 - row_disp



    if not (0 <= col < 8 and 0 <= row_chess < 8):

        return



    clicked_square = chess.square(col, row_chess)



    if selected_square is None:

        # If no piece is selected, select the clicked one if it's ours

        piece = current_board.piece_at(clicked_square)

        if piece and piece.color == chess.WHITE:

            selected_square = clicked_square

            draw_board(current_board)

    else:

        # A piece is already selected, try to make a move

                move = chess.Move(selected_square, clicked_square)

                if move in current_board.legal_moves:

                    move_uci = move.uci()

                    print(f"Human played: {move_uci}")

                    try:

                        with open("human_move.txt", 'w') as f:

                            f.write(move_uci)

                    except Exception as e:

                        print(f"Error writing to human_move.txt: {e}")

                    

                    selected_square = None

                    # The board will be redrawn by the watcher thread

                else:

                    # Invalid move, maybe select another piece of the same color

                    piece = current_board.piece_at(clicked_square)

                    if piece and piece.color == chess.WHITE:

                        selected_square = clicked_square

                    else:

                        selected_square = None # Deselect

                    draw_board(current_board)



# ── Start ──────────────────────────────────────────────────────────────────

draw_board(current_board)

update_sidebar("", "", current_board)

board_canvas.bind("<Button-1>", on_board_click)

threading.Thread(target=watch_state, daemon=True).start()

win.mainloop()
