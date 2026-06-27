import cv2
import mediapipe as mp
import numpy as np
import easyocr

# Initialize EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Webcam
cap = cv2.VideoCapture(0)

# Drawing canvas
canvas = np.zeros((480, 640, 3), dtype=np.uint8)

prev_x, prev_y = 0, 0
detected_letter = ""

print("\nControls:")
print("Draw using index finger")
print("Press S → Predict Alphabet")
print("Press C → Clear")
print("Press Q → Quit\n")

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            h, w, c = frame.shape
            index_tip = hand_landmarks.landmark[8]

            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            # Draw circle on fingertip
            cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)

            if prev_x == 0 and prev_y == 0:
                prev_x, prev_y = x, y

            # Draw line on canvas
            cv2.line(canvas, (prev_x, prev_y), (x, y), (255, 255, 255), 8)

            prev_x, prev_y = x, y
    else:
        prev_x, prev_y = 0, 0

    # Combine frame and canvas
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_canvas, 50, 255, cv2.THRESH_BINARY)
    canvas_colored = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    combined = cv2.addWeighted(frame, 0.7, canvas_colored, 0.3, 0)

    # Show detected letter
    cv2.putText(combined, f"Detected: {detected_letter}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2)

    cv2.imshow("Alphabet Detector (Air Draw)", combined)

    key = cv2.waitKey(1) & 0xFF

    # Predict
    if key == ord('s'):
        result = reader.readtext(thresh, detail=0)
        if result:
            detected_letter = result[0]
        else:
            detected_letter = "Not Clear"

    # Clear
    elif key == ord('c'):
        canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        detected_letter = ""

    # Quit
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()