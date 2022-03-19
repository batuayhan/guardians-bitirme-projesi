import tkinter as tk
from tkinter import ttk


class View(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        b = tk.Button(self, text="Login with Google", command=self.new_window)
        self.configure(bg="#e8e8e8")
        b.place(x=40,y=25,height=40)

    def new_window(self):
        window = tk.Toplevel(self)
        window.title("Guardians")
        window.geometry("510x420")
        window.configure(bg="#e8e8e8")

        buttonKimlik = ttk.Button(window, text="Kimlik Doğrulama")
        buttonKimlik.place(x=25, y=25, height=50)

        c = ttk.Checkbutton(window)
        c.place(x=175, y=40)

        buttonKagit = ttk.Button(window, text="Kağıt Kontrolü")
        buttonKagit.place(x=25, y=100, height=50, width=139)

        c2 = ttk.Checkbutton(window)
        c2.place(x=175, y=110)

        saatLabel = ttk.Label(window, text="Saat")
        saatLabel.place(x=300, y=25)

        saatEntry = ttk.Entry(window)
        saatEntry.insert(0, "Kalan Dakika: 45")
        saatEntry.config(state='disabled')
        saatEntry.place(x=300, y=50)

        kameraLabel = ttk.Label(window, text="Öğrenci Kamerası")
        kameraLabel.place(x=300, y=100)

        kameraEntry = ttk.Entry(window)
        kameraEntry.config(state='disabled')
        kameraEntry.place(x=300, y=125, height=175)

        submitButton = ttk.Button(window, text="Submit")
        submitButton.place(x=400, y=370, height=30)

if __name__ == "__main__":
    root = tk.Tk()
    view = View(root)
    root.title("Guardians")
    root.geometry("200x100")
    root.configure(bg="#e8e8e8")
    view.pack(side="top", fill="both", expand=True)
    root.mainloop()
