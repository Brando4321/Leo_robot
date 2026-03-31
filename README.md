## **LEO: Low-cost Electromechanical Operator**

**LEO** is an integrated electromechanical system that bridges the gap between digital chess strategy and physical gameplay. By combining **Computer Vision (OpenCV)**, a custom **Minimax AI engine**, and a high-precision **Robotic Arm**, LEO allows users to compete against a sophisticated AI that physically manipulates pieces on a real-world chessboard.

The project serves as a comprehensive application of **Data Structures and Algorithms (DSA)**, game theory, and hardware-software integration.

---

### **Core Features**

* **Vision-Based Board Tracking**: Utilizes a camera feed and `boardScanner.py` to detect physical piece occupancy in real-time, ensuring the digital engine stays synchronized with the physical board.
* **Custom AI Engine**: Features a Minimax algorithm enhanced with **Alpha-Beta Pruning** and a specialized evaluation function that accounts for both linear piece value and non-linear king safety strategies.
* **Interactive GUI**: A professional-grade **Tkinter** interface that displays the current FEN state, move history, and Stockfish "hints" for manual piece placement during testing.
* **Hardware Integration**: Maps digital UCI moves to specific 3D coordinates stored in `controlMovements.json` to drive robotic arm servos.
* **Cross-Platform Communication**: Employs a robust file-watching system to enable seamless data exchange between the Python backend, the OpenCV vision layer, and the Arduino-controlled arm.

---

### **Technical Stack**

| Layer | Technologies Used |
| :--- | :--- |
| **Logic & AI** | Python, `python-chess` library, Minimax w/ Alpha-Beta Pruning |
| **Computer Vision** | OpenCV, NumPy, Perspective Transformation, Image Subtraction |
| **Frontend** | Tkinter (Python GUI Library) |
| **Hardware** | Arduino, Servo Motors, C++, JSON Coordinate Mapping |

---

### **How It Works**

1.  **Calibration**: Users define the board boundaries using `find_corners.py` to generate a perfect top-down warped view for the AI.
2.  **Move Detection**: The system monitors physical changes. When a human moves a piece, the vision system validates the move against the legal move set.
3.  **Engine Calculation**: The AI calculates the optimal response based on a weighted evaluation of the board's defensive and aggressive potential.
4.  **Physical Execution**: The move is sent to the Arduino, which translates the UCI coordinates into servo movements to physically relocate the piece.

---

### **Authors**
* **Brandon Solorio** – Lead Developer & Computer Science Student at Reedley College.
* **Kenneth Flores** –  Lead Mechanical Engineer Student at Reedley College.
* **Nelsi Valdovinos ** Developer & Computer Science Student at Reedley College.
