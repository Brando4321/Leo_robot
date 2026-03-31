# calibrate.py
import cv2
import numpy as np
from boardScanner import CAMERA_INDEX  # Use the shared constant

clicked_points = []

def mouse_callback(event, x, y, flags, param):
    global clicked_points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(clicked_points) < 4:
            clicked_points.append([x, y])
            print(f"Clicked point {len(clicked_points)}/4: ({x}, {y})")
        else:
            print("Already have 4 points. Press 'r' to reset.")

target_size = 800
target_corners = np.float32([
    [0,           0],
    [target_size, 0],
    [0,           target_size],
    [target_size, target_size],
])

cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print(f"Error: Cannot open webcam at index {CAMERA_INDEX}")
    exit()

window_name = "Original (Click 4 corners)"
cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, mouse_callback)

print("\n--- Interactive Calibration Tool ---")
print("Place your EMPTY board under the camera.")
print("\nClick the 4 corners in this order:")
print("  1. Top-Left")
print("  2. Top-Right")
print("  3. Bottom-Left")
print("  4. Bottom-Right")
print("\nControls:")
print("  's' — save empty_board.png and print coordinates")
print("  'r' — reset clicked points")
print("  'q' — quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame.")
        break

    # Draw clicked points
    for i, point in enumerate(clicked_points):
        cv2.circle(frame, tuple(point), 5, (0, 255, 0), -1)
        cv2.putText(frame, str(i + 1), (point[0] + 10, point[1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    warped = np.zeros((target_size, target_size, 3), dtype=np.uint8)

    if len(clicked_points) == 4:
        board_corners = np.float32(clicked_points)
        perspective_matrix = cv2.getPerspectiveTransform(board_corners, target_corners)
        warped = cv2.warpPerspective(frame, perspective_matrix, (target_size, target_size))

    cv2.imshow(window_name, frame)
    cv2.imshow("Warped (Press 's' to save)", warped)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        if len(clicked_points) == 4:
            gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
            cv2.imwrite("empty_board.png", gray_warped)
            print("\nSUCCESS: 'empty_board.png' saved!")
            print("\n--- Copy these into boardScanner.py ---")
            print("self.board_corners = np.float32([")
            labels = ["Top-left", "Top-right", "Bottom-left", "Bottom-right"]
            for i, (pt, label) in enumerate(zip(clicked_points, labels)):
                comma = "," if i < 3 else ""
                print(f"    [{pt[0]}, {pt[1]}]{comma}  # {label}")
            print("])")
            print("\nPress 'q' to quit.")
        else:
            print("Error: Click all 4 corners before saving.")

    elif key == ord('r'):
        clicked_points = []
        print("\nPoints reset. Click the 4 corners again.")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()