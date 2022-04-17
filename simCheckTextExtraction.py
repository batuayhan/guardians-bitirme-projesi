import cv2
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import easyocr
import requests
import numpy as np
import imutils
import difflib

def similarity(str1, str2):
    str1 = str1.lower()
    str2 = str2.lower()
    return difflib.SequenceMatcher(str1, str2).ratio()

def read(path):
    reader = easyocr.Reader(['en'])
    return reader.readtext(path)

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
            res = read("simtest.jpg")
            for r in res:
                print(r)

    Tk().withdraw()
    filename = askopenfilename()
    res_file = read(filename)
    for r in res_file:
        print(r)

    if len(res_file) < len(res):
        for i in range(len(res_file)):
            pass
