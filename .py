import cv2
import numpy as np
import random

# List of words to draw
words = ["cat", "house", "tree", "car", "sun", "flower", "dog"]
word_to_draw = random.choice(words)
print(f"Your word to draw is: {word_to_draw}")

# Create a white canvas
canvas = np.ones((500, 500, 3), dtype=np.uint8) * 255

drawing = False  # True if mouse is pressed
last_point = None

# Mouse callback function
def draw(event, x, y, flags, param):
    global drawing, last_point
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        last_point = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        cv2.line(canvas, last_point, (x, y), (0, 0, 0), 5)
        last_point = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        last_point = None

cv2.namedWindow("Guess the Drawing")
cv2.setMouseCallback("Guess the Drawing", draw)

print("Draw the word on the canvas. Press 'q' to quit and reveal the word.")

while True:
    cv2.imshow("Guess the Drawing", canvas)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()
print(f"The word was: {word_to_draw}")
