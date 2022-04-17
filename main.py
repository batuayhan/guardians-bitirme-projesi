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
from auth import Auth
import paperControl
import cv2
import idCheck
import simCheck
from tkinter.filedialog import askopenfilename


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
examTime = 2700
studentId = "161101024"
directoryNames = ["lastPaperCheck","examVideo","idCheck","firstPaperCheck"]
blob = bucket.blob(courseName+'/'+examName+'/'+studentId+'/'+directoryNames[1]+'/ogrenciKayit'+studentId+'.mp4')
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
        b = tk.Button(self, text="Login with Google", command=self.login)
        self.configure(bg="#e8e8e8")
        b.place(x=40,y=25,height=40)
        self.window = tk.Toplevel(self)
        self.window.withdraw()
        
    def login(self):
        #auth = Auth()
        self.new_window()

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

        buttonKimlik = ttk.Button(self.window, text="Kimlik Doğrulama", command=id_control)
        buttonKimlik.place(x=25, y=25, height=50, width=155)
        c = ttk.Checkbutton(self.window)
        c.place(x=185, y=40)
        kimlikLabel = ttk.Label(self.window, text="Kameraya kimliğinizi gösterdiğiniz sırada butona basınız.")
        kimlikLabel.place(x=25,y=75)

        buttonKagit = ttk.Button(self.window, text="Sınav Önü Kağıt Kontrolü", command=paper_control)
        buttonKagit.place(x=25, y=100, height=50, width=155)
        c2 = ttk.Checkbutton(self.window)
        c2.place(x=185, y=110)
        kagitLabel = ttk.Label(self.window, text="Kameraya boş kağıdınızı gösterdiğiniz sırada")
        kagitLabel.place(x=25,y=150)
        kagitLabel2 = ttk.Label(self.window, text="butona basınız.")
        kagitLabel2.place(x=25, y=175)

        buttonKagit2 = ttk.Button(self.window, text="Sınav Sonu Kağıt Gösterme", command=last_paper_control)
        buttonKagit2.place(x=25,y=200, height=50, width=155)
        c3 = ttk.Checkbutton(self.window)
        c3.place(x=185, y=215)
        kagitLabel3 = ttk.Label(self.window, text="Sınavınızı bitirdikten sonra kağıdınızı")
        kagitLabel3.place(x=25,y=250)
        kagitLabel4 = ttk.Label(self.window, text="gösterdiğiniz sırada butona basınız.")
        kagitLabel4.place(x=25, y=275)

        buttonKagit3 = ttk.Button(self.window, text="Kağıt Fotoğrafı Yükleme", command=paper_submit)
        buttonKagit3.place(x=25,y=300, height=50, width=155)
        c4 = ttk.Checkbutton(self.window)
        c4.place(x=185, y=315)
        kagitLabel5 = ttk.Label(self.window, text="Sınavınızı bitirdikten sonra kağıdınızın")
        kagitLabel5.place(x=25,y=350)
        kagitLabel6 = ttk.Label(self.window, text="fotoğrafını yükleyiniz.")
        kagitLabel6.place(x=25, y=375)
        
        global saatLabel
        saatLabel = ttk.Label(self.window, text="Kalan Sınav Süresi: ")
        saatLabel.place(x=300, y=25)
        saatLabel.config(font=("Helvetica", 12))



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
                studentCam.copyDetected = True
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
        
def paper_control():
    image_name = "firstpaper.jpg"
    frame = studentCam.original_frame
    cv2.imwrite(image_name, frame)
    result = paperControl.paperControl(image_name)
    if result:
        res = "Kağıt boş"
        f = open(res, "w")
    else:
        res = "Kağıt boş değil"
        f= open(res, "w")
    f.close()
    b1 = bucket.blob(courseName + '/' + examName + '/' + studentId + '/' + directoryNames[3] + '/firstpaper_' + studentId + '.jpg')
    b2 = bucket.blob(courseName + '/' + examName + '/' + studentId + '/' + directoryNames[3] + '/firstpapercontrol_' + studentId + '.jpg')
    b3 = bucket.blob(courseName + '/' + examName + '/' + studentId + '/' + directoryNames[3] + '/'+res + '_' + studentId)
    b1.upload_from_filename(image_name)
    b2.upload_from_filename("firstpapercontrol.jpg")
    b3.upload_from_filename(res)
    os.remove(image_name)
    os.remove("firstpapercontrol.jpg")
    os.remove(res)

def id_control():
    image_name = "id.jpg"
    frame = studentCam.original_frame
    cv2.imwrite(image_name, frame)
    result = idCheck.idCheck(image_name, studentId)
    if result:
        res = "Kontrol başarılı"
        f = open(res, "w")
    else:
        res = "Kontrol Başarısız"
        f = open(res, 'w')
    f.close()
    b1 = bucket.blob(courseName + '/' + examName + '/' + studentId + '/' + directoryNames[2] + '/id_' + studentId + '.jpg')
    b2 = bucket.blob(courseName + '/' + examName + '/' + studentId + '/' + directoryNames[2] + '/' + res + '_' + studentId)
    b1.upload_from_filename(image_name)
    b2.upload_from_filename(res)
    os.remove(image_name)
    os.remove(res)

def last_paper_control():
    image_name = "lastpaper.jpg"
    frame = studentCam.original_frame
    cv2.imwrite(image_name, frame)

def paper_submit():
    filename = askopenfilename()
    result = simCheck.simCheck("lastpaper.jpg", filename)
    f = open(result, "w")
    f.close()
    b1 = bucket.blob(courseName + '/' + examName + '/' + studentId + '/' + directoryNames[0] + '/lastpaper_' + studentId + '.jpg')
    b2 = bucket.blob(courseName + '/' + examName + '/' + studentId + '/' + directoryNames[0] + '/dosya_' + studentId + '.jpg')
    b3 = bucket.blob(courseName + '/' + examName + '/' + studentId + '/' + directoryNames[0] + '/'+result + '_' + studentId)
    b1.upload_from_filename("lastpaper.jpg")
    b2.upload_from_filename(filename)
    b3.upload_from_filename(result)
    os.remove("lastpaper.jpg")
    os.remove(result)
        
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
