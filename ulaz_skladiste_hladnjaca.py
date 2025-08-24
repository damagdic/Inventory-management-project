from tkinter import *
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter.ttk import Combobox
import tkinter.ttk as ttk
from datetime import datetime
from repo_narudzba import fetch_kontakti, fetch_proizvodi, create_narudzba_s_stavkama
from repo_ulazi import fetch_ulazi_search

def ulaz_hladnjaca_form(window):
    ulaz_frame = Frame(window, bg='white', width=800, height=600)
    ulaz_frame.place(x=0, y=0)

    proizvod_options = ["Kuhani kukuruz šećerac", "Kuhana cikla", "Kuhana leća", "Kuhani slanutak"]

    titlelabel = Label(ulaz_frame, text="Ulaz robe Hladnjača", bg='blue', font=("times new roman", 24, "bold"), fg = "white")
    titlelabel.place(x=0,y=0,relwidth=1)

    back_button = Button(ulaz_frame, text="Natrag", bg='white', font=("times new roman", 15), fg = "black", command=lambda: ulaz_frame.destroy())
    back_button.place(x=10, y=10)

    left_frame = Frame(ulaz_frame, bg='white')
    left_frame.place(x=10, y=50, width=380, height=500)

    left_frame_title = Label(left_frame, text="Unos podataka", bg='white', font=("times new roman", 20), fg = "black")
    left_frame_title.grid(row=0, column=0, padx=10, pady=10)

   # Kontakt (kupac/dobavljač – ovisno o tvom značenju)
    Label(left_frame, text="Kontakt:", bg='white').grid(row=1, column=0, sticky='e', padx=10, pady=6)
    kontakti = fetch_kontakti()  # [{'idKontakt':1,'naziv':'Konzum'}, ...]
    kontakt_var = StringVar()
    kontakt_cb = Combobox(left_frame, textvariable=kontakt_var, state="readonly",
                          values=[f"{k['idKontakt']} - {k['naziv']}" for k in kontakti])
    kontakt_cb.grid(row=1, column=1, sticky='w', padx=10, pady=6)

    # Proizvod
    Label(left_frame, text="Proizvod:", bg='white').grid(row=2, column=0, sticky='e', padx=10, pady=6)
    proizvodi = fetch_proizvodi()  # [{'idProizvod':..,'naziv':..}]
    proizvod_var = StringVar()
    proizvod_cb = Combobox(left_frame, textvariable=proizvod_var, state="readonly",
                           values=[f"{p['idProizvod']} - {p['naziv']}" for p in proizvodi])
    proizvod_cb.grid(row=2, column=1, sticky='w', padx=10, pady=6)

    # Količina
    Label(left_frame, text="Količina:", bg='white').grid(row=3, column=0, sticky='e', padx=10, pady=6)
    kolicina_entry = Entry(left_frame); kolicina_entry.grid(row=3, column=1, sticky='w', padx=10, pady=6)

    # Datum primitka (u Narudzba)
    Label(left_frame, text="Datum primitka:", bg='white').grid(row=4, column=0, sticky='e', padx=10, pady=6)
    datum_primitka = DateEntry(left_frame, date_pattern='dd/mm/yyyy')
    datum_primitka.grid(row=4, column=1, sticky='w', padx=10, pady=6)

    # Datum narudžbe (obavezno u tvojoj shemi)
    Label(left_frame, text="Datum narudžbe:", bg='white').grid(row=5, column=0, sticky='e', padx=10, pady=6)
    datum_narudzbe = DateEntry(left_frame, date_pattern='dd/mm/yyyy')
    datum_narudzbe.grid(row=5, column=1, sticky='w', padx=10, pady=6)

    def on_unesi():
        try:
            print("[DEBUG] klik Unesi")
            # parse kontakt id
            if not kontakt_var.get():
                raise ValueError("Odaberi kontakt.")
            idKontakt = int(kontakt_var.get().split(" - ")[0])

            # parse proizvod id
            if not proizvod_var.get():
                raise ValueError("Odaberi proizvod.")
            idProizvod = int(proizvod_var.get().split(" - ")[0])

            # količina
            k_txt = kolicina_entry.get().strip()
            if not k_txt.isdigit() or int(k_txt) <= 0:
                raise ValueError("Količina mora biti pozitivan cijeli broj.")
            kolicina = int(k_txt)

            # datumi -> YYYY-MM-DD
            d_pr = datetime.strptime(datum_primitka.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            d_na = datetime.strptime(datum_narudzbe.get(), "%d/%m/%Y").strftime("%Y-%m-%d")

            # transakcijski insert: Narudzba + DetaljiNarudzbe (jedna stavka)
            idNar = create_narudzba_s_stavkama(
                idKontakt=idKontakt,
                datumNarudzbe=d_na,
                datumPrimitka=d_pr,
                stavke=[(idProizvod, kolicina)]
            )

            messagebox.showinfo("OK", f"Narudžba #{idNar} je spremljena.")
            load_ulazi()
            # reset polja
            kontakt_var.set(""); proizvod_var.set("")
            kolicina_entry.delete(0, END)

        except Exception as e:
            messagebox.showerror("Greška", str(e))

    unesi_button = Button(left_frame, text="Unesi", bg='white', font=("times new roman", 15), fg = "black", command=on_unesi)
    unesi_button.grid(row=6, column=0, columnspan=2, pady=10)

    right_frame = Frame(ulaz_frame, bg='white')
    right_frame.place(x=410, y=50, width=380, height=500)

    right_frame_title = Label(right_frame, text="Popis ulaza", bg='white', font=("times new roman", 20), fg = "black")
    right_frame_title.place(x=10, y=10)
    
    search_frame = Frame(right_frame, bg='white')
    search_frame.place(x=10, y=50, width=360, height=40)

    search_by = Combobox(search_frame, values=["Proizvod", "Godina ulaza", "Broj računa"], font=("times new roman", 10))
    search_by.set("Pretraži po")
    search_by.grid(row=0, column=0, padx=5, pady=10)

    search_entry = Entry(search_frame, font=("times new roman", 10))
    search_entry.grid(row=0, column=1, padx=5, pady=10)

    search_button = Button(search_frame, text="Pretraži", bg='white', font=("times new roman", 10), fg = "black", cursor="hand2")
    search_button.grid(row=0, column=2, padx=5, pady=10)

    tv_container = Frame(right_frame, bg='white')
    tv_container.place(x=10, y=100, width=360, height=390)


    ulazi_treeview = ttk.Treeview(tv_container, columns=("kontakt", "proizvod", "kolicina", "datum_primitka"), show='headings')
    ulazi_treeview.pack(side='left', fill='both', expand=True)
    vertical_scrollbar = Scrollbar(tv_container, orient=VERTICAL, command=ulazi_treeview.yview)
    vertical_scrollbar.pack(side=RIGHT, fill=Y)
    ulazi_treeview.configure(yscrollcommand=vertical_scrollbar.set)

    ulazi_treeview.heading("kontakt", text="Kontakt")
    ulazi_treeview.heading("proizvod", text="Proizvod")
    ulazi_treeview.heading("kolicina", text="Količina")
    ulazi_treeview.heading("datum_primitka", text="Datum primitka")

    ulazi_treeview.column("kontakt", width=85)
    ulazi_treeview.column("proizvod", width=85)
    ulazi_treeview.column("kolicina", width=85)
    ulazi_treeview.column("datum_primitka", width=85)

    def load_ulazi():
        rows = fetch_ulazi_search(limit=200)
        print("[DEBUG] redova:", len(rows))
        for r in rows[:5]:
            print("[DBG]", r)
        ulazi_treeview.delete(*ulazi_treeview.get_children())
        for r in rows:
            ulazi_treeview.insert(
                "", "end",
                values=( r["kontakt"], r["proizvod"],
                        r["kolicina"], r["datum_primitka"])
            )

    load_ulazi()