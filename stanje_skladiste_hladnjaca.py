from repo_stanje import fetch_stanje_hladnjaca
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import Combobox

def provjeri_stanje_hladnjaca(window):
    frame = Frame(window, bg='white', width=800, height=600)
    frame.place(x=0, y=0)

    Label(frame, text="Stanje – Hladnjača ",
          bg='blue', fg='white', font=("times new roman", 20, "bold")).place(x=0, y=0, relwidth=1, height=50)
    Button(frame, text="Natrag", command=frame.destroy).place(x=10, y=10)

    # Search bar
    search_frame = Frame(frame, bg='white')
    search_frame.place(x=10, y=60, width=780, height=40)

    Label(search_frame, text="Pretraži naziv:", bg='white').grid(row=0, column=0, padx=6)
    term_var = StringVar()
    Entry(search_frame, textvariable=term_var, width=30).grid(row=0, column=1, padx=6)

    exclude_var = BooleanVar(value=True)
    Checkbutton(search_frame, text="Isključi 'Kiseli kupus' artikle",
                variable=exclude_var, bg='white').grid(row=0, column=2, padx=12)

    # Treeview
    tv_container = Frame(frame, bg='white')
    tv_container.place(x=10, y=110, width=780, height=420)

    cols = ("naziv","jm","stanje","cijena")
    tv = ttk.Treeview(tv_container, columns=cols, show='headings')
    tv.pack(side='left', fill='both', expand=True)

    vs = Scrollbar(tv_container, orient=VERTICAL, command=tv.yview)
    vs.pack(side=RIGHT, fill=Y)
    tv.configure(yscrollcommand=vs.set)

    tv.heading("naziv", text="Naziv")
    tv.heading("jm", text="JM")
    tv.heading("stanje", text="Stanje")
    tv.heading("cijena", text="Cijena")

    tv.column("naziv", width=350)
    tv.column("jm", width=70, anchor='center')
    tv.column("stanje", width=130, anchor='e')
    tv.column("cijena", width=130, anchor='e')

    tv.tag_configure("neg", background="#ffe5e5")  # stanje <= 0

    # Summary (brojač)
    summary = Label(frame, text="", anchor='w', bg='white', font=("times new roman", 12, "bold"))
    summary.place(x=10, y=540, width=780, height=30)

    def load_data():
        rows = fetch_stanje_hladnjaca(term=term_var.get().strip(),
                                      exclude_kupus=exclude_var.get())
        tv.delete(*tv.get_children())

        broj_artikala = 0
        for r in rows:
            naziv = r["naziv"]
            jm = r["jm"]
            stanje = r["stanje"] if r["stanje"] is not None else 0
            cijena = r["cijena"]
            cijena_txt = "" if cijena is None else f"{cijena:.2f}"

            tags = ("neg",) if (stanje is None or stanje <= 0) else ()
            tv.insert("", "end", values=(naziv, jm, stanje, cijena_txt), tags=tags)

            broj_artikala += 1

        summary.config(text=f"Artikala: {broj_artikala}")

    # gumbi search/reset
    Button(search_frame, text="Traži", command=load_data).grid(row=0, column=3, padx=6)
    Button(search_frame, text="Reset", command=lambda: (term_var.set(""), load_data())).grid(row=0, column=4, padx=6)

    load_data()