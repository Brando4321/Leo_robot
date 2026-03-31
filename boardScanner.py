# boardScanner.py
import cv2
import numpy as np

CAMERA_INDEX = 0
DEBUG = True

class BoardScanner:
    def __init__(self, camera_index=CAMERA_INDEX, empty_board_img_path="empty_board.png"):
        print(f"Initializing camera (index {camera_index})...")
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open webcam at index {camera_index}")

        # Run find_corners.py to get correct values for your setup.
        # Order: top-left, top-right, bottom-left, bottom-right
        self.board_corners = np.float32([
      [718, 305],  # Top-left
    [1365, 275],  # Top-right
    [731, 987],  # Bottom-left
    [1564, 876]  # Bottom-right
])
    

        self.target_size = 800
        self.target_corners = np.float32([
            [0,                0],
            [self.target_size, 0],
            [0,                self.target_size],
            [self.target_size, self.target_size],
        ])

        self.perspective_matrix = cv2.getPerspectiveTransform(
            self.board_corners, self.target_corners
        )

        # --- THRESHOLDS ---
        self.PIXEL_DIFF_THRESHOLD = 10   # lower = more sensitive
        self.OCCUPANCY_THRESHOLD  = 0.40 # lowered — pieces showing 0.07-0.85
        self.ROI_MARGIN_FRACTION  = 0.30 # inset from square edges

        self.BLUR_KERNEL = 5

        # If your camera sees rank 1 at the TOP of the image, set this to True.
        # Flip discovered from debug screenshot — white is at top, black at bottom
        # but chess code expects rank 8 at top row (index 0).
        self.FLIP_BOARD = False

        # --- EMPTY BOARD BASELINE ---
        try:

            self.empty_board_warped = cv2.imread(empty_board_img_path)
            if self.empty_board_warped is None:
                raise IOError
            self.empty_board_warped = cv2.cvtColor(self.empty_board_warped, cv2.COLOR_BGR2GRAY)
            self.empty_board_warped = cv2.GaussianBlur(
                self.empty_board_warped, (self.BLUR_KERNEL, self.BLUR_KERNEL), 0
            )
            if self.FLIP_BOARD:
                self.empty_board_warped = cv2.flip(self.empty_board_warped, -1)
            print("Loaded empty board baseline.")
        except IOError:
            print("ERROR: 'empty_board.png' not found.")
            print("Run find_corners.py then calibrate.py first.")
            self.empty_board_warped = None

    def _get_warped_board(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        warped_color = cv2.warpPerspective(
            frame, self.perspective_matrix, (self.target_size, self.target_size)
        )
        if self.FLIP_BOARD:
            warped_color = cv2.flip(warped_color, -1)
        gray = cv2.cvtColor(warped_color, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (self.BLUR_KERNEL, self.BLUR_KERNEL), 0)
        return gray, warped_color

    def get_occupancy_state(self):
        if self.empty_board_warped is None:
            print("Cannot get occupancy state: no empty board baseline loaded.")
            return None
        
    

        warped_current, warped_color = self._get_warped_board()
        if warped_current is None:
            return None

        state_matrix = np.zeros((8, 8), dtype=int)
        square_size = self.target_size // 8
        roi_margin  = int(square_size * self.ROI_MARGIN_FRACTION)

        if DEBUG:
            debug_img = warped_color.copy()

        for r in range(8):
            for c in range(8):
                y1 = r * square_size + roi_margin
                y2 = (r + 1) * square_size - roi_margin
                x1 = c * square_size + roi_margin
                x2 = (c + 1) * square_size - roi_margin

                square_current = warped_current[y1:y2, x1:x2]
                square_empty   = self.empty_board_warped[y1:y2, x1:x2]

                diff = cv2.absdiff(square_current, square_empty)
                _, thresh = cv2.threshold(
                    diff, self.PIXEL_DIFF_THRESHOLD, 255, cv2.THRESH_BINARY
                )

                occupied_pixels = cv2.countNonZero(thresh)
                total_pixels    = square_current.size
                ratio           = occupied_pixels / total_pixels if total_pixels > 0 else 0
                print(f"Square ({r},{c}) ratio: {ratio:.3f}")
                occupied        = ratio > self.OCCUPANCY_THRESHOLD

                if occupied:
                    state_matrix[r, c] = 1

                if DEBUG:
                    color = (0, 255, 0) if occupied else (0, 0, 255)
                    cv2.rectangle(debug_img, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(debug_img, f"{ratio:.2f}", (x1 + 2, y1 + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

        if DEBUG:
            # draw a more visible border around the full board
            cv2.rectangle(debug_img, (0, 0), (self.target_size - 1, self.target_size - 1), (255, 255, 0), 3)

            # scale up debug window for better visibility
            scale_factor = 1.5
            debug_display = cv2.resize(
                debug_img,
                (int(self.target_size * scale_factor), int(self.target_size * scale_factor)),
                interpolation=cv2.INTER_LINEAR,
            )

            cv2.imshow("Debug (green=occupied, red=empty)", debug_display)
            cv2.waitKey(1)

        return state_matrix

    def __del__(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()