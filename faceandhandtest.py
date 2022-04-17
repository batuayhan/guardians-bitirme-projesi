# It helps in identifying the faces
import cv2, sys, numpy, os
import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

prev_time = 0
cur_time = 0


size = 4
haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'datasets'


# Part 1: Create fisherRecognizer
print('Recognizing Face Please Be in sufficient Lights...')

# Create a list of images and a list of corresponding names
(images, labels, names, id) = ([], [], {}, 0)
for (subdirs, dirs, files) in os.walk(datasets):
    for subdir in dirs:
        names[id] = subdir
        subjectpath = os.path.join(datasets, subdir)
        for filename in os.listdir(subjectpath):
            path = subjectpath + '/' + filename
            label = id
            images.append(cv2.imread(path, 0))
            labels.append(int(label))
        id += 1
(width, height) = (130, 100)

# Create a Numpy array from the two lists above
(images, labels) = [numpy.array(lis) for lis in [images, labels]]

# OpenCV trains a model from the images
# NOTE FOR OpenCV2: remove '.face'
model = cv2.face.LBPHFaceRecognizer_create()
model.train(images, labels)

# Part 2: Use fisherRecognizer on camera stream
face_cascade = cv2.CascadeClassifier(haar_file)
webcam = cv2.VideoCapture(0)

elKaldirildiMi = False

while True:
    _, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    # print("[INFO] handmarks: {}".format(results.multi_hand_landmarks))
    

    if results.multi_hand_landmarks:
        if(elKaldirildiMi == False):
            elKaldirildiMi = True
            print("[INFO] El Kaldırıldı")
        for hand_landmarks in results.multi_hand_landmarks:
            for index, lm in enumerate(hand_landmarks.landmark):
                height, width, channel = img.shape
                cx, cy = int(lm.x * width), int(lm.y * height)
                cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    else:
        if(elKaldirildiMi == True):
            elKaldirildiMi = False
            print("[INFO] El İndirildi")
    cur_time = time.time()
    fps = 1/(cur_time-prev_time)
    prev_time = cur_time

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)


    #(_, im) = webcam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (width, height))
        # Try to recognize the face
        prediction = model.predict(face_resize)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)

        if prediction[1]<500:

            cv2.putText(img, '% s - %.0f' % (names[prediction[0]], prediction[1]), (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
        else:
            cv2.putText(img, 'not recognized', (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

    cv2.imshow('OpenCV', img)
    
    key = cv2.waitKey(10)
    if key == 27:
            break