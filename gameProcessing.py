import time
import chess
import numpy as np
from boardScanner import BoardScanner

# Constants
STATE_FILE = "board_state.txt"
HUMAN_MOVE_FILE = "human_move.txt"

def matrix_to_fen_part(matrix):
    """Converts the 8x8 occupancy matrix to a simplified string for comparison."""
    return "".join(map(str, matrix.flatten()))

def get_move_from_matrices(old_matrix, new_matrix):
    """
    Detects which squares changed to identify a move.
    Returns (from_square_index, to_square_index)
    """
    diff = new_matrix.astype(int) - old_matrix.astype(int)
    from_sq = np.where(diff == -1) # Was occupied, now empty
    to_sq = np.where(diff == 1)    # Was empty, now occupied
    
    if len(from_sq[0]) == 1 and len(to_sq[0]) == 1:
        # Convert (row, col) to chess.Square
        # boardScanner row 0 is top (rank 8), chess lib rank 0 is bottom
        f_idx = chess.square(from_sq[1][0], 7 - from_sq[0][0])
        t_idx = chess.square(to_sq[1][0], 7 - to_sq[0][0])
        return chess.Move(f_idx, t_idx)
    return None

def main():
    scanner = BoardScanner()
    board = chess.Board()
    
    # Initialize state file
    with open(STATE_FILE, "w") as f:
        f.write(f"{board.fen()}\n\nNone")

    print("Game Started. White (Human) to move physically.")

    while not board.is_game_over():
        current_matrix = scanner.get_occupancy_state()
        if current_matrix is None:
            continue

        if board.turn == chess.WHITE:
            # OPTION A: Detect move via Camera
            # (Compares current physical state vs expected board state)
            # For simplicity, we can also wait for GUI input as you requested
            
            if os.path.exists(HUMAN_MOVE_FILE):
                with open(HUMAN_MOVE_FILE, "r") as f:
                    move_uci = f.read().strip()
                
                if move_uci:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        board.push(move)
                        # Update state for GUI
                        with open(STATE_FILE, "w") as f:
                            f.write(f"{board.fen()}\n{move_uci}\nHuman")
                        os.remove(HUMAN_MOVE_FILE)
                        print(f"Human moved: {move_uci}. Waiting for you to move Black...")

        else:
            # STOCKFISH TURN
            # In a real setup, Stockfish moves here. 
            # Since no arm, we pick best move and tell the user to move it.
            import random
            legal_moves = list(board.generate_legal_moves())
            engine_move = random.choice(legal_moves) # Placeholder for Stockfish
            
            # Update GUI to show the "Hint" of what to move
            with open(STATE_FILE, "w") as f:
                f.write(f"{board.fen()}\n{engine_move.uci()}\nStockfish")
            
            print(f"Stockfish wants to move: {engine_move.uci()}")
            print("Please move the physical piece, then press Enter.")
            input("Press Enter once physical move is complete...")
            
            board.push(engine_move)
            # Final state update after physical confirmation
            with open(STATE_FILE, "w") as f:
                f.write(f"{board.fen()}\n{engine_move.uci()}\nStockfish")

        time.sleep(1)

if __name__ == "__main__":
    import os
    main()