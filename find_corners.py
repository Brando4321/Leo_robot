# find_corners.py
# Run this, click the 4 corners of the board in order, and it prints
# the exact coordinates to paste into boardScanner.py
import cv2
import numpy as np

CAMERA_INDEX = 0

clicked = []

def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(clicked) < 4:
        clicked.append((x, y))
        print(f"Point {len(clicked)}: ({x}, {y})")
        if len(clicked) == 4:
            print("\n✅ Copy this into boardScanner.py:")
            print("self.board_corners = np.float32([")
            labels = ["Top-left", "Top-right", "Bottom-left", "Bottom-right"]
            for i, ((px, py), label) in enumerate(zip(clicked, labels)):
                comma = "," if i < 3 else ""
                print(f"    [{px}, {py}]{comma}  # {label}")
            print("])")

cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print(f"Cannot open camera {CAMERA_INDEX}")
    exit()

cv2.namedWindow("Click the 4 board corners: 1=Top-Left  2=Top-Right  3=Bottom-Left  4=Bottom-Right")
cv2.setMouseCallback("Click the 4 board corners: 1=Top-Left  2=Top-Right  3=Bottom-Left  4=Bottom-Right", click)

print("Click corners in this order:")
print("  1. Top-Left")
print("  2. Top-Right")
print("  3. Bottom-Left")
print("  4. Bottom-Right")
print("Press 'r' to reset, 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Draw clicked points
    for i, (x, y) in enumerate(clicked):
        cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)
        cv2.putText(frame, str(i+1), (x+10, y+10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    # Draw lines between points once we have all 4
    if len(clicked) == 4:
        pts = np.array(clicked, dtype=np.int32)
        # top edge
        cv2.line(frame, clicked[0], clicked[1], (0, 255, 0), 2)
        # bottom edge
        cv2.line(frame, clicked[2], clicked[3], (0, 255, 0), 2)
        # left edge
        cv2.line(frame, clicked[0], clicked[2], (0, 255, 0), 2)
        # right edge
        cv2.line(frame, clicked[1], clicked[3], (0, 255, 0), 2)

    cv2.imshow("Click the 4 board corners: 1=Top-Left  2=Top-Right  3=Bottom-Left  4=Bottom-Right", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        clicked.clear()
        print("Reset — click the 4 corners again")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()