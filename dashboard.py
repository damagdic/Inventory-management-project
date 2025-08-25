from tkinter import *
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter.ttk import Combobox
import tkinter.ttk as ttk
from ulaz_skladiste_hladnjaca import ulaz_hladnjaca_form
from izlaz_skladiste_hladnjaca import izlaz_hladnjaca_form

#funcionality part

def skladiste_hladnjaca():
    hladnjaca_frame = Frame(window, bg='white', width=800, height=600)
    hladnjaca_frame.place(x=0, y=0)

    titlelabel = Label(hladnjaca_frame, text="Skladište Hladnjača", bg='blue', font=("times new roman", 24, "bold"), fg = "white")
    titlelabel.place(x=0,y=0,relwidth=1)

    back_button = Button(hladnjaca_frame, text="Natrag", bg='white', font=("times new roman", 15), fg = "black", command=lambda: hladnjaca_frame.destroy())
    back_button.place(x=10, y=10)

    midFrame = Frame(hladnjaca_frame, bg='white')
    midFrame.place(x=200, y=200, width=400, height=520)

    ulaz_button = Button(midFrame, text="Ulaz robe", bg='white', font=("times new roman", 15), fg = "black", command=lambda : ulaz_hladnjaca_form(window))
    ulaz_button.pack(fill=X)

    izlaz_button = Button(midFrame, text="Izlaz robe", bg='white', font=("times new roman", 15), fg = "black", command=lambda: izlaz_hladnjaca_form(window))
    izlaz_button.pack(fill=X)

    provjeri_stanje_button = Button(midFrame, text="Provjeri Stanje", bg='white', font=("times new roman", 15), fg = "black")
    provjeri_stanje_button.pack(fill=X)

    statistika_button = Button(midFrame, text="Statistika", bg='white', font=("times new roman", 15), fg = "black")
    statistika_button.pack(fill=X)


def skladiste_pogon():
    pogon_frame = Frame(window, bg='white', width=800, height=600)
    pogon_frame.place(x=0, y=0)

    titlelabel = Label(pogon_frame, text="Skladište Pogon", bg='blue', font=("times new roman", 24, "bold"), fg = "white")
    titlelabel.place(x=0,y=0,relwidth=1)

    back_button = Button(pogon_frame, text="Natrag", bg='white', font=("times new roman", 15), fg = "black", command=lambda: pogon_frame.destroy())
    back_button.place(x=10, y=10)

    midFrame = Frame(pogon_frame, bg='white')
    midFrame.place(x=200, y=200, width=400, height=520)

    ulaz_button = Button(midFrame, text="Ulaz robe", bg='white', font=("times new roman", 15), fg = "black", command=ulaz_pogon_form)
    ulaz_button.pack(fill=X)

    izlaz_button = Button(midFrame, text="Izlaz robe", bg='white', font=("times new roman", 15), fg = "black")
    izlaz_button.pack(fill=X)

    provjeri_stanje_button = Button(midFrame, text="Provjeri Stanje", bg='white', font=("times new roman", 15), fg = "black")
    provjeri_stanje_button.pack(fill=X)

    statistika_button = Button(midFrame, text="Statistika", bg='white', font=("times new roman", 15), fg = "black")
    statistika_button.pack(fill=X)

def ulaz_pogon_form():
    ulaz_frame = Frame(window, bg='white', width=800, height=600)
    ulaz_frame.place(x=0, y=0)

    titlelabel = Label(ulaz_frame, text="Ulaz robe Pogon", bg='blue', font=("times new roman", 24, "bold"), fg = "white")
    titlelabel.place(x=0,y=0,relwidth=1)

    back_button = Button(ulaz_frame, text="Natrag", bg='white', font=("times new roman", 15), fg = "black", command=lambda: ulaz_frame.destroy())
    back_button.place(x=10, y=10)

def on_exit():
    if messagebox.askokcancel("Izlaz", "Želite li stvarno izaći?"):
        window.quit()

#gui part

window = Tk()
window.title("Dashboard")
window.geometry("800x600")
window.resizable(False, False)

window.config(bg='white')

titlelabel = Label(window, text="Kontrola ulaza i izlaza", bg='blue', font=("times new roman", 24, "bold"), fg = "white")
titlelabel.place(x=0,y=0,relwidth=1)

subtitlelabel = Label(window, text="Dobrodošli u sustav kontrole ulaza i izlaza Madig d.o.o\tDatum: 01.01.2023.\t Vrijeme: 12:00", bg='white', font=("times new roman", 9), fg = "black")
subtitlelabel.place(x=0,y=50, relwidth=1)

midFrame = Frame(window, bg='white')
midFrame.place(x=200, y=200, width=400, height=520)

menuLabel = Label(midFrame, text="Izbornik", bg='white', font=("times new roman", 15, "bold"), fg = "black")
menuLabel.pack(pady=10)

skladiste_hladnjaca_button = Button(midFrame, text="Skladište Hladnjaca", bg='white', font=("times new roman", 15), fg = "black", command=skladiste_hladnjaca)  
skladiste_hladnjaca_button.pack(fill=X)

skladiste_pogon_button = Button(midFrame, text="Skladište Pogon", bg='white', font=("times new roman", 15), fg = "black", command=skladiste_pogon)
skladiste_pogon_button.pack(fill=X)

exit_button = Button(midFrame, text="Izlaz", bg='white', font=("times new roman", 15), fg = "black")
exit_button.pack(fill=X)

exit_button.config(command=on_exit)


window.mainloop()