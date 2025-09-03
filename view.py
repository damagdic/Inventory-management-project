# view.py
from __future__ import annotations
from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime, date
from typing import Optional

try:
    from tkcalendar import DateEntry
    _HAS_CAL = True
except Exception:
    _HAS_CAL = False

from model import Kontakt, Proizvod
from presenter import (
    # zajednički
    fetch_kontakti, fetch_proizvodi,
    # ulaz
    create_ulaz, update_ulaz, fetch_ulazi,
    # izlaz
    create_izlaz, update_izlaz, fetch_izlazi,
    # stanje
    fetch_stanje,
    # kontakti
    list_kontakti, create_kontakt, update_kontakt, delete_kontakt
)

# -----------------------------
# Pomocne
# -----------------------------

def _parse_ddmmyyyy_to_iso(s: str) -> str:
    """'dd.mm.yyyy' -> 'YYYY-MM-DD'"""
    return datetime.strptime(s.strip(), "%d.%m.%Y").strftime("%Y-%m-%d")

def _iso_to_ddmmyyyy(s: str) -> str:
    """'YYYY-MM-DD' -> 'dd.mm.yyyy'"""
    return datetime.strptime(s, "%Y-%m-%d").strftime("%d.%m.%Y")

def _get_date_widget(parent):
    if _HAS_CAL:
        de = DateEntry(parent, date_pattern='dd.mm.yyyy')
        de.set_date(date.today())
        return de
    e = Entry(parent)
    e.insert(0, date.today().strftime("%d.%m.%Y"))
    return e

def _get_date_iso(widget) -> str:
    """Vrati 'YYYY-MM-DD' iz widgeta (DateEntry ili Entry)."""
    if _HAS_CAL and isinstance(widget, DateEntry):
        d = widget.get_date()              
        return d.strftime("%Y-%m-%d")
    return datetime.strptime(widget.get().strip(), "%d.%m.%Y").strftime("%Y-%m-%d")



