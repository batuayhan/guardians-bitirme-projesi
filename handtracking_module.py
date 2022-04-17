import cv2
import mediapipe as mp
import time


class HandDetector():
    def __init__(self, mode=False, max_hands = 2, min_detection = 0.5, min_track = 0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.min_detection = min_detection
        self.min_track = min_track

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, self.min_detection, self.min_track)
        self.mp_draw = mp.solutions.drawing_utils


    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print("[INFO] handmarks: {}".format(results.multi_hand_landmarks))

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return img

    def findPostion(self, img, handNo = 0, draw = True):

        landmark_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[handNo]
            for index, lm in enumerate(my_hand.landmark):
                height, width, channel = img.shape
                cx, cy = int(lm.x * width), int(lm.y * height)
                landmark_list.append([index, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                # self.mp_draw.draw_landmarks(img, my_hand, self.mp_hands.HAND_CONNECTIONS)

        return landmark_list
   
def main():
    prev_time = 0
    cur_time = 0
    handDetector = HandDetector()
    cap = cv2.VideoCapture(0)
    while True:
        _, img = cap.read()
        img = handDetector.findHands(img)
        landmarks_list = handDetector.findPostion(img)
        if len(landmarks_list) != 0:
            print(landmarks_list[4])
        cur_time = time.time()
        fps = 1/(cur_time-prev_time)
        prev_time = cur_time

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()