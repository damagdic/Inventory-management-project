from db import get_conn

def _next_id(conn, table: str, id_col: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COALESCE(MAX({id_col}), 0) + 1 FROM {table}")
        return cur.fetchone()[0]

def create_otpremnica_s_stavkama(idKontakt: int, datumOtpremnice: str, datumIsporuke: str,
                                 brojOtpremnice: str, stavke: list[tuple[int, int]]):
    """
    stavke = [(idProizvod, kolicina), ...]
    datumi: 'YYYY-MM-DD'
    Smanjuje Proizvod.StanjeNaSkladistu za svaku stavku.
    Vraća idOtpremnica.
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            idOtpremnica = _next_id(conn, "Otpremnica", "idOtpremnica")
            cur.execute("""
                INSERT INTO Otpremnica (idOtpremnica, idKontakt, datumOtpremnice, datumIsporuke, brojOtpremnice)
                VALUES (%s, %s, %s, %s, %s)
            """, (idOtpremnica, idKontakt, datumOtpremnice, datumIsporuke, brojOtpremnice))

            for idProizvod, kolicina in stavke:
                idDetalj = _next_id(conn, "DetaljiOtpremnice", "idDetaljiOtpremnice")
                cur.execute("""
                    INSERT INTO DetaljiOtpremnice (idDetaljiOtpremnice, idOtpremnica, idProizvod, kolicina, cijena)
                    VALUES (%s, %s, %s, %s, 0)
                """, (idDetalj, idOtpremnica, idProizvod, kolicina))

                # zaključaj proizvod i umanji stanje
                cur.execute("SELECT StanjeNaSkladistu FROM Proizvod WHERE idProizvod=%s FOR UPDATE", (idProizvod,))
                row = cur.fetchone()
                if not row:
                    raise Exception(f"Proizvod {idProizvod} ne postoji.")
                cur.execute("""
                    UPDATE Proizvod
                    SET StanjeNaSkladistu = StanjeNaSkladistu - %s
                    WHERE idProizvod = %s
                """, (kolicina, idProizvod))

        conn.commit()
        return idOtpremnica
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_otpremnica_i_detalj(row_id: int, idOtpremnica: int,
                               new_idKontakt: int,
                               new_idProizvod: int,
                               new_kolicina: int,
                               new_datumOtpremnice: str,
                               new_datumIsporuke: str,
                               new_brojOtpremnice: str):
    """
    row_id = idDetaljiOtpremnice
    datumi: 'YYYY-MM-DD'
    Koregira i zalihe: ako promijeniš proizvod/količinu.
    """
    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT idProizvod, kolicina
                FROM DetaljiOtpremnice
                WHERE idDetaljiOtpremnice=%s
                FOR UPDATE
            """, (row_id,))
            old = cur.fetchone()
            if not old:
                raise Exception("Detalj otpremnice ne postoji.")
            old_prod = old["idProizvod"]
            old_qty  = old["kolicina"]

            # korigiraj zalihe (izlaz)
            if old_prod != new_idProizvod:
                # vrati staru količinu starom proizvodu +
                cur.execute("UPDATE Proizvod SET StanjeNaSkladistu = StanjeNaSkladistu + %s WHERE idProizvod=%s",
                            (old_qty, old_prod))
                # skini novu količinu s novog proizvoda -
                cur.execute("UPDATE Proizvod SET StanjeNaSkladistu = StanjeNaSkladistu - %s WHERE idProizvod=%s",
                            (new_kolicina, new_idProizvod))
            else:
                delta = new_kolicina - old_qty
                if delta != 0:
                    cur.execute("UPDATE Proizvod SET StanjeNaSkladistu = StanjeNaSkladistu - %s WHERE idProizvod=%s",
                                (delta, new_idProizvod))

            # detalj
            cur.execute("""
                UPDATE DetaljiOtpremnice
                SET idProizvod=%s, kolicina=%s
                WHERE idDetaljiOtpremnice=%s
            """, (new_idProizvod, new_kolicina, row_id))

            # zaglavlje
            cur.execute("""
                UPDATE Otpremnica
                SET idKontakt=%s, datumOtpremnice=%s, datumIsporuke=%s, brojOtpremnice=%s
                WHERE idOtpremnica=%s
            """, (new_idKontakt, new_datumOtpremnice, new_datumIsporuke, new_brojOtpremnice, idOtpremnica))

        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_izlazi_search(search_by: str | None = None, term: str | None = None, limit: int = 200):
    """
    Vraća:
      row_id, idOtpremnica, idKontakt, idProizvod,
      kontakt, proizvod, kolicina, datum_isporuke, broj_otpremnice
    """
    base_sql = """
    SELECT
        do.idDetaljiOtpremnice AS row_id,
        o.idOtpremnica,
        k.idKontakt,
        p.idProizvod,
        k.naziv                           AS kontakt,
        p.naziv                           AS proizvod,
        do.kolicina                       AS kolicina,
        DATE_FORMAT(o.datumIsporuke, '%d.%m.%Y') AS datum_isporuke,
        o.brojOtpremnice                  AS broj_otpremnice
    FROM DetaljiOtpremnice do
    JOIN Otpremnica o ON o.idOtpremnica = do.idOtpremnica
    JOIN Proizvod   p ON p.idProizvod   = do.idProizvod
    JOIN Kontakt    k ON k.idKontakt    = o.idKontakt
    """
    where, params = "", []
    if search_by and term:
        if search_by == "Proizvod":
            where = "WHERE p.naziv LIKE %s"; params.append(f"%{term}%")
        elif search_by == "Kontakt":
            where = "WHERE k.naziv LIKE %s"; params.append(f"%{term}%")
        elif search_by == "Godina isporuke":
            where = "WHERE YEAR(o.datumIsporuke) = %s"; params.append(int(term))
        elif search_by == "Otpremnica #":
            where = "WHERE o.idOtpremnica = %s"; params.append(int(term))

    sql = base_sql + where + " ORDER BY do.idDetaljiOtpremnice DESC LIMIT %s"
    params.append(limit)

    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()