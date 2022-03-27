import cv2
import easyocr
import requests
import numpy as np
import imutils

def read(path):
    reader = easyocr.Reader(['en'])
    return reader.readtext(path)

def idCheck(image_name):
    camera = cv2.VideoCapture(0)
    no = ""
    while True:
        #url = "http://192.168.1.20:8080/shot.jpg"
        #img_resp = requests.get(url)
        #img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        #image = cv2.imdecode(img_arr, -1)
        #image = imutils.resize(image, width=1000, height=1800)
        _, image = camera.read()
        cv2.imshow('ID Check', image)
        if cv2.waitKey(1) & 0xFF==ord('s'):
            isOk = False
            cv2.imwrite(image_name,image)
            img = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
            res = read(image_name)
            #for r in res:
                #print(r)
            for i in range(0,len(res)):
                if("Ogrenci No" in res[i]):
                    isOk = True
                    no = res[i+1][1]
                    break
            test = cv2.imread(image_name)
            if isOk == False:
                str = "Invalid ID"
                testt = cv2.putText(test, str, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                cv2.imshow('Result', testt)
            else:
                str = "Welcome, " + no
                testt = cv2.putText(test, str, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                cv2.imshow('Result', testt)
    camera.release()
    cv2.destroyAllWindows()
idCheck("idtest.jpg")
