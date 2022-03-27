import cv2
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import requests
import numpy as np
import imutils

def simCheck(image_name):
    camera = cv2.VideoCapture(0)
    while True:
        '''url = "http://192.168.1.20:8080/shot.jpg"
        img_resp = requests.get(url)
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        image = cv2.imdecode(img_arr, -1)
        image = imutils.resize(image, width=1000, height=1800)'''
        _, image = camera.read()
        cv2.imshow('ID Check', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            #camera.release()
            cv2.destroyAllWindows()
            break
        if cv2.waitKey(1) & 0xFF==ord('s'):
            cv2.imwrite(image_name,image)
            cv2.destroyAllWindows()
            break

    Tk().withdraw()
    filename = askopenfilename()
    image_one = cv2.imread(image_name)
    image_two = cv2.imread(filename)

    #Check if two images are equals
    if image_one.shape == image_two.shape:
        print("The images have same size and channels")
        difference = cv2.subtract(image_one, image_two)
        b, g, r = cv2.split(difference)

        if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
            print("The images are completely Equal")
        else:
            print("The images are NOT equal")

    #Check similarities between the 2 images
    sift = cv2.xfeatures2d.SIFT_create()
    kp_1, desc_1 = sift.detectAndCompute(image_one, None)
    kp_2, desc_2 = sift.detectAndCompute(image_two, None)

    index_params = dict(algorithm=0, trees=5)
    search_params = dict()
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(desc_1, desc_2, k=2)

    good_points = []
    for m, n in matches:
        if m.distance < 0.6*n.distance:
            good_points.append(m)

    # Define how similar they are
    number_keypoints = 0
    if len(kp_1) <= len(kp_2):
        number_keypoints = len(kp_1)
    else:
        number_keypoints = len(kp_2)

    print("Keypoints Image one: " + str(len(kp_1)))
    print("Keypoints Image two: " + str(len(kp_2)))
    print("Good Matches:", len(good_points))
    print("Match: ", len(good_points) / number_keypoints * 100, "/100")
    result = cv2.drawMatches(image_one, kp_1, image_two, kp_2, good_points, None)
    cv2.imshow("result", cv2.resize(result, None, fx=0.4, fy=0.4))
    cv2.imwrite("feature_matching.jpg", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
