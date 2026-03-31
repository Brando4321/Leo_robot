# cv_input.py
import chess
import numpy as np
import time
import os
from boardScanner import BoardScanner

HUMAN_MOVE_FILE  = "human_move.txt"
STATE_FILE       = "board_state.txt"

def get_current_board():
    """Reads the FEN from board_state.txt so the CV knows whose turn it is."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                return chess.Board(lines[0].strip())
    return chess.Board()

def convert_to_matrix(board):
    matrix = np.zeros((8, 8), dtype=int)
    for r in range(8):
        for c in range(8):
            # c is column (0-7), 7-r is rank (0-7)
            square = chess.square(c, 7 - r) 
            if board.piece_at(square):
                matrix[r, c] = 1
    return matrix

def main():
    scanner = BoardScanner(camera_index=0)
    print("CV System Online. Monitoring for White's move...")

    while True:
        board = get_current_board()
        
        # Only detect moves when it is White's (Human) turn 
        if board.turn == chess.WHITE:
            state_A = convert_to_matrix(board)
            current_cv = scanner.get_occupancy_state()

            if current_cv is not None and not np.array_equal(state_A, current_cv):
                print("Movement detected! Waiting 2s for hand to clear...")
                time.sleep(2.0) 
                state_B = scanner.get_occupancy_state()

                best_move = None
                min_diff = 999
                
                # Check every legal move to see which one matches the camera 
                for move in board.legal_moves:
                    board.push(move)
                    projected = convert_to_matrix(board)
                    board.pop()
                    
                    diff = np.sum(np.abs(projected - state_B))
                    if diff < min_diff:
                        min_diff = diff
                        best_move = move
                
                # If the best match is close enough, write the file 
                if best_move and min_diff <= 2:
                    move_uci = best_move.uci()
                    print(f"✅ MATCH FOUND: {move_uci} (Diff: {min_diff})")
                    with open(HUMAN_MOVE_FILE, 'w') as f:
                        f.write(move_uci + '\n')
                    print(f"File '{HUMAN_MOVE_FILE}' updated. Waiting for Brain...")
                    time.sleep(5) # Cooldown to prevent double-writes
                else:
                    print(f"❌ No legal move matches. Closest was {best_move} with {min_diff} errors.")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()