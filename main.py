import tkinter as tk
from tkinter import *
from tkinter import ttk

window = tk.Tk()
window.title("Guardians")
window.geometry("200x100")
window.configure(bg="#e8e8e8")

s = ttk.Style(window)
s.theme_use('aqua')


def openNewWindow():
    newWindow = Toplevel(window)
    newWindow.title("Guardians")
    newWindow.geometry("510x420")
    newWindow.configure(bg="#e8e8e8")
    newWindow.columnconfigure(0, weight=1)
    newWindow.columnconfigure(1, weight=1)
    newWindow.columnconfigure(2, weight=3)

    buttonKimlik = ttk.Button(newWindow, text="Kimlik Doğrulama")
    buttonKimlik.grid(column=0, row=0, sticky=W, padx=5, pady=5)

    c = ttk.Checkbutton(newWindow)
    c.grid(column=1, row=0,sticky=W)

    buttonKagit = ttk.Button(newWindow, text="Kağıt Kontrolü")
    buttonKagit.grid(column=0, row=2, sticky=W, padx=5, pady=5)

    c2 = ttk.Checkbutton(newWindow)
    c2.grid(column=1,row=2,sticky=W)

    saatLabel = ttk.Label(newWindow, text="Saat")
    saatLabel.grid(column=1,row=0,sticky=E,padx=160)

    saatEntry = ttk.Entry(newWindow)
    saatEntry.insert(0,"Kalan Dakika: 45")
    saatEntry.grid(column=1,row=1,sticky=E,padx=5)

    kameraLabel = ttk.Label(newWindow, text="Öğrenci Kamerası")
    kameraLabel.grid(column=1, row=2,sticky=E,padx=80,pady=5)

    kameraEntry = ttk.Entry(newWindow)
    kameraEntry.grid(column=1, row=3, padx=5,pady=5,ipady=100,sticky=E)

    submitButton = ttk.Button(newWindow, text="Submit")
    submitButton.grid(column=1,row=6,padx=5,pady=30,sticky=E)


button = ttk.Button(window, text='Click to login with Google',

                          command=openNewWindow)
button.grid(column=0, row=2)

window.mainloop()
