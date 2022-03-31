import cv2
import mediapipe as mp
import time
import utils, math
import sys, numpy, os


mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

prev_time = 0
cur_time = 0


size = 4
faceRecognitionHaarcascadeFile = 'haarcascade_frontalface_default.xml'
faceRecognitionDataSets = 'datasets'

# Create a list of images and a list of corresponding names
(images, labels, names, id) = ([], [], {}, 0)
for (subdirs, dirs, files) in os.walk(faceRecognitionDataSets):
    for subdir in dirs:
        names[id] = subdir
        subjectpath = os.path.join(faceRecognitionDataSets, subdir)
        for filename in os.listdir(subjectpath):
            path = subjectpath + '/' + filename
            label = id
            images.append(cv2.imread(path, 0))
            labels.append(int(label))
        id += 1


# Create a Numpy array from the two lists above
(images, labels) = [numpy.array(lis) for lis in [images, labels]]

# OpenCV trains a model from the images
# NOTE FOR OpenCV2: remove '.face'
model = cv2.face.LBPHFaceRecognizer_create()
model.train(images, labels)

# Part 2: Use fisherRecognizer on camera stream
face_cascade = cv2.CascadeClassifier(faceRecognitionHaarcascadeFile)







# variables 

CEF_COUNTER =0
TOTAL_BLINKS =0
# constants
CLOSED_EYES_FRAME =3
FONTS =cv2.FONT_HERSHEY_COMPLEX
# Left eyes indices 
LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
# right eyes indices
RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]  
map_face_mesh = mp.solutions.face_mesh


# camera object 
camera = cv2.VideoCapture(0)

# video recording
frame_width = int(camera.get(3))
frame_height = int(camera.get(4))
size = (frame_width, frame_height)
result = cv2.VideoWriter('filename.avi', cv2.VideoWriter_fourcc(*'MJPG'), 10, size)
riskyMomentsFacePath = 'RiskyMoments/Face'
riskyMomentsEyesPath = 'RiskyMoments/Eyes'

# landmark detection function 
def landmarksDetection(img, results, draw=False):
    img_height, img_width= img.shape[:2]
    # list[(x,y), (x,y)....]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw :
        [cv2.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]

    # returning the list of tuples for each landmarks 
    return mesh_coord

# Euclaidean distance 
def euclaideanDistance(point, point1):
    x, y = point
    x1, y1 = point1
    distance = math.sqrt((x1 - x)**2 + (y1 - y)**2)
    return distance

# Blinking Ratio
def blinkRatio(img, landmarks, right_indices, left_indices):
    # Right eyes 
    # horizontal line 
    rh_right = landmarks[right_indices[0]]
    rh_left = landmarks[right_indices[8]]
    # vertical line 
    rv_top = landmarks[right_indices[12]]
    rv_bottom = landmarks[right_indices[4]]
    # draw lines on right eyes 
    # cv2.line(img, rh_right, rh_left, utils.GREEN, 2)
    # cv2.line(img, rv_top, rv_bottom, utils.WHITE, 2)

    # LEFT_EYE 
    # horizontal line 
    lh_right = landmarks[left_indices[0]]
    lh_left = landmarks[left_indices[8]]

    # vertical line 
    lv_top = landmarks[left_indices[12]]
    lv_bottom = landmarks[left_indices[4]]

    rhDistance = euclaideanDistance(rh_right, rh_left)
    rvDistance = euclaideanDistance(rv_top, rv_bottom)

    lvDistance = euclaideanDistance(lv_top, lv_bottom)
    lhDistance = euclaideanDistance(lh_right, lh_left)

    reRatio = rhDistance/rvDistance
    leRatio = lhDistance/lvDistance

    ratio = (reRatio+leRatio)/2
    return ratio 

# Eyes Extrctor function,
def eyesExtractor(img, right_eye_coords, left_eye_coords):
    # converting color image to  scale image 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # getting the dimension of image 
    dim = gray.shape

    # creating mask from gray scale dim
    mask = numpy.zeros(dim, dtype=numpy.uint8)

    # drawing Eyes Shape on mask with white color 
    cv2.fillPoly(mask, [numpy.array(right_eye_coords, dtype=numpy.int32)], 255)
    cv2.fillPoly(mask, [numpy.array(left_eye_coords, dtype=numpy.int32)], 255)

    # showing the mask 
    # cv2.imshow('mask', mask)
    
    # draw eyes image on mask, where white shape is 
    eyes = cv2.bitwise_and(gray, gray, mask=mask)
    # change black color to gray other than eys 
    # cv2.imshow('eyes draw', eyes)
    eyes[mask==0]=155
    
    # getting minium and maximum x and y  for right and left eyes 
    # For Right Eye 
    r_max_x = (max(right_eye_coords, key=lambda item: item[0]))[0]
    r_min_x = (min(right_eye_coords, key=lambda item: item[0]))[0]
    r_max_y = (max(right_eye_coords, key=lambda item : item[1]))[1]
    r_min_y = (min(right_eye_coords, key=lambda item: item[1]))[1]

    # For LEFT Eye
    l_max_x = (max(left_eye_coords, key=lambda item: item[0]))[0]
    l_min_x = (min(left_eye_coords, key=lambda item: item[0]))[0]
    l_max_y = (max(left_eye_coords, key=lambda item : item[1]))[1]
    l_min_y = (min(left_eye_coords, key=lambda item: item[1]))[1]

    # croping the eyes from mask 
    cropped_right = eyes[r_min_y: r_max_y, r_min_x: r_max_x]
    cropped_left = eyes[l_min_y: l_max_y, l_min_x: l_max_x]

    # returning the cropped eyes 
    return cropped_right, cropped_left

