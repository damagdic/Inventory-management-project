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

            # 2) STAVKE + update stanja
            for idProizvod, kolicina in stavke:
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

def update_narudzba_i_detalj(row_id: int, idNarudzba: int,
                             new_idKontakt: int,
                             new_idProizvod: int,
                             new_kolicina: int,
                             new_datumNarudzbe: str,
                             new_datumPrimitka: str):
    """
    row_id = idDetaljiNarudzbe
    datumi: 'YYYY-MM-DD'
    """
    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            # dohvat starog detalja
            cur.execute("""
                SELECT idProizvod, kolicina
                FROM DetaljiNarudzbe
                WHERE idDetaljiNarudzbe=%s
                FOR UPDATE
            """, (row_id,))
            old = cur.fetchone()
            if not old:
                raise Exception("Detalj narudžbe ne postoji.")
            old_prod = old["idProizvod"]
            old_qty  = old["kolicina"]

            # ako se mijenja proizvod ili količina -> ispravi zalihe
            if old_prod != new_idProizvod:
                # vrati staru količinu starom proizvodu -
                cur.execute("UPDATE Proizvod SET StanjeNaSkladistu = StanjeNaSkladistu - %s WHERE idProizvod=%s",
                            (old_qty, old_prod))
                # dodaj novu količinu novom proizvodu +
                cur.execute("UPDATE Proizvod SET StanjeNaSkladistu = StanjeNaSkladistu + %s WHERE idProizvod=%s",
                            (new_kolicina, new_idProizvod))
            else:
                # isti proizvod -> korigiraj razlikom
                delta = new_kolicina - old_qty
                if delta != 0:
                    cur.execute("UPDATE Proizvod SET StanjeNaSkladistu = StanjeNaSkladistu + %s WHERE idProizvod=%s",
                                (delta, new_idProizvod))

            # update detalja
            cur.execute("""
                UPDATE DetaljiNarudzbe
                SET idProizvod=%s, kolicina=%s
                WHERE idDetaljiNarudzbe=%s
            """, (new_idProizvod, new_kolicina, row_id))

            # update zaglavlja (kontakt + datumi)
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