# -----------------------------
# Ekran: Ulaz Hladnjača
# -----------------------------
class UlazHladnjaca(Frame):
    def __init__(self, master):
        super().__init__(master, bg='white', width=800, height=600)
        self.place(x=0, y=0)

        Label(self, text="Ulaz robe Hladnjača", bg='blue', fg='white',
            font=("times new roman", 24, "bold")).place(x=0, y=0, relwidth=1)

        Button(self, text="Natrag", command=self.destroy).place(x=10, y=10)

        # lijevo – forma
        left = Frame(self, bg='white'); left.place(x=10, y=50, width=380, height=500)
        Label(left, text="Unos podataka", bg='white',
            font=("times new roman", 20)).grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # kontakt
        Label(left, text="Kontakt:", bg='white').grid(row=1, column=0, sticky='e', padx=10, pady=6)
        self.kontakti = fetch_kontakti()
        self.kontakt_id_by_name = {k.naziv: k.idKontakt for k in self.kontakti}
        self.kontakt_var = StringVar()
        self.cb_kontakt = ttk.Combobox(left, textvariable=self.kontakt_var, values=[k.naziv for k in self.kontakti], state="readonly")
        self.cb_kontakt.grid(row=1, column=1, sticky='w', padx=10, pady=6)

        # proizvod
        Label(left, text="Proizvod:", bg='white').grid(row=2, column=0, sticky='e', padx=10, pady=6)
        self.proizvodi = fetch_proizvodi()
        self.proizvod_id_by_name = {p.naziv: p.idProizvod for p in self.proizvodi}
        self.proizvod_var = StringVar()
        self.cb_proizvod = ttk.Combobox(left, textvariable=self.proizvod_var, values=[p.naziv for p in self.proizvodi], state="readonly")
        self.cb_proizvod.grid(row=2, column=1, sticky='w', padx=10, pady=6)

        # kolicina
        Label(left, text="Količina:", bg='white').grid(row=3, column=0, sticky='e', padx=10, pady=6)
        self.e_kolicina = Entry(left); self.e_kolicina.grid(row=3, column=1, sticky='w', padx=10, pady=6)

        # datumi
        Label(left, text="Datum primitka:", bg='white').grid(row=4, column=0, sticky='e', padx=10, pady=6)
        self.w_dat_pr = _get_date_widget(left); self.w_dat_pr.grid(row=4, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Datum narudžbe:", bg='white').grid(row=5, column=0, sticky='e', padx=10, pady=6)
        self.w_dat_na = _get_date_widget(left); self.w_dat_na.grid(row=5, column=1, sticky='w', padx=10, pady=6)

        Button(left, text="Unesi", command=self.on_unesi).grid(row=6, column=0, columnspan=2, pady=10)

        # desno – lista + update
        right = Frame(self, bg='white'); right.place(x=410, y=50, width=380, height=500)
        Label(right, text="Popis ulaza", bg='white',
            font=("times new roman", 20)).place(x=10, y=10)

        tv_container = Frame(right, bg='white'); tv_container.place(x=10, y=50, width=360, height=400)
        self.tv = ttk.Treeview(tv_container, columns=("row_id","idNar","idKon","idPro","kontakt","proizvod","kolicina","datum_primitka"), show='headings')
        self.tv.pack(side='left', fill='both', expand=True)
        vs = Scrollbar(tv_container, orient=VERTICAL, command=self.tv.yview); vs.pack(side='right', fill=Y)
        self.tv.configure(yscrollcommand=vs.set)

        for c in ("row_id","idNar","idKon","idPro"):
            self.tv.heading(c, text=c); self.tv.column(c, width=1, stretch=False)
        self.tv.heading("kontakt", text="Kontakt")
        self.tv.heading("proizvod", text="Proizvod")
        self.tv.heading("kolicina", text="Količina")
        self.tv.heading("datum_primitka", text="Datum primitka")

        self.tv.column("kontakt", width=100)
        self.tv.column("proizvod", width=100)
        self.tv.column("kolicina", width=70, anchor='e')
        self.tv.column("datum_primitka", width=90, anchor='center')

        self.tv.bind("<<TreeviewSelect>>", self.on_select)

        Button(right, text="Ažuriraj odabrani", command=self.on_update).place(x=10, y=460)

        self.load_ulazi()

    def _get_date(self, widget) -> str:
        if _HAS_CAL:
            # DateEntry.get() vraća string u zadanom patternu
            return _parse_ddmmyyyy_to_iso(widget.get())
        return _parse_ddmmyyyy_to_iso(widget.get())

    def on_unesi(self):
        try:
            if not self.kontakt_var.get() or not self.proizvod_var.get():
                raise ValueError("Odaberi kontakt i proizvod.")
            idKontakt = self.kontakt_id_by_name[self.kontakt_var.get()]
            idProizvod = self.proizvod_id_by_name[self.proizvod_var.get()]
            kolicina = int(self.e_kolicina.get().strip())
            if kolicina <= 0: raise ValueError("Količina mora biti > 0.")

            d_pr = _get_date_iso(self.w_dat_pr)
            d_na = _get_date_iso(self.w_dat_na)

            nar = create_ulaz(
                idKontakt=idKontakt,
                datumNarudzbe=d_na,
                datumPrimitka=d_pr,
                stavke=[(idProizvod, kolicina)]
            )
            messagebox.showinfo("OK", f"Narudžba #{nar.idNarudzba} spremljena.")
            self.load_ulazi()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def load_ulazi(self):
        rows = fetch_ulazi(limit=200)
        self.tv.delete(*self.tv.get_children())
        for r in rows:
            self.tv.insert("", "end", values=(
                r["row_id"], r["idNarudzba"], r["idKontakt"], r["idProizvod"],
                r["kontakt"], r["proizvod"], r["kolicina"], r["datum_primitka"]
            ))

    def on_select(self, _=None):
        sel = self.tv.selection()
        if not sel: return
        vals = self.tv.item(sel[0], "values")
        # redoslijed: row_id,idNar,idKon,idPro,kontakt,proizvod,kolicina,dat_pr
        _, dat_nar, _, _, kontakt, proizvod, kolicina, dat_pr = vals
        self.kontakt_var.set(kontakt)
        self.proizvod_var.set(proizvod)
        self.e_kolicina.delete(0, END); self.e_kolicina.insert(0, kolicina)
        try:
            # dat_pr je već "dd.mm.yyyy"; DateEntry ima set_date(date)
            if _HAS_CAL:
                d = datetime.strptime(dat_pr, "%d.%m.%Y").date()
                self.w_dat_pr.set_date(d)
            else:
                pass
        except:
            pass

    def on_update(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberi red.")
            return
        vals = self.tv.item(sel[0], "values")
        row_id, idNar, *_ = vals
        try:
            idKontakt = self.kontakt_id_by_name[self.kontakt_var.get()]
            idProizvod = self.proizvod_id_by_name[self.proizvod_var.get()]
            kolicina = int(self.e_kolicina.get().strip())
            d_pr = _get_date_iso(self.w_dat_pr)
            d_na = _get_date_iso(self.w_dat_na)

            update_ulaz(
                row_id=int(row_id),
                idNarudzba=int(idNar),
                new_idKontakt=int(idKontakt),
                new_idProizvod=int(idProizvod),
                new_kolicina=int(kolicina),
                new_datumNarudzbe=d_na,
                new_datumPrimitka=d_pr
            )
            messagebox.showinfo("OK", "Zapis ažuriran.")
            self.load_ulazi()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

# -----------------------------
# Ekran: Izlaz Hladnjača
# -----------------------------
class IzlazHladnjaca(Frame):
    def __init__(self, master):
        super().__init__(master, bg='white', width=800, height=600)
        self.place(x=0, y=0)

        Label(self, text="Izlaz robe Hladnjača", bg='blue', fg='white',
            font=("times new roman", 24, "bold")).place(x=0, y=0, relwidth=1)
        Button(self, text="Natrag", command=self.destroy).place(x=10, y=10)

        left = Frame(self, bg='white'); left.place(x=10, y=50, width=380, height=500)
        Label(left, text="Unos izlaza", bg='white', font=("times new roman", 20)).grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        Label(left, text="Kontakt:", bg='white').grid(row=1, column=0, sticky='e', padx=10, pady=6)
        self.kontakti = fetch_kontakti()
        self.kontakt_id_by_name = {k.naziv: k.idKontakt for k in self.kontakti}
        self.kontakt_var = StringVar()
        self.cb_kontakt = ttk.Combobox(left, textvariable=self.kontakt_var, values=[k.naziv for k in self.kontakti], state="readonly")
        self.cb_kontakt.grid(row=1, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Proizvod:", bg='white').grid(row=2, column=0, sticky='e', padx=10, pady=6)
        self.proizvodi = fetch_proizvodi()
        self.proizvod_id_by_name = {p.naziv: p.idProizvod for p in self.proizvodi}
        self.proizvod_var = StringVar()
        self.cb_proizvod = ttk.Combobox(left, textvariable=self.proizvod_var, values=[p.naziv for p in self.proizvodi], state="readonly")
        self.cb_proizvod.grid(row=2, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Količina:", bg='white').grid(row=3, column=0, sticky='e', padx=10, pady=6)
        self.e_kolicina = Entry(left); self.e_kolicina.grid(row=3, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Datum isporuke:", bg='white').grid(row=4, column=0, sticky='e', padx=10, pady=6)
        self.w_dat_isporuke = _get_date_widget(left); self.w_dat_isporuke.grid(row=4, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Broj otpremnice:", bg='white').grid(row=5, column=0, sticky='e', padx=10, pady=6)
        self.e_broj = Entry(left); self.e_broj.grid(row=5, column=1, sticky='w', padx=10, pady=6)

        Button(left, text="Unesi izlaz", command=self.on_unesi).grid(row=6, column=0, columnspan=2, pady=10)

        right = Frame(self, bg='white'); right.place(x=410, y=50, width=380, height=500)
        Label(right, text="Popis izlaza", bg='white', font=("times new roman", 20)).place(x=10, y=10)

        tv_container = Frame(right, bg='white'); tv_container.place(x=10, y=50, width=360, height=400)
        self.tv = ttk.Treeview(tv_container, columns=("row_id","idOt","idKon","idPro","kontakt","proizvod","kolicina","broj_otpremnice","datum_isporuke"), show='headings')
        self.tv.pack(side='left', fill='both', expand=True)
        vs = Scrollbar(tv_container, orient=VERTICAL, command=self.tv.yview); vs.pack(side='right', fill=Y)
        self.tv.configure(yscrollcommand=vs.set)

        for c in ("row_id","idOt","idKon","idPro"):
            self.tv.heading(c, text=c); self.tv.column(c, width=1, stretch=False)
        self.tv.heading("kontakt", text="Kontakt")
        self.tv.heading("proizvod", text="Proizvod")
        self.tv.heading("kolicina", text="Količina")
        self.tv.heading("broj_otpremnice", text="Br. otpremnice")
        self.tv.heading("datum_isporuke", text="Datum isporuke")

        self.tv.column("kontakt", width=100)
        self.tv.column("proizvod", width=100)
        self.tv.column("kolicina", width=70, anchor='e')
        self.tv.column("broj_otpremnice", width=110, anchor='w')
        self.tv.column("datum_isporuke", width=100, anchor='center')

        self.tv.bind("<<TreeviewSelect>>", self.on_select)

        Button(right, text="Ažuriraj odabrani", command=self.on_update).place(x=10, y=460)

        self.load_izlazi()

    def on_unesi(self):
        try:
            if not self.kontakt_var.get() or not self.proizvod_var.get():
                raise ValueError("Odaberi kontakt i proizvod.")
            idKontakt = self.kontakt_id_by_name[self.kontakt_var.get()]
            idProizvod = self.proizvod_id_by_name[self.proizvod_var.get()]
            kolicina = int(self.e_kolicina.get().strip())
            if kolicina <= 0: raise ValueError("Količina mora biti > 0.")
            d_isporuke = _parse_ddmmyyyy_to_iso(self.w_dat_isporuke.get())
            broj = (self.e_broj.get() or "").strip()
            if not broj: raise ValueError("Upiši broj otpremnice.")

            idOt = create_izlaz(
                idKontakt=idKontakt,
                datumIsporuke=d_isporuke,
                brojOtpremnice=broj,
                stavke=[(idProizvod, kolicina, None)]
            )
            messagebox.showinfo("OK", f"Otpremnica #{idOt.brojOtpremnice} spremljena.")
            self.load_izlazi()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def load_izlazi(self):
        rows = fetch_izlazi(limit=200)
        self.tv.delete(*self.tv.get_children())
        for r in rows:
            self.tv.insert("", "end", values=(
                r["row_id"], r["idOtpremnica"], r["idKontakt"], r["idProizvod"],
                r["kontakt"], r["proizvod"], r["kolicina"], r["broj_otpremnice"], r["datum_isporuke"]
            ))

    def on_select(self, _=None):
        sel = self.tv.selection()
        if not sel: return
        vals = self.tv.item(sel[0], "values")
        # row_id,idOt,idKon,idPro,kontakt,proizvod,kolicina,broj,dat
        _, _, _, _, kontakt, proizvod, kolicina, broj, dat = vals
        self.kontakt_var.set(kontakt)
        self.proizvod_var.set(proizvod)
        self.e_kolicina.delete(0, END); self.e_kolicina.insert(0, kolicina)
        self.e_broj.delete(0, END); self.e_broj.insert(0, broj)
        try:
            if _HAS_CAL:
                d = datetime.strptime(dat, "%d.%m.%Y").date()
                self.w_dat_isporuke.set_date(d)
        except: pass

    def on_update(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberi red.")
            return
        vals = self.tv.item(sel[0], "values")
        row_id, idOt, *_ = vals
        try:
            idKontakt = self.kontakt_id_by_name[self.kontakt_var.get()]
            idProizvod = self.proizvod_id_by_name[self.proizvod_var.get()]
            kolicina = int(self.e_kolicina.get().strip())
            broj = (self.e_broj.get() or "").strip()
            d_isporuke = _parse_ddmmyyyy_to_iso(self.w_dat_isporuke.get())

            update_izlaz(
                row_id=int(row_id),
                idOtpremnica=int(idOt),
                new_idKontakt=int(idKontakt),
                new_idProizvod=int(idProizvod),
                new_kolicina=kolicina,
                new_datumIsporuke=d_isporuke,
                new_brojOtpremnice=broj
            )
            messagebox.showinfo("OK", "Zapis ažuriran.")
            self.load_izlazi()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

# -----------------------------
# Ekran: Stanje
# -----------------------------
class StanjeHladnjaca(Frame):
    def __init__(self, master):
        super().__init__(master, bg='white', width=800, height=600)
        self.place(x=0, y=0)
        Label(self, text="Stanje – Hladnjača", bg='blue', fg='white',
            font=("times new roman", 24, "bold")).place(x=0, y=0, relwidth=1)
        Button(self, text="Natrag", command=self.destroy).place(x=10, y=10)

        search = Frame(self, bg='white'); search.place(x=10, y=60, width=780, height=40)
        Label(search, text="Pretraži naziv:", bg='white').grid(row=0, column=0, padx=6)
        self.term_var = StringVar()
        Entry(search, textvariable=self.term_var, width=30).grid(row=0, column=1, padx=6)
        self.exclude_var = BooleanVar(value=True)
        Checkbutton(search, text="Isključi 'Kiseli kupus' artikle", variable=self.exclude_var, bg='white').grid(row=0, column=2, padx=12)
        Button(search, text="Traži", command=self.load_data).grid(row=0, column=3, padx=6)
        Button(search, text="Reset", command=lambda:(self.term_var.set(""), self.load_data())).grid(row=0, column=4, padx=6)

        tv_container = Frame(self, bg='white'); tv_container.place(x=10, y=110, width=780, height=430)
        self.tv = ttk.Treeview(tv_container, columns=("naziv","jm","stanje","cijena"), show='headings')
        self.tv.pack(side='left', fill='both', expand=True)
        vs = Scrollbar(tv_container, orient=VERTICAL, command=self.tv.yview); vs.pack(side='right', fill=Y)
        self.tv.configure(yscrollcommand=vs.set)

        self.tv.heading("naziv", text="Naziv")
        self.tv.heading("jm", text="JM")
        self.tv.heading("stanje", text="Stanje")
        self.tv.heading("cijena", text="Cijena")

        self.tv.column("naziv", width=380)
        self.tv.column("jm", width=80, anchor='center')
        self.tv.column("stanje", width=120, anchor='e')
        self.tv.column("cijena", width=120, anchor='e')

        self.tv.tag_configure("neg", background="#ffe5e5")

        self.load_data()

    def load_data(self):
        rows = fetch_stanje(term=self.term_var.get().strip() or None, exclude_kupus=self.exclude_var.get())
        self.tv.delete(*self.tv.get_children())
        for r in rows:
            naziv = r["naziv"]
            jm = r["jm"]
            stanje = r["stanje"] if r["stanje"] is not None else 0
            cijena = r["cijena"]
            cijena_txt = "" if cijena is None else f"{cijena:.2f}"
            tags = ("neg",) if (stanje is None or stanje <= 0) else ()
            self.tv.insert("", "end", values=(naziv, jm, stanje, cijena_txt), tags=tags)

# -----------------------------
# Ekran: Kontakti (CRUD)
# -----------------------------
class KontaktiScreen(Frame):
    def __init__(self, master):
        super().__init__(master, bg='white', width=800, height=600)
        self.place(x=0, y=0)
        Label(self, text="Kontakti", bg='blue', fg='white',
            font=("times new roman", 24, "bold")).place(x=0, y=0, relwidth=1)
        Button(self, text="Natrag", command=self.destroy).place(x=10, y=10)

        left = Frame(self, bg='white'); left.place(x=10, y=60, width=360, height=520)
        Label(left, text="Dodaj/Ažuriraj kontakt", bg='white',
            font=("times new roman", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,10), sticky='w')

        Label(left, text="Naziv*", bg='white').grid(row=1, column=0, sticky='e', padx=6, pady=4)
        self.e_naziv = Entry(left, width=30); self.e_naziv.grid(row=1, column=1, sticky='w', padx=6, pady=4)

        Label(left, text="OIB", bg='white').grid(row=2, column=0, sticky='e', padx=6, pady=4)
        self.e_oib = Entry(left, width=30); self.e_oib.grid(row=2, column=1, sticky='w', padx=6, pady=4)

        Label(left, text="Adresa", bg='white').grid(row=3, column=0, sticky='e', padx=6, pady=4)
        self.e_adresa = Entry(left, width=30); self.e_adresa.grid(row=3, column=1, sticky='w', padx=6, pady=4)

        Label(left, text="Kontakt osoba", bg='white').grid(row=4, column=0, sticky='e', padx=6, pady=4)
        self.e_kosoba = Entry(left, width=30); self.e_kosoba.grid(row=4, column=1, sticky='w', padx=6, pady=4)

        Label(left, text="Telefon", bg='white').grid(row=5, column=0, sticky='e', padx=6, pady=4)
        self.e_telefon = Entry(left, width=30); self.e_telefon.grid(row=5, column=1, sticky='w', padx=6, pady=4)

        btns = Frame(left, bg='white'); btns.grid(row=6, column=0, columnspan=2, pady=8)
        Button(btns, text="Spremi novi", command=self.on_save).pack(side='left', padx=4)
        Button(btns, text="Ažuriraj", command=self.on_update).pack(side='left', padx=4)
        Button(btns, text="Obriši", command=self.on_delete).pack(side='left', padx=4)

        right = Frame(self, bg='white'); right.place(x=380, y=60, width=410, height=520)
        search = Frame(right, bg='white'); search.pack(fill='x')
        Label(search, text="Traži (naziv):", bg='white').pack(side='left', padx=6)
        self.term_var = StringVar()
        Entry(search, textvariable=self.term_var, width=25).pack(side='left', padx=6)
        Button(search, text="Traži", command=self.load_list).pack(side='left', padx=6)
        Button(search, text="Reset", command=lambda:(self.term_var.set(""), self.load_list())).pack(side='left', padx=6)

        tv_container = Frame(right, bg='white'); tv_container.pack(fill='both', expand=True, padx=6, pady=6)
        self.tv = ttk.Treeview(tv_container, columns=("id","naziv","oib","adresa","kontakt","telefon"), show='headings')
        self.tv.pack(side='left', fill='both', expand=True)
        vs = Scrollbar(tv_container, orient=VERTICAL, command=self.tv.yview); vs.pack(side='right', fill=Y)
        self.tv.configure(yscrollcommand=vs.set)

        for col, title, w, anc in [
            ("id","ID",60,'e'), ("naziv","Naziv",150,'w'), ("oib","OIB",110,'e'),
            ("adresa","Adresa",180,'w'), ("kontakt","Kontakt osoba",140,'w'),
            ("telefon","Telefon",110,'w')
        ]:
            self.tv.heading(col, text=title); self.tv.column(col, width=w, anchor=anc)

        self.tv.bind("<<TreeviewSelect>>", self.on_select)
        self._selected_id: Kontakt | None = None

        self.load_list()

    def load_list(self, term: str | None = None):
        self.tv.delete(*self.tv.get_children())
        self._rows: list[Kontakt] = fetch_kontakti(term)  
        for k in self._rows:
            self.tv.insert("", "end", values=(
                k.idKontakt, k.naziv, k.OIB or "", k.adresa or "", k.kontaktOsoba or "", k.telefon or ""
            ))

    def on_select(self, _=None):
        sel = self.tv.selection()
        if not sel: 
            self._selected_id = None
            return
        vals = self.tv.item(sel[0], "values")
        idk = int(vals[0])
        found = next((x for x in getattr(self, "_rows", []) if x.idKontakt == idk), None)
        if found is None:
            found = Kontakt.get(idk)
        self._selected_id = found
        self.e_naziv.delete(0, END);   self.e_naziv.insert(0, found.naziv or "")
        self.e_oib.delete(0, END);     self.e_oib.insert(0, found.OIB or "")
        self.e_adresa.delete(0, END);  self.e_adresa.insert(0, found.adresa or "")
        self.e_kosoba.delete(0, END);  self.e_kosoba.insert(0, found.kontaktOsoba or "")
        self.e_telefon.delete(0, END); self.e_telefon.insert(0, found.telefon or "")

    def on_save(self):
        try:
            k = Kontakt(
                idKontakt=None,
                naziv=self.e_naziv.get(),
                OIB=self.e_oib.get(),
                adresa=self.e_adresa.get(),
                kontaktOsoba=self.e_kosoba.get(),
                telefon=self.e_telefon.get()
            )
            new_id = k.save()  # INSERT u save()
            messagebox.showinfo("OK", f"Kontakt dodan (ID: {new_id}).")
            self._selected_id = k
            self.load_list()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def on_update(self):
        if not self._selected_id:
            messagebox.showwarning("Upozorenje", "Odaberite kontakt.")
            return
        try:
            k = self._selected_id 
            k.naziv = self.e_naziv.get()
            k.OIB = self.e_oib.get()
            k.adresa = self.e_adresa.get()
            k.kontaktOsoba = self.e_kosoba.get()
            k.telefon = self.e_telefon.get()
            k.save()  
            messagebox.showinfo("OK", "Kontakt ažuriran.")
            self.load_list()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def on_delete(self):
        if not self._selected_id:
            messagebox.showwarning("Upozorenje", "Odaberite kontakt.")
            return
        if not messagebox.askyesno("Potvrda", "Obrisati odabrani kontakt?"):
            return
        try:
            self._selected_id.delete()
            self._selected_id = None
            messagebox.showinfo("OK", "Kontakt obrisan.")
            self.load_list()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

# -----------------------------
# Dashboard (glavni ekran)
# -----------------------------
class Dashboard(Tk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard")
        self.geometry("800x600")
        self.resizable(False, False)
        self.config(bg='white')

        self.header = Label(self, text="Kontrola ulaza i izlaza",
                            bg='blue', fg='white',
                            font=("times new roman", 24, "bold"))
        self.header.place(x=0, y=0, relwidth=1, height=60)

        self.content = Frame(self, bg='white')
        self.content.place(x=0, y=60, relwidth=1, relheight=1)

        self.show_main_menu()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_main_menu(self):
        self._clear_content()

        wrap = Frame(self.content, bg='white')
        wrap.place(relx=0.5, rely=0.5, anchor='center')

        Label(wrap, text="Dobrodošli!", bg='white',
              font=("times new roman", 18, "bold")).pack(pady=(0, 16))

        btn_width = 26
        pady = 6

        Button(wrap, text="Skladište Hladnjača",
               font=("times new roman", 14),
               command=self.show_hladnjaca_menu,
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Skladište Pogon",
               font=("times new roman", 14),
               state="disabled",  # ili command=self.show_pogon_menu 
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Kontakti",
               font=("times new roman", 14),
               command=lambda: KontaktiScreen(self),
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Izlaz",
               font=("times new roman", 14),
               command=self.destroy,
               width=btn_width).pack(pady=(pady, 0), fill='x')
    
    def show_pogon_menu(self):
        self._clear_content()

        wrap = Frame(self.content, bg='white')
        wrap.place(relx=0.5, rely=0.5, anchor='center')

        Label(wrap, text="Skladište Pogon", bg='white',
              font=("times new roman", 18, "bold")).pack(pady=(0, 16))

        btn_width = 26
        pady = 6

        Button(wrap, text="Ulaz robe",
               font=("times new roman", 14),
               state="disabled",
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Izlaz robe",
               font=("times new roman", 14),
               state="disabled",
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Provjeri stanje",
               font=("times new roman", 14),
               state="disabled",
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Statistika",
               font=("times new roman", 14),
               state="disabled",
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Natrag",
               font=("times new roman", 14),
               command=self.show_main_menu,
               width=btn_width).pack(pady=(pady, 0), fill='x')

    def show_hladnjaca_menu(self):
        self._clear_content()

        wrap = Frame(self.content, bg='white')
        wrap.place(relx=0.5, rely=0.5, anchor='center')

        Label(wrap, text="Skladište Hladnjača", bg='white',
              font=("times new roman", 18, "bold")).pack(pady=(0, 16))

        btn_width = 26
        pady = 6

        Button(wrap, text="Ulaz robe",
               font=("times new roman", 14),
               command=lambda: UlazHladnjaca(self),
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Izlaz robe",
               font=("times new roman", 14),
               command=lambda: IzlazHladnjaca(self),
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Provjeri stanje",
               font=("times new roman", 14),
               command=lambda: StanjeHladnjaca(self),
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Statistika",
               font=("times new roman", 14),
               state="disabled",
               width=btn_width).pack(pady=pady, fill='x')

        Button(wrap, text="Natrag",
               font=("times new roman", 14),
               command=self.show_main_menu,
               width=btn_width).pack(pady=(pady, 0), fill='x')


def run():
    app = Dashboard()
    app.mainloop()


if __name__ == "__main__":
    run()