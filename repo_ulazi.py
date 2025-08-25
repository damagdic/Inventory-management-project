from db import get_conn


from db import get_conn

def fetch_ulazi_search(search_by: str | None = None, term: str | None = None, limit: int = 200):
    """
    Vraća redove s kolonama:
    row_id, idNarudzba, idKontakt, idProizvod, kontakt, proizvod, kolicina, datum_primitka
    Filtrira prema search_by/term:
      - "Proizvod": p.naziv LIKE %term%
      - "Kontakt":  k.naziv LIKE %term%
      - "Godina ulaza": YEAR(n.datumPrimitka) = term (int)
    """
    base_sql = """
    SELECT
        dn.idDetaljiNarudzbe AS row_id,
        n.idNarudzba,
        k.idKontakt,
        p.idProizvod,
        k.naziv              AS kontakt,
        p.naziv              AS proizvod,
        dn.kolicina          AS kolicina,
        DATE_FORMAT(n.datumPrimitka, '%d.%m.%Y') AS datum_primitka
    FROM DetaljiNarudzbe dn
    JOIN Narudzba  n ON n.idNarudzba = dn.idNarudzba
    JOIN Proizvod  p ON p.idProizvod = dn.idProizvod
    JOIN Kontakt   k ON k.idKontakt  = n.idKontakt
    """
    where, params = "", []

    if search_by and term:
        if search_by == "Proizvod":
            where = "WHERE p.naziv LIKE %s"
            params.append(f"%{term}%")
        elif search_by == "Kontakt":
            where = "WHERE k.naziv LIKE %s"
            params.append(f"%{term}%")
        elif search_by == "Godina ulaza":
            where = "WHERE YEAR(n.datumPrimitka) = %s"
            params.append(int(term))

    sql = base_sql + where + " ORDER BY dn.idDetaljiNarudzbe DESC LIMIT %s"
    params.append(limit)

    conn = get_conn()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()