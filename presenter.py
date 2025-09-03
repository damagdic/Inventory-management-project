# service.py
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any
from datetime import date
from model import (
    get_conn,
    Kontakt, Proizvod,
    Narudzba, DetaljiNarudzbe,
    Otpremnica, DetaljiOtpremnice,
)

# -----------------------------
# Pomoćni dohvat za comboboxe/listinge
# -----------------------------

def fetch_kontakti(term: Optional[str] = None) -> List[Kontakt]:
    sql = "SELECT idKontakt, naziv, OIB, adresa, kontaktOsoba, telefon FROM Kontakt"
    params: list[Any] = []
    if term:
        sql += " WHERE naziv LIKE %s"
        params.append(f"%{term}%")
    sql += " ORDER BY naziv"

    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        result: List[Kontakt] = []
        for r in rows:
            result.append(Kontakt(
                idKontakt=r['idKontakt'],
                naziv=r['naziv'],
                OIB=r['OIB'],
                adresa=r['adresa'],
                kontaktOsoba=r['kontaktOsoba'],
                telefon=r['telefon']
            ))
        return result
    finally:
        conn.close()


def fetch_proizvodi(term: Optional[str] = None) -> List[Proizvod]:
    sql = "SELECT idProizvod, naziv, idJedinicaMjere FROM Proizvod"
    params: list[Any] = []
    if term:
        sql += " WHERE naziv LIKE %s"
        params.append(f"%{term}%")
    sql += " ORDER BY naziv"
    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [Proizvod(idProizvod=r['idProizvod'], naziv=r['naziv'], idJedinicaMjere=r['idJedinicaMjere']) for r in rows]   
    finally:
        conn.close()

# -----------------------------
# KONTAKTI – CRUD
# -----------------------------

