from tkinter import *
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter.ttk import Combobox
import tkinter.ttk as ttk
from datetime import datetime
from repo_narudzba import fetch_kontakti, fetch_proizvodi, create_narudzba_s_stavkama, update_narudzba_i_detalj
from repo_ulazi import fetch_ulazi_search

def ulaz_hladnjaca_form(window):
    ulaz_frame = Frame(window, bg='white', width=800, height=600)
    ulaz_frame.place(x=0, y=0)

    titlelabel = Label(ulaz_frame, text="Ulaz robe Hladnjača", bg='blue', font=("times new roman", 24, "bold"), fg = "white")
    titlelabel.place(x=0,y=0,relwidth=1)

    back_button = Button(ulaz_frame, text="Natrag", bg='white', font=("times new roman", 15), fg = "black", command=lambda: ulaz_frame.destroy())
    back_button.place(x=10, y=10)

    left_frame = Frame(ulaz_frame, bg='white')
    left_frame.place(x=10, y=50, width=380, height=500)

    left_frame_title = Label(left_frame, text="Unos podataka", bg='white', font=("times new roman", 20), fg = "black")
    left_frame_title.grid(row=0, column=0, padx=10, pady=10)

    Label(left_frame, text="Kontakt:", bg='white').grid(row=1, column=0, sticky='e', padx=10, pady=6)
    kontakti = fetch_kontakti()
    kontakt_options = [k["naziv"] for k in kontakti]
    kontakt_id_by_name = {k["naziv"]: k["idKontakt"] for k in kontakti}
    kontakt_var = StringVar()
    kontakt_cb = Combobox(left_frame, textvariable=kontakt_var, state="readonly",
                        values=kontakt_options)
    kontakt_cb.grid(row=1, column=1, sticky='w', padx=10, pady=6)

    # Proizvodi
    Label(left_frame, text="Proizvod:", bg='white').grid(row=2, column=0, sticky='e', padx=10, pady=6)
    proizvodi = fetch_proizvodi()
    proizvod_options = [p["naziv"] for p in proizvodi]
    proizvod_id_by_name = {p["naziv"]: p["idProizvod"] for p in proizvodi}
    proizvod_var = StringVar()
    proizvod_cb = Combobox(left_frame, textvariable=proizvod_var, state="readonly",
                        values=proizvod_options)
    proizvod_cb.grid(row=2, column=1, sticky='w', padx=10, pady=6)
        # Količina
    Label(left_frame, text="Količina:", bg='white').grid(row=3, column=0, sticky='e', padx=10, pady=6)
    kolicina_entry = Entry(left_frame); kolicina_entry.grid(row=3, column=1, sticky='w', padx=10, pady=6)

    # Datum primitka (u Narudzba)
    Label(left_frame, text="Datum primitka:", bg='white').grid(row=4, column=0, sticky='e', padx=10, pady=6)
    datum_primitka = DateEntry(left_frame, date_pattern='dd/mm/yyyy')
    datum_primitka.grid(row=4, column=1, sticky='w', padx=10, pady=6)

    # Datum narudžbe 
    Label(left_frame, text="Datum narudžbe:", bg='white').grid(row=5, column=0, sticky='e', padx=10, pady=6)
    datum_narudzbe = DateEntry(left_frame, date_pattern='dd/mm/yyyy')
    datum_narudzbe.grid(row=5, column=1, sticky='w', padx=10, pady=6)

    def on_unesi():
        try:
            # parse kontakt id
            if not kontakt_var.get():
                raise ValueError("Odaberi kontakt.")
            idKontakt = kontakt_id_by_name.get(kontakt_cb.get())

            # parse proizvod id
            if not proizvod_var.get():
                raise ValueError("Odaberi proizvod.")
            idProizvod = proizvod_id_by_name.get(proizvod_cb.get())

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

    search_by = Combobox(
        search_frame,
        values=["Proizvod", "Kontakt", "Godina ulaza"],
        font=("times new roman", 10), state="readonly", width=14
    )
    search_by.set("Proizvod")
    search_by.grid(row=0, column=0, padx=5, pady=10)

    search_entry = Entry(search_frame, font=("times new roman", 10), width=20)
    search_entry.grid(row=0, column=1, padx=5, pady=10)

    def do_search():
        sb = search_by.get()
        term = search_entry.get().strip()
        if sb in ("Godina ulaza") and term and not term.isdigit():
            messagebox.showwarning("Upozorenje", "Unesi broj (npr. 2025).")
            return
        load_ulazi(sb, term)

    search_button = Button(search_frame, text="Pretraži", bg='white', font=("times new roman", 10), fg = "black", cursor="hand2", command=do_search )
    search_button.grid(row=0, column=2, padx=5, pady=10)

    search_entry.bind("<Return>", lambda e: do_search())

    tv_container = Frame(right_frame, bg='white')
    tv_container.place(x=10, y=100, width=360, height=350)

    update_button = Button(right_frame, text="Ažuriraj", bg='white', font=("times new roman", 10), fg="black", cursor="hand2")
    update_button.place(x = 10, y = 460)

    cols = ("row_id","idNarudzba","idKontakt","idProizvod",
        "kontakt","proizvod","kolicina","datum_primitka")

    ulazi_treeview = ttk.Treeview(tv_container, columns=cols, show='headings')
    ulazi_treeview.pack(side='left', fill='both', expand=True)
    vertical_scrollbar = Scrollbar(tv_container, orient=VERTICAL, command=ulazi_treeview.yview)
    vertical_scrollbar.pack(side=RIGHT, fill=Y)
    ulazi_treeview.configure(yscrollcommand=vertical_scrollbar.set)

    for hidden in ("row_id","idNarudzba","idKontakt","idProizvod"):
        ulazi_treeview.heading(hidden, text=hidden)
        ulazi_treeview.column(hidden, width=1, stretch=False, anchor='w')

    ulazi_treeview.heading("kontakt", text="Kontakt")
    ulazi_treeview.heading("proizvod", text="Proizvod")
    ulazi_treeview.heading("kolicina", text="Količina")
    ulazi_treeview.heading("datum_primitka", text="Datum primitka")

    ulazi_treeview.column("kontakt", width=85)
    ulazi_treeview.column("proizvod", width=85)
    ulazi_treeview.column("kolicina", width=85)
    ulazi_treeview.column("datum_primitka", width=85)

    def load_ulazi(sb: str | None = None, term: str | None = None):
        rows = fetch_ulazi_search(search_by=sb, term=term, limit=200)
        ulazi_treeview.delete(*ulazi_treeview.get_children())
        for r in rows:
            ulazi_treeview.insert(
                "", "end",
                 values=(r["row_id"], r["idNarudzba"], r["idKontakt"], r["idProizvod"],
                    r["kontakt"], r["proizvod"], r["kolicina"], r["datum_primitka"])
            )

    load_ulazi()

    def select_data(event=None):
        sel = ulazi_treeview.selection()
        if not sel:
            return
        vals = ulazi_treeview.item(sel[0], "values")
        # redoslijed: row_id, idNarudzba, idKontakt, idProizvod, kontakt, proizvod, kolicina, dat_pr
        _, _, _, _, kontakt, proizvod, kolicina, dat_pr = vals

        kontakt_cb.set(kontakt)     
        proizvod_cb.set(proizvod)
        kolicina_entry.delete(0, END)
        kolicina_entry.insert(0, kolicina)
        try:
            datum_primitka.set_date(datetime.strptime(dat_pr, "%d.%m.%Y").date())
        except: pass

    ulazi_treeview.bind("<<TreeviewSelect>>", select_data)
    

    def on_update():
        sel = ulazi_treeview.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberi red za ažuriranje.")
            return
        vals = ulazi_treeview.item(sel[0], "values")
        row_id, idNarudzba, _, _, _, _, _, _= vals  

        try:
            name_k = kontakt_cb.get().strip()
            name_p = proizvod_cb.get().strip()
            if not name_k or not name_p:
                raise ValueError("Odaberi kontakt i proizvod.")

            new_idKontakt  = kontakt_id_by_name.get(name_k)
            new_idProizvod = proizvod_id_by_name.get(name_p)
            if new_idKontakt is None or new_idProizvod is None:
                raise ValueError("Nepoznat kontakt/proizvod.")

            k_txt = kolicina_entry.get().strip()
            if not k_txt.isdigit() or int(k_txt) <= 0:
                raise ValueError("Količina mora biti pozitivan cijeli broj.")
            new_kolicina = int(k_txt)

            d_pr = datetime.strptime(datum_primitka.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            d_na = datetime.strptime(datum_narudzbe.get(), "%d/%m/%Y").strftime("%Y-%m-%d")

            update_narudzba_i_detalj(
                row_id=int(row_id),
                idNarudzba=int(idNarudzba),
                new_idKontakt=int(new_idKontakt),
                new_idProizvod=int(new_idProizvod),
                new_kolicina=new_kolicina,
                new_datumPrimitka=d_pr,
                new_datumNarudzbe=d_na
            )
            messagebox.showinfo("OK", "Zapis ažuriran.")
            load_ulazi()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    update_button.config(command=on_update)
