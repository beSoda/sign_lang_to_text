import cv2
import mediapipe as mp
import csv
import os


# List out the Sign Language you want to add (remove trained so it wouldnt replace the current data)
# make sure to also add it into live_recognition line 25 class
gesture_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                'U', 'V', 'W', 'X', 'Y', 'Z']

SAMPLES_PER_GESTURE = 500
DATA_DIR = "gesture_data"
os.makedirs(DATA_DIR, exist_ok=True)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

for gesture in gesture_list:
    print(f"\n➡️ Show gesture: {gesture} – press Enter to begin")
    input()

    count = 0
    while count < SAMPLES_PER_GESTURE:
        success, frame = cap.read()
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                draw.draw_landmarks(frame, hand_landmarks,
                                    mp_hands.HAND_CONNECTIONS)

                keypoints = []
                for lm in hand_landmarks.landmark:
                    keypoints += [lm.x, lm.y, lm.z]

                with open(f"{DATA_DIR}/{gesture}.csv", 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(keypoints)

                count += 1

        cv2.putText(frame, f"{gesture}: {count}/{SAMPLES_PER_GESTURE}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Collecting Gesture Data", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

print("\n✅ Data collection done.")
cap.release()
cv2.destroyAllWindows()
