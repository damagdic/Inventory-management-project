from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
import tkinter.ttk as ttk
from tkcalendar import DateEntry
from datetime import datetime, date

from repo_narudzba import fetch_kontakti, fetch_proizvodi
from repo_izlaz import create_otpremnica_s_stavkama, update_otpremnica_i_detalj, fetch_izlazi_search

def izlaz_hladnjaca_form(window):
    izlaz_frame = Frame(window, bg='white', width=800, height=600)
    izlaz_frame.place(x=0, y=0)

    titlelabel = Label(izlaz_frame, text="Izlaz robe Hladnjača",
                       bg='blue', font=("times new roman", 24, "bold"), fg="white")
    titlelabel.place(x=0, y=0, relwidth=1)

    back_button = Button(izlaz_frame, text="Natrag", bg='white',
                         font=("times new roman", 15), fg="black",
                         command=lambda: izlaz_frame.destroy())
    back_button.place(x=10, y=10)

    left_frame = Frame(izlaz_frame, bg='white')
    left_frame.place(x=10, y=50, width=380, height=500)

    left_frame_title = Label(left_frame, text="Unos podataka", bg='white',
                             font=("times new roman", 20), fg="black")
    left_frame_title.grid(row=0, column=0, padx=10, pady=10)

    # Kontakt
    Label(left_frame, text="Kontakt:", bg='white').grid(row=1, column=0, sticky='e', padx=10, pady=6)
    kontakti = fetch_kontakti()
    kontakt_options = [k["naziv"] for k in kontakti]
    kontakt_id_by_name = {k["naziv"]: k["idKontakt"] for k in kontakti}
    kontakt_var = StringVar()
    kontakt_cb = Combobox(left_frame, textvariable=kontakt_var, state="readonly",
                          values=kontakt_options)
    kontakt_cb.grid(row=1, column=1, sticky='w', padx=10, pady=6)

    # Proizvod
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
    kolicina_entry = Entry(left_frame)
    kolicina_entry.grid(row=3, column=1, sticky='w', padx=10, pady=6)

    # Datum isporuke (nema datum otpremnice polja!)
    Label(left_frame, text="Datum isporuke:", bg='white').grid(row=4, column=0, sticky='e', padx=10, pady=6)
    datum_isporuke = DateEntry(left_frame, date_pattern='dd/mm/yyyy')
    datum_isporuke.grid(row=4, column=1, sticky='w', padx=10, pady=6)

    # Broj otpremnice
    Label(left_frame, text="Broj otpremnice:", bg='white').grid(row=5, column=0, sticky='e', padx=10, pady=6)
    broj_entry = Entry(left_frame)
    broj_entry.grid(row=5, column=1, sticky='w', padx=10, pady=6)

    # RIGHT (lista izlaza)
    right_frame = Frame(izlaz_frame, bg='white')
    right_frame.place(x=410, y=50, width=380, height=500)

    right_frame_title = Label(right_frame, text="Popis izlaza", bg='white',
                              font=("times new roman", 20), fg="black")
    right_frame_title.place(x=10, y=10)

    search_frame = Frame(right_frame, bg='white')
    search_frame.place(x=10, y=50, width=360, height=40)

    search_by = Combobox(search_frame, values=["Proizvod", "Kontakt", "Godina isporuke", "Otpremnica #"],
                         font=("times new roman", 10), state="readonly")
    search_by.set("Proizvod")
    search_by.grid(row=0, column=0, padx=5, pady=10)

    search_entry = Entry(search_frame, font=("times new roman", 10))
    search_entry.grid(row=0, column=1, padx=5, pady=10)

    search_button = Button(search_frame, text="Pretraži", bg='white',
                           font=("times new roman", 10), fg="black",
                           cursor="hand2")
    search_button.grid(row=0, column=2, padx=5, pady=10)

    tv_container = Frame(right_frame, bg='white')
    tv_container.place(x=10, y=100, width=360, height=350)

    cols = ("row_id","idOtpremnica","idKontakt","idProizvod",
            "kontakt","proizvod","kolicina","datum_isporuke","broj_otpremnice")
    izlazi_treeview = ttk.Treeview(tv_container, columns=cols, show='headings')
    izlazi_treeview.pack(side='left', fill='both', expand=True)
    vs = Scrollbar(tv_container, orient=VERTICAL, command=izlazi_treeview.yview)
    vs.pack(side=RIGHT, fill=Y)
    izlazi_treeview.configure(yscrollcommand=vs.set)

    for hidden in ("row_id","idOtpremnica","idKontakt","idProizvod"):
        izlazi_treeview.heading(hidden, text=hidden)
        izlazi_treeview.column(hidden, width=1, stretch=False, anchor='w')

    izlazi_treeview.heading("kontakt", text="Kontakt")
    izlazi_treeview.heading("proizvod", text="Proizvod")
    izlazi_treeview.heading("kolicina", text="Količina")
    izlazi_treeview.heading("datum_isporuke", text="Datum isporuke")
    izlazi_treeview.heading("broj_otpremnice", text="Broj otpremnice")

    izlazi_treeview.column("kontakt", width=60)
    izlazi_treeview.column("proizvod", width=100)
    izlazi_treeview.column("kolicina", width=60, anchor='e')
    izlazi_treeview.column("datum_isporuke", width=60)
    izlazi_treeview.column("broj_otpremnice", width=60)

    def load_izlazi(sb=None, term=None):
        rows = fetch_izlazi_search(search_by=sb, term=term, limit=200)
        izlazi_treeview.delete(*izlazi_treeview.get_children())
        for r in rows:
            izlazi_treeview.insert(
                "", "end",
                values=(r["row_id"], r["idOtpremnica"], r["idKontakt"], r["idProizvod"],
                        r["kontakt"], r["proizvod"], r["kolicina"], r["datum_isporuke"], r["broj_otpremnice"])
            )

    def do_search():
        sb = search_by.get()
        term = search_entry.get().strip()
        if sb in ("Godina isporuke","Otpremnica #") and term and not term.isdigit():
            messagebox.showwarning("Upozorenje", "Unesi broj.")
            return
        load_izlazi(sb, term)

    search_button.config(command=do_search)
    search_entry.bind("<Return>", lambda e: do_search())

    def on_select(event=None):
        sel = izlazi_treeview.selection()
        if not sel:
            return
        vals = izlazi_treeview.item(sel[0], "values")
        # redoslijed: row_id, idOtpremnica, idKontakt, idProizvod, kontakt, proizvod, kolicina, datum_isporuke, broj
        _, _, _, _, kontakt, proizvod, kolicina, dat_is, broj = vals
        kontakt_cb.set(kontakt)
        proizvod_cb.set(proizvod)
        kolicina_entry.delete(0, END); kolicina_entry.insert(0, kolicina)
        try:
            datum_isporuke.set_date(datetime.strptime(dat_is, "%d.%m.%Y").date())
        except:
            pass
        broj_entry.delete(0, END); broj_entry.insert(0, broj)

    izlazi_treeview.bind("<<TreeviewSelect>>", on_select)

    def on_unesi():
        try:
            name_k = kontakt_cb.get().strip()
            name_p = proizvod_cb.get().strip()
            if not name_k or not name_p:
                raise ValueError("Odaberi kontakt i proizvod.")
            idKontakt  = kontakt_id_by_name[name_k]
            idProizvod = proizvod_id_by_name[name_p]

            k_txt = kolicina_entry.get().strip()
            if not k_txt.isdigit() or int(k_txt) <= 0:
                raise ValueError("Količina mora biti pozitivan cijeli broj.")
            kolicina = int(k_txt)

            broj = broj_entry.get().strip()
            if not broj:
                raise ValueError("Upiši broj otpremnice.")

            # datumi: isporuka iz polja, otpremnica bez polja -> postavimo automatski
            d_is = datetime.strptime(datum_isporuke.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            d_ot = d_is   # ili date.today().strftime("%Y-%m-%d") ako želiš "danas"

            idOtp = create_otpremnica_s_stavkama(
                idKontakt=idKontakt,
                datumOtpremnice=d_ot,
                datumIsporuke=d_is,
                brojOtpremnice=broj,
                stavke=[(idProizvod, kolicina)]
            )
            messagebox.showinfo("OK", f"Otpremnica #{idOtp} je spremljena.")
            load_izlazi()
            # reset
            proizvod_var.set(""); kolicina_entry.delete(0, END)
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    unesi_button = Button(left_frame, text="Unesi", bg='white', font=("times new roman", 15),
                          fg="black", command=on_unesi)
    unesi_button.grid(row=6, column=0, columnspan=2, pady=10)

    def on_update():
        sel = izlazi_treeview.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberi red za ažuriranje.")
            return
        vals = izlazi_treeview.item(sel[0], "values")
        row_id, idOtp, _, _, _, _, _, _, _ = vals
        try:
            name_k = kontakt_cb.get().strip()
            name_p = proizvod_cb.get().strip()
            if not name_k or not name_p:
                raise ValueError("Odaberi kontakt i proizvod.")
            new_idKontakt  = kontakt_id_by_name[name_k]
            new_idProizvod = proizvod_id_by_name[name_p]

            k_txt = kolicina_entry.get().strip()
            if not k_txt.isdigit() or int(k_txt) <= 0:
                raise ValueError("Količina mora biti pozitivan cijeli broj.")
            new_kolicina = int(k_txt)

            broj = broj_entry.get().strip()
            if not broj:
                raise ValueError("Upiši broj otpremnice.")

            d_is = datetime.strptime(datum_isporuke.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            d_ot = d_is  # bez zasebnog polja

            update_otpremnica_i_detalj(
                row_id=int(row_id),
                idOtpremnica=int(idOtp),
                new_idKontakt=int(new_idKontakt),
                new_idProizvod=int(new_idProizvod),
                new_kolicina=new_kolicina,
                new_datumOtpremnice=d_ot,
                new_datumIsporuke=d_is,
                new_brojOtpremnice=broj
            )
            messagebox.showinfo("OK", "Zapis ažuriran.")
            load_izlazi(search_by.get(), search_entry.get().strip())
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    Button(right_frame, text="Ažuriraj", bg='white',
           font=("times new roman", 10), fg="black",
           cursor="hand2", command=on_update).place(x=10, y=460)


    load_izlazi()