# Eyes Postion Estimator 
def positionEstimator(cropped_eye):
    # getting height and width of eye 
    h, w =cropped_eye.shape
    
    # remove the noise from images
    gaussain_blur = cv2.GaussianBlur(cropped_eye, (9,9),0)
    median_blur = cv2.medianBlur(gaussain_blur, 3)

    # applying thrsholding to convert binary_image
    ret, threshed_eye = cv2.threshold(median_blur, 130, 255, cv2.THRESH_BINARY)

    # create fixd part for eye with 
    piece = int(w/3) 

    # slicing the eyes into three parts 
    right_piece = threshed_eye[0:h, 0:piece]
    center_piece = threshed_eye[0:h, piece: piece+piece]
    left_piece = threshed_eye[0:h, piece +piece:w]
    
    # calling pixel counter function
    eye_position, color = pixelCounter(right_piece, center_piece, left_piece)

    return eye_position, color 

# creating pixel counter function 
def pixelCounter(first_piece, second_piece, third_piece):
    # counting black pixel in each part 
    right_part = numpy.sum(first_piece==0)
    center_part = numpy.sum(second_piece==0)
    left_part = numpy.sum(third_piece==0)
    # creating list of these values
    eye_parts = [right_part, center_part, left_part]

    # getting the index of max values in the list 
    max_index = eye_parts.index(max(eye_parts))
    pos_eye ='' 
    if max_index==0:
        pos_eye="RIGHT"
        color=[utils.BLACK, utils.GREEN]
    elif max_index==1:
        pos_eye = 'CENTER'
        color = [utils.YELLOW, utils.PINK]
    elif max_index ==2:
        pos_eye = 'LEFT'
        color = [utils.GRAY, utils.YELLOW]
    else:
        pos_eye="Closed"
        color = [utils.GRAY, utils.YELLOW]
    return pos_eye, color

def saveFrame(filename, frame):
    cv2.imwrite(filename, frame)


def detectRisks(frame):
    elKaldirildiMi = False
    frame_counter =0
    (width, height) = (130, 100)
    with map_face_mesh.FaceMesh(min_detection_confidence =0.5, min_tracking_confidence=0.5) as face_mesh:
        # starting time here 
        start_time = time.time()
        # starting Video loop here.
        riskyFaceCounter = 1
        riskyEyesCounter = 1

        

        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            if(elKaldirildiMi == False):
                elKaldirildiMi = True
                print("[INFO] El Kaldırıldı")
            for hand_landmarks in results.multi_hand_landmarks:
                for index, lm in enumerate(hand_landmarks.landmark):
                    height, width, channel = frame.shape
                    cx, cy = int(lm.x * width), int(lm.y * height)
                    cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            if(elKaldirildiMi == True):
                elKaldirildiMi = False
                print("[INFO] El İndirildi")

        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        
        if faces != ():
            print("[INFO] Face Detected")
        else:
            saveFrame("RiskyMoments/Face/Frame" + str(riskyFaceCounter) + ".jpg", frame)
            riskyFaceCounter += 1
            #print("[INFO] Face Not Detected")
        

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (width, height))
            # Try to recognize the face
            prediction = model.predict(face_resize)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            if prediction[1]<500:
                cv2.putText(frame, '% s - %.0f' % (names[prediction[0]], prediction[1]), (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            else:
                cv2.putText(frame, 'not recognized', (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
        

        frame_counter +=1 # frame counter
        #  resizing frame
        frame = cv2.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        frame_height, frame_width= frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        results  = face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            mesh_coords = landmarksDetection(frame, results, False)
            
            
            cv2.polylines(frame,  [numpy.array([mesh_coords[p] for p in LEFT_EYE ], dtype=numpy.int32)], True, utils.GREEN, 1, cv2.LINE_AA)
            cv2.polylines(frame,  [numpy.array([mesh_coords[p] for p in RIGHT_EYE ], dtype=numpy.int32)], True, utils.GREEN, 1, cv2.LINE_AA)

            right_coords = [mesh_coords[p] for p in RIGHT_EYE]
            left_coords = [mesh_coords[p] for p in LEFT_EYE]
            crop_right, crop_left = eyesExtractor(frame, right_coords, left_coords)

            eye_position, color = positionEstimator(crop_right)
            utils.colorBackgroundText(frame, f'R: {eye_position}', FONTS, 1.0, (40, 220), 2, color[0], color[1], 8, 8)
            eye_position_left, color = positionEstimator(crop_left)
            utils.colorBackgroundText(frame, f'L: {eye_position_left}', FONTS, 1.0, (40, 320), 2, color[0], color[1], 8, 8)

            if eye_position != 'CENTER':
                #print(eye_position)
                saveFrame("RiskyMoments/Eyes/Frame" + str(riskyEyesCounter) + ".jpg", frame)
                riskyEyesCounter += 1
            
        
        # cv2.imwrite(f'img/frame_{frame_counter}.png', frame)
