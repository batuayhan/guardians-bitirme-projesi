from faulthandler import disable
import time
import tkinter as tk
from tkinter import PhotoImage, StringVar, ttk
from tracemalloc import start
import camera
from PIL import Image, ImageTk
from threading import Thread
from tkinter import messagebox
import sys
import firebase_admin
from firebase_admin import credentials
from google.cloud import storage
import os
import RiskDetector
import datetime
import ntplib
from time import ctime
import examguardTelegramBot
from tkinter import *
from PIL import ImageTk, Image



ntpClient = ntplib.NTPClient()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./serviceAccountKey.json"
cred = credentials.Certificate("./serviceAccountKey.json")
firebase = firebase_admin.initialize_app(cred)
client = storage.Client()
bucket = client.get_bucket('exam-guard.appspot.com')
courseName = "BIL421"
examName = "exam1"
'''
enter exam time as seconds !!
'''
examTime = 10
studentId = "161101024"
directoryNames = ["examPapersByExamGuard","examPapersByPhone","examVideo","idCheck"]
blob = bucket.blob(courseName+'/'+examName+'/'+studentId+'/'+directoryNames[2]+'/ogrenciKayit'+studentId+'.mp4')
#blob.content_type = "video/webm"
#of = open("deneme.jpg", 'rb')
#blob.upload_from_file(of)

startTime = -1
endTime = -1
riskyMomentsTimeStamps = []
saatLabel = None


def getCurrentTime():
    try:
        request = ntpClient.request('europe.pool.ntp.org', version=3)
        return int(request.orig_time)
    except:
        return int(time.time())

def groupRiskyMoments(lst):
    if lst != []:
        res = [[lst[0]]]
        for i in range(1, len(lst)):
            if lst[i-1]+1 == lst[i]:
                res[-1].append(lst[i])
            else:
                res.append([lst[i]])
        return res


