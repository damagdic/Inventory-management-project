from db import get_conn

def fetch_kontakti():
    """Za puniti combobox (id, naziv)."""
    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT idKontakt, naziv FROM Kontakt ORDER BY naziv")
            return cur.fetchall()
    finally:
        conn.close()

def fetch_proizvodi():
    """Za puniti combobox (id, naziv)."""
    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT idProizvod, naziv FROM Proizvod ORDER BY naziv")
            return cur.fetchall()
    finally:
        conn.close()

def _next_id(conn, table: str, id_col: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COALESCE(MAX({id_col}), 0) + 1 FROM {table}")
        return cur.fetchone()[0]

def create_narudzba_s_stavkama(idKontakt: int, datumNarudzbe: str, datumPrimitka: str,
                                stavke: list[tuple[int, int]]):
    """
    stavke = [(idProizvod, kolicina), ...]
    datumi: 'YYYY-MM-DD'
    Vraća: idNarudzba
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 1) zaglavlje
            idNarudzba = _next_id(conn, "Narudzba", "idNarudzba")
            cur.execute("""
                INSERT INTO Narudzba (idNarudzba, idKontakt, datumNarudzbe, datumPrimitka)
                VALUES (%s, %s, %s, %s)
            """, (idNarudzba, idKontakt, datumNarudzbe, datumPrimitka))

            # 2) STAVKE + update stanja (JEDNA PETLJA!)
            for idProizvod, kolicina in stavke:
                # detalj
                idDetalj = _next_id(conn, "DetaljiNarudzbe", "idDetaljiNarudzbe")
                cur.execute("""
                    INSERT INTO DetaljiNarudzbe (idDetaljiNarudzbe, idNarudzba, idProizvod, kolicina)
                    VALUES (%s, %s, %s, %s)
                """, (idDetalj, idNarudzba, idProizvod, kolicina))

                # zaključaj proizvod dok ažuriraš stanje
                cur.execute("SELECT StanjeNaSkladistu FROM Proizvod WHERE idProizvod=%s FOR UPDATE", (idProizvod,))
                row = cur.fetchone()
                if not row:
                    raise Exception(f"Proizvod {idProizvod} ne postoji.")

                # update stanja (+ ulaz)
                cur.execute("""
                    UPDATE Proizvod
                    SET StanjeNaSkladistu = StanjeNaSkladistu + %s
                    WHERE idProizvod = %s
                """, (kolicina, idProizvod))

        conn.commit()
        return idNarudzba
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
