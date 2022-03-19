import tkinter as tk
from tkinter import ttk
import camera
from PIL import Image, ImageTk
from threading import Thread
from tkinter import messagebox
import sys

class View(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        b = tk.Button(self, text="Login with Google", command=self.new_window)
        self.configure(bg="#e8e8e8")
        b.place(x=40,y=25,height=40)
        self.window = tk.Toplevel(self)

    def new_window(self):
        self.window.title("Guardians")
        self.window.geometry("510x420")
        self.window.configure(bg="#e8e8e8")

        buttonKimlik = ttk.Button(self.window, text="Kimlik Doğrulama")
        buttonKimlik.place(x=25, y=25, height=50)

        c = ttk.Checkbutton(self.window)
        c.place(x=175, y=40)

        buttonKagit = ttk.Button(self.window, text="Kağıt Kontrolü")
        buttonKagit.place(x=25, y=100, height=50, width=139)

        c2 = ttk.Checkbutton(self.window)
        c2.place(x=175, y=110)

        saatLabel = ttk.Label(self.window, text="Saat")
        saatLabel.place(x=300, y=25)

        saatEntry = ttk.Entry(self.window)
        saatEntry.insert(0, "Kalan Dakika: 45")
        saatEntry.config(state='disabled')
        saatEntry.place(x=300, y=50)

        t2 = Thread(target=self.show_cam, args=(200,150))
        t2.daemon = True
        t2.start()
        t3 = Thread(target=studentCam.record_video, args=())
        t3.daemon=True
        t3.start()
        submitButton = ttk.Button(self.window, text="Finish",command = on_closing)
        submitButton.place(x=400, y=370, height=30)

    def show_cam(self,x,y):
        while True:
            if finished:
                break
            imageframe = studentCam.image_frame(x,y)
            if finished:
                break
            imageframe = ImageTk.PhotoImage(image=imageframe)
            if finished:
                break
            kameraLabel = ttk.Label(self.window, image=imageframe)
            if finished:
                break
            kameraLabel.image = imageframe
            if finished:
                break
            kameraLabel.place(x=300,y=150)

global studentCam
global finished
def start_camera():
        global studentCam
        studentCam = camera.start_camera()

def on_closing():
    if messagebox.askokcancel("Finish", "Make you sure whether sent your exam papers. Are you sure?"):
        global studentCam
        global finished
        finished=True
        studentCam.stop_camera() #stop recording

        
if __name__ == "__main__":
    start_camera()
    finished = False
    root = tk.Tk()
    view = View(root)
    root.title("Guardians")
    root.geometry("200x100")
    root.configure(bg="#e8e8e8")
    view.pack(side="top", fill="both", expand=True)
    root.mainloop()
