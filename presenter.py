# service.py
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any
from datetime import date
from model import get_conn

# -----------------------------
# Pomoćni dohvat za comboboxe/listinge
# -----------------------------

def fetch_kontakti(term: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT idKontakt, naziv FROM Kontakt"
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


def fetch_proizvodi(term: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT idProizvod, naziv FROM Proizvod"
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


def create_kontakt(naziv: str, oib: Optional[str], adresa: Optional[str],
                   kontakt_osoba: Optional[str], telefon: Optional[str]) -> int:
    naziv = (naziv or "").strip()
    if not naziv:
        raise ValueError("Naziv je obavezan.")
    oib_val = (oib or "").strip() or None  # kolona OIB neka bude CHAR(11) NULL
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Kontakt (naziv, OIB, adresa, kontaktOsoba, telefon)
                VALUES (%s, %s, %s, %s, %s)
            """, (naziv, oib_val, adresa, kontakt_osoba, telefon))
            conn.commit()
            return cur.lastrowid
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_kontakt(idKontakt: int, naziv: str, oib: Optional[str],
                   adresa: Optional[str], kontakt_osoba: Optional[str],
                   telefon: Optional[str]) -> None:
    naziv = (naziv or "").strip()
    if not naziv:
        raise ValueError("Naziv je obavezan.")
    oib_val = (oib or "").strip() or None
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Kontakt
                   SET naziv=%s, OIB=%s, adresa=%s, kontaktOsoba=%s, telefon=%s
                 WHERE idKontakt=%s
            """, (naziv, oib_val, adresa, kontakt_osoba, telefon, idKontakt))
            conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_kontakt(idKontakt: int) -> None:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Kontakt WHERE idKontakt=%s", (idKontakt,))
            conn.commit()
    except Exception as e:
        conn.rollback()
        # 1451 = Cannot delete or update a parent row (FK)
        if getattr(e, "errno", None) == 1451:
            raise ValueError("Kontakt je povezan s dokumentima (narudžbe/otpremnice) i ne može se obrisati.")
        raise
    finally:
        conn.close()

# -----------------------------
# ULAZ – Narudzba + DetaljiNarudzbe
# -----------------------------

def create_ulaz(
    idKontakt: int,
    datumNarudzbe: str,      # 'YYYY-MM-DD'
    datumPrimitka: str,      # 'YYYY-MM-DD'
    stavke: List[Tuple[int, int]],   # [(idProizvod, kolicina), ...]
) -> int:
    """
    Trigeri na DetaljiNarudzbe rade +stanje.
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Narudzba (idKontakt, datumNarudzbe, datumPrimitka)
                VALUES (%s, %s, %s)
            """, (idKontakt, datumNarudzbe, datumPrimitka))
            idNar = cur.lastrowid
            for pid, qty in stavke:
                cur.execute("""
                    INSERT INTO DetaljiNarudzbe (idNarudzba, idProizvod, kolicina)
                    VALUES (%s, %s, %s)
                """, (idNar, pid, qty))
        conn.commit()
        return idNar
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_ulaz(
    row_id: int,               # idDetaljiNarudzbe
    idNarudzba: int,
    new_idKontakt: int,
    new_idProizvod: int,
    new_kolicina: int,
    new_datumNarudzbe: str,    # 'YYYY-MM-DD'
    new_datumPrimitka: str,    # 'YYYY-MM-DD'
) -> None:
    """
    Trigeri na DetaljiNarudzbe koregiraju zalihe (delta/promjena proizvoda).
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE DetaljiNarudzbe
                   SET idProizvod=%s, kolicina=%s
                 WHERE idDetaljiNarudzbe=%s
            """, (new_idProizvod, new_kolicina, row_id))
            cur.execute("""
                UPDATE Narudzba
                   SET idKontakt=%s, datumNarudzbe=%s, datumPrimitka=%s
                 WHERE idNarudzba=%s
            """, (new_idKontakt, new_datumNarudzbe, new_datumPrimitka, idNarudzba))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


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
        DATE_FORMAT(n.datumPrimitka, '%%d.%%m.%%Y') AS datum_primitka
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
) -> int:
    """
    datumOtpremnice se automatski stavlja na današnji datum.
    Trigeri na DetaljiOtpremnice rade -stanje i blokiraju minus.
    """
    # (opcionalno) prije-insert provjera da izbjegnemo ružnu DB grešku
    for pid, qty, _ in stavke:
        if not _can_issue(pid, qty):
            raise ValueError("Nedovoljno na skladištu za neke stavke.")

    today = date.today().strftime("%Y-%m-%d")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Otpremnica (idKontakt, datumOtpremnice, datumIsporuke, brojOtpremnice)
                VALUES (%s, %s, %s, %s)
            """, (idKontakt, today, datumIsporuke, brojOtpremnice))
            idOt = cur.lastrowid
            for pid, qty, cij in stavke:
                cur.execute("""
                    INSERT INTO DetaljiOtpremnice (idOtpremnica, idProizvod, kolicina, cijena)
                    VALUES (%s, %s, %s, %s)
                """, (idOt, pid, qty, cij))
        conn.commit()
        return idOt
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


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
    Trigeri na DetaljiOtpremnice koregiraju zalihe (delta/promjena proizvoda).
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # zaglavlje najprije (datumOtpremnice ostaje kakav jest)
            cur.execute("""
                UPDATE Otpremnica
                   SET idKontakt=%s, datumIsporuke=%s, brojOtpremnice=%s
                 WHERE idOtpremnica=%s
            """, (new_idKontakt, new_datumIsporuke, new_brojOtpremnice, idOtpremnica))
            # detalj
            cur.execute("""
                UPDATE DetaljiOtpremnice
                   SET idProizvod=%s, kolicina=%s
                 WHERE idDetaljiOtpremnice=%s
            """, (new_idProizvod, new_kolicina, row_id))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


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
        DATE_FORMAT(o.datumIsporuke, '%%d.%%m.%%Y') AS datum_isporuke
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