class View(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        b = tk.Button(self, text="Login with Google", command=self.new_window)
        self.configure(bg="#e8e8e8")
        b.place(x=35,y=30,height=40,width=130)
        self.window = tk.Toplevel(self)
        self.window.withdraw()
        
        

    def new_window(self):
        root.withdraw()
        self.window.deiconify()
        global startTime
        startTime = getCurrentTime()
        self.window.title("Guardians")
        self.window.geometry("510x420")
        self.window.iconbitmap('images/logo2.ico')
        x_Left = int(self.window.winfo_screenwidth()/2 - 255)
        y_Top = int(self.window.winfo_screenheight()/2 - 210)
        self.window.geometry("+{}+{}".format(x_Left, y_Top))
        self.window.configure(bg="#e8e8e8")     

        buttonKimlik = ttk.Button(self.window, text="Kimlik Doğrulama")
        buttonKimlik.place(x=25, y=25, height=50)

        c = ttk.Checkbutton(self.window)
        c.place(x=175, y=40)

        kimlikLabel = ttk.Label(self.window, text="Kameraya kimliğinizi gösterdiğiniz sırada butona basınız.")
        kimlikLabel.place(x=25,y=75)

        buttonKagit = ttk.Button(self.window, text="Kağıt Kontrolü")
        buttonKagit.place(x=25, y=100, height=50, width=139)

        c2 = ttk.Checkbutton(self.window)
        c2.place(x=175, y=110)

        kagitLabel = ttk.Label(self.window, text="Kameraya kağıdınızı gösterdiğiniz sırada")
        kagitLabel.place(x=25,y=150)
        kagitLabel2 = ttk.Label(self.window, text="butona basınız.")
        kagitLabel2.place(x=25, y=175)

        buttonKagit2 = ttk.Button(self.window, text="Sınav sonrası Kağıt Gösterimi")
        buttonKagit2.place(x=25,y=200, height=50)

        c3 = ttk.Checkbutton(self.window)
        c3.place(x=250, y=215)

        kagitLabel = ttk.Label(self.window, text="Sınavınızı bitirdikten sonra kağıdınızı")
        kagitLabel.place(x=25,y=150)
        kagitLabel2 = ttk.Label(self.window, text="gösterdiğiniz sırada butona basınız.")
        kagitLabel2.place(x=25, y=175)

        global saatLabel
        saatLabel = ttk.Label(self.window, text="Kalan Sınav Süresi: ")
        saatLabel.place(x=300, y=25)



        t2 = Thread(target=self.show_cam, args=(200,150))
        t2.daemon = True
        t2.start()
        t3 = Thread(target=studentCam.record_video, args=())
        t3.daemon=True
        t3.start()

        t4 = Thread(target=self.detectRisk, args=(200,150))
        t4.daemon = True
        t4.start()

        t5 = Thread(target=self.updateTime, args=())
        t5.daemon = True
        t5.start()

    

        submitButton = ttk.Button(self.window, text="Finish",command = on_closing)
        submitButton.place(x=400, y=370, height=30)
    
    def updateTime(self):
        while True:
            timeLeft = examTime-getCurrentTime()+startTime
            if timeLeft >= 0 :
                saatLabel.configure(text="Kalan Sınav Süresi: "+str(datetime.timedelta(seconds = timeLeft)))
                time.sleep(1)
            else:
                studentCam.isTimeOver = True 
      

    def detectRisk(self, x, y):
        while True:
            riskyMomentFlag = False
            imageframe = studentCam.image_frame(x,y)
            ret = studentCam.grabbed
            frame = studentCam.frame
            detectionData = RiskDetector.detectRisks(frame)
            if detectionData[0] == 1:
                studentCam.handDetected = True
                examguardTelegramBot.sendMessage(str(studentId) + " numaralı öğrenci elini kaldırdı.")
            else:
                studentCam.handDetected = False
                riskyMomentFlag = False
            if detectionData[1] == 1:
                studentCam.copyDetected = True,
                if riskyMomentFlag == False and getCurrentTime() not in riskyMomentsTimeStamps :
                    riskyMomentsTimeStamps.append(getCurrentTime())
                    riskyMomentFlag = True
                
            else:
                studentCam.copyDetected = False
        

    def show_cam(self,x,y):
        print('goruntu yerlestirildi.')
        imageframe = studentCam.image_frame(x,y)
        imageframe = ImageTk.PhotoImage(image=imageframe)
        kameraLabel = ttk.Label(self.window, image=imageframe)
        kameraLabel.image = imageframe
        kameraLabel.place(x=300,y=150)
        while True:
            if finished:
                break
            imageframe = studentCam.image_frame(x,y)
            if finished:
                break
            imageframe = ImageTk.PhotoImage(image=imageframe)
            if finished:
                break
            kameraLabel.configure(image=imageframe)
            kameraLabel.image = imageframe
            kameraLabel.place(x=300,y=150)

global studentCam
global finished
def start_camera():
        global studentCam
        studentCam = camera.start_camera()

def on_closing():
    if messagebox.askokcancel("Finish", "Make you sure whether sent your exam papers. Are you sure?"):
        endTime = getCurrentTime()
        print("exam time: ",endTime-startTime)
        print("risky moments: ",(riskyMomentsTimeStamps))
        print("risky moments: ", groupRiskyMoments(riskyMomentsTimeStamps))
        global studentCam
        global finished
        finished=True
        studentCam.stop_camera() #stop recording
        print("video sisteme yükleniyor")
        blob.upload_from_filename("ogrenciKayit.mp4")
        print("video sisteme yüklendi")
        studentCam.finish()
        print("program kapatildi")
        

        
if __name__ == "__main__":
    start_camera()
    finished = False
    root = tk.Tk()
    view = View(root)
    root.title("Guardians")
    root.geometry("200x100")
    root.configure(bg="#e8e8e8")
    root.iconbitmap('images/logo2.ico')
    x_Left = int(root.winfo_screenwidth()/2 - 100)
    y_Top = int(root.winfo_screenheight()/2 - 50)
    root.geometry("+{}+{}".format(x_Left, y_Top))
    view.pack(side="top", fill="both", expand=True)
    root.mainloop()