def list_kontakti(term: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT idKontakt, naziv, OIB, adresa, kontaktOsoba, telefon FROM Kontakt"
    params: list[Any] = []
    if term:
        sql += " WHERE naziv LIKE %s"
        params.append(f"%{term}%")
    sql += " ORDER BY naziv"
    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def create_kontakt(naziv: str, oib: Optional[str],
                   adresa: Optional[str], kontakt_osoba: Optional[str],
                   telefon: Optional[str]) -> int:
    k = Kontakt(idKontakt=None, naziv=naziv, OIB=oib, adresa=adresa,
                kontaktOsoba=kontakt_osoba, telefon=telefon)
    return k.save()
     

def update_kontakt(idKontakt: int, naziv: str, oib: Optional[str],
                   adresa: Optional[str], kontakt_osoba: Optional[str],
                   telefon: Optional[str]) -> None:
    k = Kontakt.get(idKontakt)
    if not k:
        raise ValueError("Kontakt ne postoji.")
    k.naziv = naziv
    k.OIB = oib
    k.adresa = adresa
    k.kontaktOsoba = kontakt_osoba
    k.telefon = telefon
    k.save()


def delete_kontakt(idKontakt: int) -> None:
    k = Kontakt.get(idKontakt)
    if not k:
        return
    k.delete()

# -----------------------------
# ULAZ – Narudzba + DetaljiNarudzbe
# -----------------------------

def create_ulaz(
    idKontakt: int,
    datumNarudzbe: str,      # 'YYYY-MM-DD'
    datumPrimitka: str,      # 'YYYY-MM-DD'
    stavke: List[Tuple[int, int]],   # [(idProizvod, kolicina), ...]
) -> Narudzba:
    """
    Trigeri na DetaljiNarudzbe rade +stanje.
    """
    n = Narudzba(idNarudzba=None, idKontakt=idKontakt, datumNarudzbe=datumNarudzbe, datumPrimitka=datumPrimitka)
    n.save()
    for pid, qty in stavke:
        det = DetaljiNarudzbe(
            idDetaljiNarudzbe=None,
            idNarudzba=n.idNarudzba,
            idProizvod=pid,
            kolicina=qty
        )
        det.save()  

    return n


def update_ulaz(
    row_id: int,               # idDetaljiNarudzbe
    idNarudzba: int,
    new_idKontakt: int,
    new_idProizvod: int,
    new_kolicina: int,
    new_datumNarudzbe: str,    # 'YYYY-MM-DD'
    new_datumPrimitka: str,    # 'YYYY-MM-DD'
) -> None:
    det = DetaljiNarudzbe.get(row_id)
    det.idProizvod = new_idProizvod
    det.kolicina = new_kolicina
    det.save()

    n = Narudzba.get(idNarudzba)
    if not n:
        raise ValueError("Narudzba ne postoji.")
    n.idKontakt = new_idKontakt
    n.datumNarudzbe = new_datumNarudzbe
    n.datumPrimitka = new_datumPrimitka
    n.save()


def fetch_ulazi(limit: int = 200) -> List[Dict[str, Any]]:
    sql = """
    SELECT
        dn.idDetaljiNarudzbe AS row_id,
        n.idNarudzba,
        n.idKontakt,
        dn.idProizvod,
        k.naziv AS kontakt,
        p.naziv AS proizvod,
        dn.kolicina AS kolicina,
        DATE_FORMAT(n.datumPrimitka, '%d.%m.%Y') AS datum_primitka,
    FROM DetaljiNarudzbe dn
    JOIN Narudzba  n ON n.idNarudzba = dn.idNarudzba
    JOIN Proizvod  p ON p.idProizvod = dn.idProizvod
    JOIN Kontakt   k ON k.idKontakt  = n.idKontakt
    ORDER BY n.idNarudzba DESC, dn.idDetaljiNarudzbe DESC
    LIMIT %s
    """
    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()
    finally:
        conn.close()

# -----------------------------
# IZLAZ – Otpremnica + DetaljiOtpremnice
# -----------------------------

def _can_issue(pid: int, qty: int) -> bool:
    """
    Brza provjera stanja (triger će svakako štititi).
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT StanjeNaSkladistu FROM Proizvod WHERE idProizvod=%s", (pid,))
            row = cur.fetchone()
            if not row: return False
            return (row[0] or 0) >= qty
    finally:
        conn.close()


def create_izlaz(
    idKontakt: int,
    datumIsporuke: str,             # 'YYYY-MM-DD'
    brojOtpremnice: str,
    stavke: List[Tuple[int, int, Optional[float]]],   # [(idProizvod, kolicina, cijena_kom or None), ...]
) -> Otpremnica:
    """
    Kreira otpremnicu i detaljeotpremnice objektno
    Triggeri rade -stanje i blokiraju minus
    """

    for pid, qty, _ in stavke:
        if not _can_issue(pid, qty):
            raise ValueError("Nedovoljno na skladištu za neke stavke.")

    today = date.today().strftime("%Y-%m-%d")
    
    ot = Otpremnica(idOtpremnica=None, idKontakt=idKontakt, datumOtpremnice=today, datumIsporuke=datumIsporuke, brojOtpremnice=brojOtpremnice)
    ot.save()
    for pid, qty, cij in stavke:
        det = DetaljiOtpremnice(idDetaljiOtpremnice=None, idOtpremnica=ot.idOtpremnica, idProizvod=pid, kolicina=qty, cijena=cij)
        det.save()
    return ot


def update_izlaz(
    row_id: int,              # idDetaljiOtpremnice
    idOtpremnica: int,
    new_idKontakt: int,
    new_idProizvod: int,
    new_kolicina: int,
    new_datumIsporuke: str,   # 'YYYY-MM-DD'
    new_brojOtpremnice: str,
) -> None:
    """
    Ažurira Otpremnicu i DetaljiOtpremnice
    Trigeri na DetaljiOtpremnice korigiraju zalihe
    """
    det = DetaljiOtpremnice.get(row_id)
    if det.idProizvod == new_idProizvod:
        delta = new_kolicina - det.kolicina
        if delta > 0 and not _can_issue(new_idProizvod, delta):
            raise ValueError("Nedovoljno na skladištu za povećanje količine.")
    else:
        if not _can_issue(new_idProizvod, new_kolicina):
            raise ValueError("Nedovoljno na skladištu za odabrani proizvod.")
    det.idProizvod = new_idProizvod
    det.kolicina = new_kolicina
    det.save()

    n = Otpremnica.get(idOtpremnica)
    if not n:
        raise ValueError("Otpremnica ne postoji.")
    n.idKontakt = new_idKontakt
    n.datumIsporuke = new_datumIsporuke
    n.brojOtpremnice = new_brojOtpremnice
    n.save()


def fetch_izlazi(limit: int = 200) -> List[Dict[str, Any]]:
    sql = """
    SELECT
        doo.idDetaljiOtpremnice AS row_id,
        o.idOtpremnica,
        o.idKontakt,
        doo.idProizvod,
        k.naziv AS kontakt,
        p.naziv AS proizvod,
        doo.kolicina AS kolicina,
        o.brojOtpremnice AS broj_otpremnice,
        DATE_FORMAT(o.datumIsporuke, '%d.%m.%Y') AS datum_isporuke
    FROM DetaljiOtpremnice doo
    JOIN Otpremnica o ON o.idOtpremnica = doo.idOtpremnica
    JOIN Proizvod  p ON p.idProizvod   = doo.idProizvod
    JOIN Kontakt   k ON k.idKontakt    = o.idKontakt
    ORDER BY o.idOtpremnica DESC, doo.idDetaljiOtpremnice DESC
    LIMIT %s
    """
    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()
    finally:
        conn.close()

# -----------------------------
# STANJE – pregled
# -----------------------------

def fetch_stanje(term: Optional[str] = None, exclude_kupus: bool = True) -> List[Dict[str, Any]]:
    sql = """
    SELECT
      p.idProizvod,
      p.naziv,
      jm.oznaka AS jm,
      p.StanjeNaSkladistu AS stanje,
      p.cijena
    FROM Proizvod p
    JOIN JedinicaMjere jm ON jm.idJedinicaMjere = p.idJedinicaMjere
    """
    where, params = [], []
    if exclude_kupus:
        where.append("(p.naziv NOT LIKE 'Kiseli kupus%%' AND p.naziv <> 'Kisela repa')")
    if term:
        where.append("p.naziv LIKE %s"); params.append(f"%{term}%")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY p.naziv"

    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()
