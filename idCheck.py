import cv2
import easyocr

def read(path):
    reader = easyocr.Reader(['en'])
    return reader.readtext(path)

def idCheck():
    camera = cv2.VideoCapture(0)
    no = ""
    while True:
        _,image = camera.read()
        cv2.imshow('ID Check', image)
        if cv2.waitKey(1) & 0xFF==ord('s'):
            isOk = False
            cv2.imwrite('test.jpg',image)
            img = cv2.imread("test.jpg", cv2.IMREAD_GRAYSCALE)
            res = read('test.jpg')
            for r in res:
                print(r)
            for i in range(0,len(res)):
                if("Ogrenci No" in res[i]):
                    isOk = True
                    no = res[i+1][1]
                    break
            test = cv2.imread('test.jpg')
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

