import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import time

vc = cv2.VideoCapture(0)

if not vc.isOpened():
    raise RuntimeError('Video kaynagi acilamadi.')

pref_width = 1280
pref_height = 720
pref_fps = 30
vc.set(cv2.CAP_PROP_FRAME_WIDTH, pref_width)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, pref_height)
vc.set(cv2.CAP_PROP_FPS, pref_fps)

width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = vc.get(cv2.CAP_PROP_FPS)
copyDetected=True
alertSliceSize=25
with pyvirtualcam.Camera(width, height, fps, fmt=PixelFormat.BGR) as cam:
    print('Sanal kamera cihazi: ' + cam.device)
    while True:
        ret, frame = vc.read()
        cv2.imshow('frame', frame)
        #cv2.imshow('frame',frame)
        if copyDetected == True:
            frame[:alertSliceSize,::] =0
            frame[:,:alertSliceSize,:] = 0
            frame[-alertSliceSize:,:,:] = 0
            frame[:,-alertSliceSize:,:] = 0
            frame[:alertSliceSize,:,2] = round(time.time()*1000)%255
            frame[:,:alertSliceSize,2] = round(time.time()*1000)%255
            frame[-alertSliceSize:,:,2] = round(time.time()*1000)%255
            frame[:,-alertSliceSize:,2] = round(time.time()*1000)%255

        cam.send(frame)
cv2.destroyAllWindows()
        