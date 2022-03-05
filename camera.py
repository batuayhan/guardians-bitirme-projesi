import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import time
from PIL import Image, ImageTk
from threading import Thread, Lock

class Camera:

    def __init__(self,src=0,width=1280,height=720):
        self.vc=cv2.VideoCapture(src)
        self.vc.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.vc.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
        self.width = width
        self.height = height
        self.fps = 30
        self.copyDetected=True
        self.alertSliceSize=25
        self.vc.set(cv2.CAP_PROP_FPS, self.fps)
        (self.grabbed, self.frame) = self.vc.read()
        self.original_frame=self.frame
        self.started = False
        self.read_lock = Lock()
        print("Tanimlamalar yapildi.")

    def start(self):
        if not self.vc.isOpened():
            raise RuntimeError('Video kaynagi acilamadi.')
        if self.started :
            print("Zaten basladi!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

        return self

    def update(self) :
        with pyvirtualcam.Camera(self.width, self.height, self.fps, fmt=PixelFormat.BGR) as cam:
            print('Sanal kamera cihazi: ' + cam.device)
            while True:
                ret, self.frame = self.vc.read()
                self.read_lock.acquire()
                self.original_frame = self.frame.copy()
                self.read_lock.release()
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                if self.copyDetected == True:
                    self.frame[:self.alertSliceSize,::] =0
                    self.frame[:,:self.alertSliceSize,:] = 0
                    self.frame[-self.alertSliceSize:,:,:] = 0
                    self.frame[:,-self.alertSliceSize:,:] = 0
                    self.frame[:self.alertSliceSize,:,2] = round(time.time()*1000)%255
                    self.frame[:,:self.alertSliceSize,2] = round(time.time()*1000)%255
                    self.frame[-self.alertSliceSize:,:,2] = round(time.time()*1000)%255
                    self.frame[:,-self.alertSliceSize:,2] = round(time.time()*1000)%255
                cam.send(self.frame)

                time.sleep(.01)

    def show_frame(self):
        cv2.imshow('frame', self.original_frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.vc.release()
            cv2.destroyAllWindows()
            exit(1)

    def image_frame(self):
        image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        return image

if __name__ == '__main__':
    print("Sanal kamera baslatiliyor. Lutfen bekleyiniz.")
    video_stream_widget = Camera().start()
    while True:
        try:
            video_stream_widget.show_frame()
        except AttributeError:
            pass


        