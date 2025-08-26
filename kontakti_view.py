from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox
from repo_kontakti import fetch_svi_kontakti, create_kontakt, update_kontakt, delete_kontakt

def kontakti_screen(window):
    frame = Frame(window, bg='white', width=800, height=600)
    frame.place(x=0, y=0)

    Label(frame, text="Kontakti", bg='blue', fg='white',
          font=("times new roman", 20, "bold")).place(x=0, y=0, relwidth=1, height=50)

    Button(frame, text="Natrag", command=frame.destroy).place(x=10, y=10)

    left = Frame(frame, bg='white'); left.place(x=10, y=60, width=360, height=520)

    Label(left, text="Dodaj novi kontakt", bg='white',
          font=("times new roman", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,10), sticky='w')

    Label(left, text="Naziv*", bg='white').grid(row=1, column=0, sticky='e', padx=6, pady=4)
    e_naziv = Entry(left, width=30); e_naziv.grid(row=1, column=1, sticky='w', padx=6, pady=4)

    Label(left, text="OIB", bg='white').grid(row=2, column=0, sticky='e', padx=6, pady=4)
    e_oib = Entry(left, width=30); e_oib.grid(row=2, column=1, sticky='w', padx=6, pady=4)

    Label(left, text="Adresa", bg='white').grid(row=3, column=0, sticky='e', padx=6, pady=4)
    e_adresa = Entry(left, width=30); e_adresa.grid(row=3, column=1, sticky='w', padx=6, pady=4)

    Label(left, text="Kontakt osoba", bg='white').grid(row=4, column=0, sticky='e', padx=6, pady=4)
    e_kosoba = Entry(left, width=30); e_kosoba.grid(row=4, column=1, sticky='w', padx=6, pady=4)

    Label(left, text="Telefon", bg='white').grid(row=5, column=0, sticky='e', padx=6, pady=4)
    e_telefon = Entry(left, width=30); e_telefon.grid(row=5, column=1, sticky='w', padx=6, pady=4)

    def on_save():
        try:
            new_id = create_kontakt(
                naziv=e_naziv.get(),
                oib=e_oib.get(),
                adresa=e_adresa.get(),
                kontakt_osoba=e_kosoba.get(),
                telefon=e_telefon.get()
            )
            messagebox.showinfo("OK", f"Kontakt dodan (ID: {new_id}).")
            e_naziv.delete(0, END); e_oib.delete(0, END)
            e_adresa.delete(0, END); e_kosoba.delete(0, END); e_telefon.delete(0, END)
            load_list()
        except Exception as e:
            messagebox.showerror("Greška", str(e))
    
    def on_update():
        if selected_id["value"] is None:
            messagebox.showwarning("Upozorenje", "Najprije odaberite kontakt iz liste.")
            return
        try:
            update_kontakt(
                idKontakt=selected_id["value"],
                naziv=e_naziv.get(),
                oib=e_oib.get(),
                adresa=e_adresa.get(),
                kontakt_osoba=e_kosoba.get(),
                telefon=e_telefon.get()
            )
            messagebox.showinfo("OK", "Kontakt ažuriran.")
            load_list()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def on_delete():
        if selected_id["value"] is None:
            messagebox.showwarning("Upozorenje", "Odaberite kontakt za brisanje.")
            return
        if not messagebox.askyesno("Potvrda", "Obrisati odabrani kontakt?"):
            return
        try:
            delete_kontakt(selected_id["value"])
            messagebox.showinfo("OK", "Kontakt obrisan.")
            for ent in (e_naziv, e_oib, e_adresa, e_kosoba, e_telefon):
                ent.delete(0, END)
            selected_id["value"] = None
            load_list()
        except Exception as e:
            messagebox.showerror("Greška", str(e))
    
    def on_update():
        if selected_id["value"] is None:
            messagebox.showwarning("Upozorenje", "Najprije odaberite kontakt iz liste.")
            return
        try:
            update_kontakt(
                idKontakt=selected_id["value"],
                naziv=e_naziv.get(),
                oib=e_oib.get(),
                adresa=e_adresa.get(),
                kontakt_osoba=e_kosoba.get(),
                telefon=e_telefon.get()
            )
            messagebox.showinfo("OK", "Kontakt ažuriran.")
            load_list()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def on_delete():
        if selected_id["value"] is None:
            messagebox.showwarning("Upozorenje", "Odaberite kontakt za brisanje.")
            return
        if not messagebox.askyesno("Potvrda", "Obrisati odabrani kontakt?"):
            return
        try:
            delete_kontakt(selected_id["value"])
            messagebox.showinfo("OK", "Kontakt obrisan.")
            for ent in (e_naziv, e_oib, e_adresa, e_kosoba, e_telefon):
                ent.delete(0, END)
            selected_id["value"] = None
            load_list()
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    Button(left, text="Spremi", command=on_save).grid(row=6, column=0, columnspan=2, pady=10)

    right = Frame(frame, bg='white'); right.place(x=380, y=60, width=410, height=520)

    search = Frame(right, bg='white'); search.pack(fill='x')
    Label(search, text="Traži (naziv):", bg='white').pack(side='left', padx=6)
    term_var = StringVar()
    Entry(search, textvariable=term_var, width=25).pack(side='left', padx=6)

    def do_search():
        load_list(term_var.get().strip())

    Button(search, text="Traži", command=do_search).pack(side='left', padx=6)
    Button(search, text="Reset", command=lambda: (term_var.set(""), load_list())).pack(side='left', padx=6)

    btn_row = Frame(left, bg='white'); btn_row.grid(row=7, column=0, columnspan=2, pady=8)
    Button(btn_row, text="Spremi novi", command=on_save).pack(side='left', padx=4)
    Button(btn_row, text="Ažuriraj odabrani", command=on_update).pack(side='left', padx=4)
    Button(btn_row, text="Obriši odabrani", command=on_delete).pack(side='left', padx=4)

    tv_container = Frame(right, bg='white')
    tv_container.pack(fill='both', expand=True, padx=6, pady=6)

    tv = ttk.Treeview(tv_container, columns=("id","naziv","oib","adresa","kontakt","telefon"),
                    show='headings')
    tv.pack(side='left', fill='both', expand=True)

    vs = Scrollbar(tv_container, orient=VERTICAL, command=tv.yview)
    vs.pack(side='right', fill=Y)

    tv.configure(yscrollcommand=vs.set)

    for col, title, w, anc in [
        ("id","ID",10,'e'), ("naziv","Naziv",60,'w'), ("oib","OIB",70,'e'),
        ("adresa","Adresa",100,'w'), ("kontakt","Kontakt osoba",50,'w'),
        ("telefon","Telefon",60,'w')
    ]:
        tv.heading(col, text=title)
        tv.column(col, width=w, anchor=anc)

    def load_list(term: str | None = None):
        tv.delete(*tv.get_children())
        rows = fetch_svi_kontakti(term=term)
        for r in rows:
            tv.insert("", "end", values=(
                r["idKontakt"], r["naziv"], r["OIB"], r["adresa"], r["kontaktOsoba"], r["telefon"]
            ))


    load_list()

    selected_id = {"value": None} 

    def on_select(event=None):
        sel = tv.selection()
        if not sel:
            selected_id["value"] = None
            return
        vals = tv.item(sel[0], "values")
        # redoslijed: id, naziv, oib, adresa, kontakt, telefon
        _id, naziv, oib, adresa, kontakt, telefon = vals
        selected_id["value"] = int(_id)
        e_naziv.delete(0, END); e_naziv.insert(0, naziv or "")
        e_oib.delete(0, END);   e_oib.insert(0, "" if oib in (None, "None") else str(oib))
        e_adresa.delete(0, END); e_adresa.insert(0, adresa or "")
        e_kosoba.delete(0, END); e_kosoba.insert(0, kontakt or "")
        e_telefon.delete(0, END); e_telefon.insert(0, telefon or "")

    tv.bind("<<TreeviewSelect>>", on_select)
