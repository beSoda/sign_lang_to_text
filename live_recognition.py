import cv2
import mediapipe as mp
import torch
import torch.nn as nn
import numpy as np
from datetime import datetime


class GestureClassifier(nn.Module):
    def __init__(self, input_size=63, hidden_size=128, num_classes=5):
        super(GestureClassifier, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, num_classes)
        )

    def forward(self, x):
        return self.net(x)


class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
               'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
               'U', 'V', 'W', 'X', 'Y', 'Z']

model = GestureClassifier(input_size=63, hidden_size=128,
                          num_classes=len(class_names))
model.load_state_dict(torch.load('gesture_classifier.pth',
                      map_location=torch.device('cpu')))
model.eval()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
spoken_gesture = None


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])

            input_tensor = torch.tensor(
                landmarks, dtype=torch.float32).unsqueeze(0)

            with torch.no_grad():
                output = model(input_tensor)
                predicted_idx = torch.argmax(output, dim=1).item()
                predicted_gesture = class_names[predicted_idx]
                confidence = torch.softmax(output, dim=1)[
                    0][predicted_idx].item()

                result_json = {
                    "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    "gesture": predicted_gesture,
                    "confidence": round(confidence, 4)
                }

            cv2.putText(frame, f'Gesture: {predicted_gesture}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    else:
        spoken_gesture = None

    cv2.imshow('Sign Language Recognition', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
