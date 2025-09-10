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
    create_izlaz, update_izlaz, fetch_izlazi, update_otpremnica_full, fetch_otpremnica_stavke, fetch_otpremnica_full, fetch_stavke_as_tuples,
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
        self.tv = ttk.Treeview(tv_container, columns=("row_id","idNar","idKon","idPro","kontakt","proizvod","kolicina","datum_primitka","datum_narudzbe"), show='headings')
        self.tv.pack(side='left', fill='both', expand=True)
        vs = Scrollbar(tv_container, orient=VERTICAL, command=self.tv.yview); vs.pack(side='right', fill=Y)
        self.tv.configure(yscrollcommand=vs.set)

        for c in ("row_id","idNar","idKon","idPro","datum_narudzbe"):
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
                r["kontakt"], r["proizvod"], r["kolicina"], r["datum_primitka"], r["datum_narudzbe"]
            ))

    def on_select(self, _=None):
        sel = self.tv.selection()
        if not sel: return
        vals = self.tv.item(sel[0], "values")
        # redoslijed: row_id,idNar,idKon,idPro,kontakt,proizvod,kolicina,dat_pr
        _, _, _, _, kontakt, proizvod, kolicina, dat_pr, dat_na = vals
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
        try:
            d = datetime.strptime(dat_na, "%d.%m.%Y").date()
            if hasattr(self.w_dat_na, "set_date"):
                self.w_dat_na.set_date(d)
            else:
                self.w_dat_na.delete(0, END); self.w_dat_na.insert(0, dat_na)
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

        Label(left, text="Kontakt:", bg='white').grid(row=6, column=0, sticky='e', padx=10, pady=6)
        self.kontakti = fetch_kontakti()
        self.kontakt_id_by_name = {k.naziv: k.idKontakt for k in self.kontakti}
        self.kontakt_var = StringVar()
        self.cb_kontakt = ttk.Combobox(left, textvariable=self.kontakt_var, values=[k.naziv for k in self.kontakti], state="readonly")
        self.cb_kontakt.grid(row=6, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Proizvod:", bg='white').grid(row=1, column=0, sticky='e', padx=10, pady=6)
        self.proizvodi = fetch_proizvodi()
        self.proizvod_id_by_name = {p.naziv: p.idProizvod for p in self.proizvodi}
        self.proizvod_var = StringVar()
        self.cb_proizvod = ttk.Combobox(left, textvariable=self.proizvod_var, values=[p.naziv for p in self.proizvodi], state="readonly")
        self.cb_proizvod.grid(row=1, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Količina:", bg='white').grid(row=2, column=0, sticky='e', padx=10, pady=6)
        self.e_kolicina = Entry(left); self.e_kolicina.grid(row=2, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Cijena:", bg='white').grid(row=3, column=0, sticky='e', padx=10, pady=6)
        self.e_cijena = Entry(left); self.e_cijena.grid(row=3, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Datum isporuke:", bg='white').grid(row=7, column=0, sticky='e', padx=10, pady=6)
        self.w_dat_isporuke = _get_date_widget(left); self.w_dat_isporuke.grid(row=7, column=1, sticky='w', padx=10, pady=6)

        Label(left, text="Broj otpremnice:", bg='white').grid(row=8, column=0, sticky='e', padx=10, pady=6)
        self.e_broj = Entry(left); self.e_broj.grid(row=8, column=1, sticky='w', padx=10, pady=6)

        self.stavke = []  # lista dictova: {"idProizvod":..., "naziv":..., "kolicina":..., "cijena": Optional[float]}

        # tablica stavki (lokalna košarica prije spremanja)
        box = Frame(left, bg='white'); box.grid(row=5, column=0, columnspan=2, sticky='nsew', padx=0, pady=(4,0))
        self.tv_stavke = ttk.Treeview(box, columns=("proizvod","kolicina","cijena"), show='headings', height=7)
        self.tv_stavke.heading("proizvod", text="Proizvod")
        self.tv_stavke.heading("kolicina", text="Količina")
        self.tv_stavke.heading("cijena", text="Cijena")
        self.tv_stavke.column("proizvod", width=160)
        self.tv_stavke.column("kolicina", width=80, anchor='e')
        self.tv_stavke.column("cijena", width=80, anchor='e')
        self.tv_stavke.pack(side='left', fill='both', expand=True)
        vs1 = Scrollbar(box, orient=VERTICAL, command=self.tv_stavke.yview); vs1.pack(side='right', fill=Y)
        self.tv_stavke.configure(yscrollcommand=vs1.set)

        btns = Frame(left, bg='white'); btns.grid(row=4, column=0, columnspan=2, pady=6)
        Button(btns, text="Dodaj stavku", command=self.on_dodaj_stavku).pack(side='left', padx=3)
        Button(btns, text="Ukloni stavku", command=self.on_ukloni_stavku).pack(side='left', padx=3)
        Button(btns, text="Isprazni", command=self.on_clear_stavke).pack(side='left', padx=3)

        Button(left, text="Kreiraj otpremnicu", command=self.on_unesi).grid(row=9, column=0, columnspan=2, pady=10)

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

        self._left_widgets = [
            self.cb_kontakt, self.cb_proizvod, self.e_kolicina,
            self.e_cijena, self.w_dat_isporuke, self.e_broj
        ]

        Button(right, text="Ažuriraj odabrani", command=self.on_open_editor).place(x=10, y=460)

        self.load_izlazi()

    def on_unesi(self):
        try:
            if not self.kontakt_var.get():
                raise ValueError("Odaberi kontakt.")
            idKontakt = self.kontakt_id_by_name[self.kontakt_var.get()]
            if not self.stavke:
                raise ValueError("Dodaj barem jednu stavku.")
            d_isporuke = _parse_ddmmyyyy_to_iso(self.w_dat_isporuke.get())
            broj = (self.e_broj.get() or "").strip()
            if not broj: 
                raise ValueError("Upiši broj otpremnice.")
    
            stavke_arg = []
            for s in self.stavke:
                cij = s.get("cijena")
                if cij is None:
                    cij = 0.0
                stavke_arg.append((s["idProizvod"], s["kolicina"], cij))

            ot = create_izlaz(
            idKontakt=idKontakt,
            datumIsporuke=d_isporuke,
            brojOtpremnice=broj,
            stavke=stavke_arg
            )
            messagebox.showinfo("OK", f"Izdan izlaz #{ot.idOtpremnica}.")
            # reset form
            self.stavke.clear(); self._refresh_stavke_tv()
            self.cb_kontakt.set(""); self.cb_proizvod.set("")
            self.e_kolicina.delete(0, END); self.e_broj.delete(0, END)
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
        if not sel: 
            self._selected_id_ot = None
            self._set_left_enabled(True)
            return
        
        vals = self.tv.item(sel[0], "values")
        # row_id,idOt,idKon,idPro,kontakt,proizvod,kolicina,broj,dat
        _, idOt, _, _, kontakt, proizvod, kolicina, broj, dat = vals
        self._selected_id_ot = int(idOt) 

        self.kontakt_var.set(kontakt)
        self.proizvod_var.set(proizvod)
        self.e_kolicina.delete(0, END); self.e_kolicina.insert(0, kolicina)
        self.e_broj.delete(0, END); self.e_broj.insert(0, broj)
        try:
            if _HAS_CAL:
                d = datetime.strptime(dat, "%d.%m.%Y").date()
                self.w_dat_isporuke.set_date(d)
        except: 
            pass

        try:
            idOt = int(idOt)
        except:
            return
        
        items = fetch_otpremnica_stavke(idOt)

        self.stavke.clear()
        self.tv_stavke.delete(*self.tv_stavke.get_children())

        for it in items:
            self.stavke.append({
                "idProizvod": it["idProizvod"],
                "naziv": it["proizvod"],
                "kolicina": int(it["kolicina"]),
                "cijena": it["cijena"],
            })
            self.tv_stavke.insert("", "end",
        values=(it["proizvod"], int(it["kolicina"]), "" if it["cijena"] is None else f"{it['cijena']:.2f}"))

        self._set_left_enabled(False)

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
    
    def on_dodaj_stavku(self):
        try:
            naziv = self.proizvod_var.get().strip()
            if not naziv:
                raise ValueError("Odaberi proizvod.")
            pid = self.proizvod_id_by_name[naziv]

            k_txt = self.e_kolicina.get().strip()
            if not k_txt.isdigit() or int(k_txt) <= 0:
                raise ValueError("Količina mora biti pozitivan cijeli broj.")
            kolicina = int(k_txt)

            cijena_txt = self.e_cijena.get().strip()
            cijena = float(cijena_txt) if cijena_txt else None

            # ako isti proizvod već postoji u košarici -> zbroji
            for s in self.stavke:
                if s["idProizvod"] == pid and s.get("cijena") == cijena:
                    s["kolicina"] += kolicina
                    break
            else:
                self.stavke.append({"idProizvod": pid, "naziv": naziv, "kolicina": kolicina, "cijena": cijena})

            self._refresh_stavke_tv()

            # reset polja za brzi unos sljedeće stavke
            self.proizvod_var.set("")
            self.e_kolicina.delete(0, END)
            self.e_cijena.delete(0, END)

        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def on_ukloni_stavku(self):
        sel = self.tv_stavke.selection()
        if not sel:
            return
        iid = sel[0]
        vals = self.tv_stavke.item(iid, "values")
        # values: (naziv, kolicina, cijena)
        naziv = vals[0]
        kolicina = int(vals[1])
        cijena = None if vals[2] in ("", None) else float(vals[2].replace(",", "."))
        for i, s in enumerate(self.stavke):
            if s["naziv"] == naziv and s["kolicina"] == kolicina and (s.get("cijena") == cijena):
                self.stavke.pop(i)
                break
        self._refresh_stavke_tv()

    def on_clear_stavke(self):
        self.stavke.clear()
        self._refresh_stavke_tv()

    def _refresh_stavke_tv(self):
        self.tv_stavke.delete(*self.tv_stavke.get_children())
        for s in self.stavke:
            c_txt = "" if s["cijena"] is None else f"{s['cijena']:.2f}"
            self.tv_stavke.insert("", "end", values=(s["naziv"], s["kolicina"], c_txt))

    def _set_left_enabled(self, enabled: bool):
        state = "readonly" if enabled else "disabled"
        # Combobox: 'readonly' ↔ 'disabled', Entry: 'normal' ↔ 'disabled'
        self.cb_kontakt.configure(state=state)
        self.cb_proizvod.configure(state=state)
        self.e_kolicina.configure(state=("normal" if enabled else "disabled"))
        self.e_cijena.configure(state=("normal" if enabled else "disabled"))
        try:
            # DateEntry ima 'state', Entry fallback nema; probaj:
            self.w_dat_isporuke.configure(state=("normal" if enabled else "disabled"))
        except Exception:
            pass
        self.e_broj.configure(state=("normal" if enabled else "disabled"))
    
    def on_open_editor(self):
        if not self._selected_id_ot:
            messagebox.showwarning("Upozorenje", "Odaberi red (otpremnicu) za uređivanje.")
            return
        OtpremnicaEditor(self, self._selected_id_ot, self.kontakti, self.proizvodi,
                         on_saved=self._after_editor_saved)

    def _after_editor_saved(self):
        # poziva editor nakon uspjeha
        self.load_izlazi()
        self._set_left_enabled(True)
        self._selected_id_ot = None


class OtpremnicaEditor(Toplevel):
    """
    Editor kompletne otpremnice:
      - zaglavlje (kontakt, datum isporuke, broj)
      - sve stavke (dodaj/ukloni/izmijeni)
      - Spremi izmjene -> update_otpremnica_full(...)
    """
    def __init__(self, master, idOt: int, kontakti, proizvodi, on_saved=None):
        super().__init__(master)
        self.title(f"Uredi otpremnicu #{idOt}")
        self.geometry("640x520")
        self.resizable(False, False)
        self.idOt = idOt
        self.on_saved = on_saved

        self.kontakti = kontakti
        self.proizvodi = proizvodi
        self.kontakt_id_by_name = {k.naziv: k.idKontakt for k in kontakti}
        self.proizvod_id_by_name = {p.naziv: p.idProizvod for p in proizvodi}

        # --- Zaglavlje ---
        top = Frame(self); top.pack(fill='x', padx=10, pady=10)

        Label(top, text="Kontakt:").grid(row=0, column=0, sticky='e', padx=6, pady=4)
        self.kontakt_var = StringVar()
        self.cb_kontakt = ttk.Combobox(top, textvariable=self.kontakt_var,
                                       values=[k.naziv for k in kontakti], state="readonly", width=40)
        self.cb_kontakt.grid(row=0, column=1, sticky='w', padx=6, pady=4)

        Label(top, text="Datum isporuke:").grid(row=1, column=0, sticky='e', padx=6, pady=4)
        self.w_dat = _get_date_widget(top)
        self.w_dat.grid(row=1, column=1, sticky='w', padx=6, pady=4)

        Label(top, text="Broj otpremnice:").grid(row=2, column=0, sticky='e', padx=6, pady=4)
        self.e_broj = Entry(top, width=30); self.e_broj.grid(row=2, column=1, sticky='w', padx=6, pady=4)

        # --- Stavke ---
        box = Frame(self); box.pack(fill='both', expand=True, padx=10, pady=(0,10))

        # Dodavanje/izmjena stavke
        form = Frame(box); form.pack(fill='x')
        Label(form, text="Proizvod:").grid(row=0, column=0, sticky='e', padx=6, pady=4)
        self.proizvod_var = StringVar()
        self.cb_proiz = ttk.Combobox(form, textvariable=self.proizvod_var,
                                     values=[p.naziv for p in proizvodi], state="readonly", width=35)
        self.cb_proiz.grid(row=0, column=1, sticky='w', padx=6, pady=4)

        Label(form, text="Količina:").grid(row=0, column=2, sticky='e', padx=4, pady=4)
        self.e_qty = Entry(form, width=10); self.e_qty.grid(row=0, column=3, sticky='w', padx=6, pady=4)

        Label(form, text="Cijena (opcionalno):").grid(row=0, column=4, sticky='e', padx=6, pady=4)
        self.e_cij = Entry(form, width=10); self.e_cij.grid(row=0, column=5, sticky='w', padx=6, pady=4)

        Button(form, text="Dodaj stavku", command=self._add_or_update_line).grid(row=1, column=1, sticky='e', padx=3)

        # Lista stavki
        list_box = Frame(box); list_box.pack(fill='both', expand=True, pady=6)
        self.tv = ttk.Treeview(list_box, columns=("proizvod","kolicina","cijena"), show='headings', height=10)
        self.tv.heading("proizvod", text="Proizvod")
        self.tv.heading("kolicina", text="Količina")
        self.tv.heading("cijena", text="Cijena")
        self.tv.column("proizvod", width=260)
        self.tv.column("kolicina", width=100, anchor='e')
        self.tv.column("cijena", width=100, anchor='e')
        self.tv.pack(side='left', fill='both', expand=True)

        vs = Scrollbar(list_box, orient=VERTICAL, command=self.tv.yview)
        vs.pack(side=RIGHT, fill=Y)
        self.tv.configure(yscrollcommand=vs.set)

        btns = Frame(box); btns.pack(fill='x')
        Button(btns, text="Ukloni stavku", command=self._remove_line).pack(side='left', padx=6)
        Button(btns, text="Isprazni sve", command=self._clear_lines).pack(side='left', padx=6)

        #Spremi 
        bottom = Frame(self); bottom.pack(fill='x', padx=10, pady=(0,10))
        Button(bottom, text="Spremi izmjene", command=self._save).pack(side='right')

        # podaci trenutne otpremnice
        self._lines: list[tuple[str,int,Optional[float]]] = []  # [(naziv, količina, cijena_or_None), ...]
        self._load_current()

        # double-click na listu -> ubaci vrijednosti u form za izmjenu
        self.tv.bind("<Double-1>", self._on_pick_line)

    def _load_current(self):
        data = fetch_otpremnica_full(self.idOt)
        if not data:
            messagebox.showerror("Greška", "Ne mogu učitati podatke otpremnice.")
            self.destroy()
            return
        
        hdr = data["header"]
        idk = hdr["idKontakt"]
        idK = int(idk) if idk is not None else None
        # pronađi naziv:
        name_k = None
        for k in self.kontakti:
            if k.idKontakt == idK:
                name_k = k.naziv; break
        if name_k:
            self.kontakt_var.set(name_k)

        # datum (YYYY-MM-DD -> widget)
        iso = hdr["datumIsporuke"]
        try:
            if _HAS_CAL:
                d = datetime.strptime(iso, "%Y-%m-%d").date()
                self.w_dat.set_date(d)
            else:
                self.w_dat.delete(0, END)
                self.w_dat.insert(0, datetime.strptime(iso, "%Y-%m-%d").strftime("%d.%m.%Y"))
        except:
            pass

        self.e_broj.delete(0, END); self.e_broj.insert(0, hdr["brojOtpremnice"] or "")

        # stavke
        self._lines.clear()
        for it in data["stavke"]:
            naziv = it["proizvod"]
            qty = int(it["kolicina"])
            cij = it["cijena"]  # može biti None
            self._lines.append((naziv, qty, (None if cij is None else float(cij))))
        self._refresh_tv()

    def _refresh_tv(self):
        self.tv.delete(*self.tv.get_children())
        for naziv, qty, cij in self._lines:
            cij_txt = "" if cij is None else f"{cij:.2f}"
            self.tv.insert("", "end", values=(naziv, qty, cij_txt))

    def _on_pick_line(self, _event=None):
        sel = self.tv.selection()
        if not sel: return
        naziv, qty, cij_txt = self.tv.item(sel[0], "values")
        self.proizvod_var.set(naziv)
        self.e_qty.delete(0, END); self.e_qty.insert(0, qty)
        self.e_cij.delete(0, END); self.e_cij.insert(0, cij_txt)

    def _add_or_update_line(self):
        name = (self.proizvod_var.get() or "").strip()
        if not name or name not in self.proizvod_id_by_name:
            messagebox.showwarning("Upozorenje", "Odaberite proizvod.")
            return
        try:
            qty = int((self.e_qty.get() or "0").strip())
            if qty <= 0: raise ValueError
        except:
            messagebox.showwarning("Upozorenje", "Količina mora biti pozitivan cijeli broj.")
            return
        cij_s = (self.e_cij.get() or "").strip()
        cij = None if cij_s == "" else float(cij_s.replace(",", "."))

        # ako već postoji isti proizvod -> zamijeni
        replaced = False
        for i, (n, _, _) in enumerate(self._lines):
            if n == name:
                self._lines[i] = (name, qty, cij)
                replaced = True
                break
        if not replaced:
            self._lines.append((name, qty, cij))
        self._refresh_tv()

    def _remove_line(self):
        sel = self.tv.selection()
        if not sel: return
        naziv, *_ = self.tv.item(sel[0], "values")
        self._lines = [t for t in self._lines if t[0] != naziv]
        self._refresh_tv()

    def _clear_lines(self):
        if messagebox.askyesno("Potvrda", "Ukloniti sve stavke?"):
            self._lines.clear()
            self._refresh_tv()

    def _save(self):
        # validacija headera
        name_k = (self.kontakt_var.get() or "").strip()
        if not name_k or name_k not in self.kontakt_id_by_name:
            messagebox.showwarning("Upozorenje", "Odaberi kontakt.")
            return
        if not self._lines:
            messagebox.showwarning("Upozorenje", "Dodaj barem jednu stavku.")
            return

        idKontakt = self.kontakt_id_by_name[name_k]
        # datum -> ISO
        if _HAS_CAL:
            d = self.w_dat.get_date()
            iso = d.strftime("%Y-%m-%d")
        else:
            iso = datetime.strptime(self.w_dat.get().strip(), "%d.%m.%Y").strftime("%Y-%m-%d")
        broj = (self.e_broj.get() or "").strip()

        # mapiraj nazive u (idProizvod, qty, cijena)
        stavke = []
        for naziv, qty, cij in self._lines:
            pid = self.proizvod_id_by_name[naziv]
            stavke.append((pid, qty, cij))

        try:
            update_otpremnica_full(self.idOt, idKontakt, iso, broj, stavke)
            messagebox.showinfo("OK", "Otpremnica je ažurirana.")
            if self.on_saved:
                self.on_saved()
            self.destroy()
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