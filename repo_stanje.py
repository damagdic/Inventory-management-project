from db import get_conn

def fetch_stanje_hladnjaca(term: str | None = None, exclude_kupus: bool = True):
    """
    Vraća listu dict-ova:
      idProizvod, naziv, jm, stanje, cijena, vrijednost
    Filtrira po nazivu (LIKE) i opcionalno isključuje 'Kiseli kupus%' i 'Kisela repa'.
    """
    sql = """
    SELECT
      p.idProizvod,
      p.naziv,
      jm.oznaka AS jm,
      p.StanjeNaSkladistu AS stanje,
      p.cijena,
      CASE WHEN p.cijena IS NULL THEN NULL
           ELSE p.cijena * p.StanjeNaSkladistu
      END AS vrijednost
    FROM Proizvod p
    JOIN JedinicaMjere jm ON jm.idJedinicaMjere = p.idJedinicaMjere
    """
    where = []
    params = []

    if exclude_kupus:
        # isključi sve “Kiseli kupus …” i točan naziv “Kisela repa”
        where.append("(p.naziv NOT LIKE 'Kiseli kupus%' AND p.naziv <> 'Kisela repa')")

    if term:
        where.append("p.naziv LIKE %s")
        params.append(f"%{term}%")

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