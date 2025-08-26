from db import get_conn
from mysql.connector import Error as MySQLError

def fetch_svi_kontakti(term: str | None = None):
    """
    Vraća listu dict-ova: idKontakt, naziv, OIB, adresa, kontaktOsoba, telefon
    Ako je term zadan, filtrira po nazivu (LIKE).
    """
    sql = """
    SELECT idKontakt, naziv, OIB, adresa, kontaktOsoba, telefon
    FROM Kontakt
    """
    params = []
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

def create_kontakt(naziv: str, oib: str | int | None, adresa: str | None,
                   kontakt_osoba: str | None, telefon: str | None) -> int:
    """
    Umeće novi kontakt. OIB očekujemo kao 11-znamenkasti (HR OIB),
    ali nije obvezan — može biti NULL.
    Vraća id novog kontakta.
    """
    # osnovne provjere
    naziv = (naziv or "").strip()
    if not naziv:
        raise ValueError("Naziv je obavezan.")

    # OIB: ako je zadan, mora biti 11 znamenki
    if oib is not None and str(oib).strip() != "":
        s = str(oib).strip()
        if not s.isdigit() or len(s) != 11:
            raise ValueError("OIB mora imati 11 znamenki (ili ostavi prazno).")
        oib_val = int(s)
    else:
        oib_val = None

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Kontakt (naziv, OIB, adresa, kontaktOsoba, telefon)
                VALUES (%s, %s, %s, %s, %s)
            """, (naziv, oib_val, adresa, kontakt_osoba, telefon))
            conn.commit()
            return cur.lastrowid  # AUTO_INCREMENT idKontakt
    except MySQLError:
        conn.rollback()
        raise
    finally:
        conn.close()

def update_kontakt(idKontakt: int, naziv: str, oib: str | int | None,
                   adresa: str | None, kontakt_osoba: str | None, telefon: str | None):
    naziv = (naziv or "").strip()
    if not naziv:
        raise ValueError("Naziv je obavezan.")

    s = (str(oib).strip() if oib is not None else "")
    if s == "":
        oib_val = None
    else:
        if not s.isdigit() or len(s) != 11:
            raise ValueError("OIB mora imati 11 znamenki (ili ostavi prazno).")
        oib_val = s  

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Kontakt
                   SET naziv=%s, OIB=%s, adresa=%s, kontaktOsoba=%s, telefon=%s
                 WHERE idKontakt=%s
            """, (naziv, oib_val, adresa, kontakt_osoba, telefon, idKontakt))
            conn.commit()
    except MySQLError:
        conn.rollback()
        raise
    finally:
        conn.close()

def delete_kontakt(idKontakt: int):
    """
    Briše kontakt. Ako je vezan FK-om (npr. u Otpremnica/Narudzba), MySQL će baciti grešku.
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Kontakt WHERE idKontakt=%s", (idKontakt,))
            conn.commit()
    except MySQLError as e:
        conn.rollback()
        # 1451 = Cannot delete or update a parent row: a foreign key constraint fails
        if getattr(e, "errno", None) == 1451:
            raise ValueError("Kontakt je povezan s dokumentima (narudžbe/otpremnice) i ne može se obrisati.")
        raise
    finally:
        conn.close()