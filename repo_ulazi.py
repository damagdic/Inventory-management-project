from db import get_conn


def fetch_ulazi_search(q: str | None = None, limit: int = 200):
    base_sql = """
    SELECT
        dn.idDetaljiNarudzbe AS row_id,         -- jedinstveni ID retka
        k.naziv              AS kontakt,
        p.naziv              AS proizvod,
        dn.kolicina          AS kolicina,
        DATE_FORMAT(n.datumPrimitka, '%d.%m.%Y') AS datum_primitka
    FROM DetaljiNarudzbe dn
    JOIN Narudzba  n ON n.idNarudzba = dn.idNarudzba
    JOIN Proizvod  p ON p.idProizvod = dn.idProizvod
    JOIN Kontakt   k ON k.idKontakt  = n.idKontakt
    """
    where = ""
    params = []
    if q:
        where = "WHERE (k.naziv LIKE %s OR p.naziv LIKE %s)"
        like = f"%{q}%"
        params.extend([like, like])

    tail = " ORDER BY dn.idDetaljiNarudzbe DESC LIMIT %s"
    params.append(limit)

    sql = base_sql + where + tail

    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()