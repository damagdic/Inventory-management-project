import os
import mysql.connector
from dataclasses import dataclass
from typing import Optional

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "Salopekselo2"),
    "database": os.getenv("DB_NAME", "skladistedb"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

# ===== JedinicaMjere =========================================================
@dataclass
class JedinicaMjere:
    idJedinicaMjere: Optional[int]
    oznaka: str
    opis: str

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idJedinicaMjere:
                    cur.execute("""UPDATE JedinicaMjere SET oznaka=%s, opis=%s
                                   WHERE idJedinicaMjere=%s""",
                                (self.oznaka, self.opis, self.idJedinicaMjere))
                else:
                    cur.execute("""INSERT INTO JedinicaMjere (oznaka, opis)
                                   VALUES (%s, %s)""",
                                (self.oznaka, self.opis))
                    self.idJedinicaMjere = cur.lastrowid
            conn.commit()
            return self.idJedinicaMjere
        finally: conn.close()

    def delete(self):
        if not self.idJedinicaMjere: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM JedinicaMjere WHERE idJedinicaMjere=%s",
                            (self.idJedinicaMjere,))
            conn.commit()
        finally: conn.close()

    @staticmethod
    def get_all():
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""SELECT idJedinicaMjere, oznaka, opis
                               FROM JedinicaMjere ORDER BY oznaka""")
                return cur.fetchall()
        finally: conn.close()


# ===== Proizvod ==============================================================
@dataclass
class Proizvod:
    idProizvod: Optional[int]
    naziv: str
    idJedinicaMjere: int
    StanjeNaSkladistu: int = 0
    cijena: Optional[float] = None

    def __str__(self):
        return f"Proizvod(id={self.idProizvod}, naziv={self.naziv}, jedinica_mjere={self.idJedinicaMjere}, stanje_na_skladistu={self.stanjeNaSkladistu}, cijena={self.cijena})"

    def __repr__(self):
        return self.__str__()

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idProizvod:
                    cur.execute("""UPDATE Proizvod
                                   SET naziv=%s, idJedinicaMjere=%s,
                                       StanjeNaSkladistu=%s, cijena=%s
                                   WHERE idProizvod=%s""",
                                (self.naziv, self.idJedinicaMjere,
                                 self.StanjeNaSkladistu, self.cijena,
                                 self.idProizvod))
                else:
                    cur.execute("""INSERT INTO Proizvod
                                      (naziv, idJedinicaMjere, StanjeNaSkladistu, cijena)
                                   VALUES (%s, %s, %s, %s)""",
                                (self.naziv, self.idJedinicaMjere,
                                 self.StanjeNaSkladistu, self.cijena))
                    self.idProizvod = cur.lastrowid
            conn.commit()
            return self.idProizvod
        finally: conn.close()

    def delete(self):
        if not self.idProizvod: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Proizvod WHERE idProizvod=%s",
                            (self.idProizvod,))
            conn.commit()
        finally: conn.close()

    @staticmethod
    def get_all():
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""SELECT idProizvod, naziv, idJedinicaMjere,
                                      StanjeNaSkladistu, cijena
                               FROM Proizvod ORDER BY naziv""")
                return cur.fetchall()
        finally: conn.close()
    
    @staticmethod
    def get(idProizvod: int) -> Optional["Proizvod"]:
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""SELECT idProizvod, naziv, idJedinicaMjere,
                                      StanjeNaSkladistu, cijena
                               FROM Proizvod WHERE idProizvod=%s""",
                            (idProizvod,))
                r = cur.fetchone()
                if not r:
                    return None
                return Proizvod(
                    idProizvod=r["idProizvod"],
                    naziv=r["naziv"],
                    idJedinicaMjere=r["idJedinicaMjere"],
                    StanjeNaSkladistu=r["StanjeNaSkladistu"],
                    cijena=r["cijena"]
                )
        finally: conn.close()

# ===== Kontakt ===============================================================
@dataclass
class Kontakt:
    idKontakt: Optional[int]
    naziv: str
    OIB: Optional[str] = None 
    adresa: Optional[str] = None
    kontaktOsoba: Optional[str] = None
    telefon: Optional[str] = None

    @staticmethod
    def _norm_str(val: Optional[str]) -> Optional[str]:
        v = (val or "").strip()
        return v if v else None

    def validate(self) -> None:
        if not self.naziv or not self.naziv.strip():
            raise ValueError("Naziv je obavezan")
        if self.OIB:
            o = self.OIB.strip()
            if not o.isdigit():
                raise ValueError("OIB smije sadržavati samo znamenke.")
            self.OIB = o

    def save(self) -> int:
        self.validate()
        self.naziv = self._norm_str(self.naziv) or ""
        self.OIB = self._norm_str(self.OIB)
        self.adresa = self._norm_str(self.adresa)
        self.kontaktOsoba = self._norm_str(self.kontaktOsoba)
        self.telefon = self._norm_str(self.telefon)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idKontakt:
                    cur.execute("""UPDATE Kontakt
                                   SET naziv=%s, OIB=%s, adresa=%s,
                                       kontaktOsoba=%s, telefon=%s
                                   WHERE idKontakt=%s""",
                                (self.naziv, self.OIB, self.adresa,
                                 self.kontaktOsoba, self.telefon, self.idKontakt))
                else:
                    cur.execute("""INSERT INTO Kontakt
                                      (naziv, OIB, adresa, kontaktOsoba, telefon)
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (self.naziv, self.OIB, self.adresa,
                                 self.kontaktOsoba, self.telefon))
                    self.idKontakt = cur.lastrowid
            conn.commit()
            return self.idKontakt
        finally: conn.close()

    @staticmethod
    def get(idKontakt: int) -> Optional["Kontakt"]:
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""
                    SELECT idKontakt, naziv, OIB, adresa, kontaktOsoba, telefon
                    FROM Kontakt WHERE idKontakt=%s
                """, (idKontakt,))
                r = cur.fetchone()
                if not r:
                    return None
                return Kontakt(
                    idKontakt=r["idKontakt"],
                    naziv=r["naziv"],
                    OIB=r["OIB"],
                    adresa=r["adresa"],
                    kontaktOsoba=r["kontaktOsoba"],
                    telefon=r["telefon"]
                )
        finally:
            conn.close()

    def delete(self):
        if not self.idKontakt: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Kontakt WHERE idKontakt=%s",
                            (self.idKontakt,))
            conn.commit()
        finally: conn.close()

    @staticmethod
    def get_all(term: Optional[str] = None):
        sql = "SELECT idKontakt, naziv, OIB, adresa, kontaktOsoba, telefon FROM Kontakt"
        params = []
        if term:
            sql += " WHERE naziv LIKE %s"; params.append(f"%{term}%")
        sql += " ORDER BY naziv"
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        finally: conn.close()


# ===== Narudzba ==============================================================
@dataclass
class Narudzba:
    idNarudzba: Optional[int]
    idKontakt: int
    datumNarudzbe: str     # 'YYYY-MM-DD'
    datumPrimitka: str     # 'YYYY-MM-DD'

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idNarudzba:
                    cur.execute("""UPDATE Narudzba
                                   SET idKontakt=%s, datumNarudzbe=%s, datumPrimitka=%s
                                   WHERE idNarudzba=%s""",
                                (self.idKontakt, self.datumNarudzbe,
                                 self.datumPrimitka, self.idNarudzba))
                else:
                    cur.execute("""INSERT INTO Narudzba
                                      (idKontakt, datumNarudzbe, datumPrimitka)
                                   VALUES (%s, %s, %s)""",
                                (self.idKontakt, self.datumNarudzbe, self.datumPrimitka))
                    self.idNarudzba = cur.lastrowid
            conn.commit()
            return self.idNarudzba
        finally: conn.close()

    def delete(self):
        if not self.idNarudzba: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Narudzba WHERE idNarudzba=%s",
                            (self.idNarudzba,))
            conn.commit()
        finally: conn.close()

    @staticmethod
    def get_all(limit: int = 200):
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""SELECT idNarudzba, idKontakt, datumNarudzbe, datumPrimitka
                               FROM Narudzba ORDER BY idNarudzba DESC LIMIT %s""",
                            (limit,))
                return cur.fetchall()
        finally: conn.close()
    
    @staticmethod
    def get(idNarudzba: int) -> Optional["Narudzba"]:
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""SELECT idNarudzba, idKontakt, datumNarudzbe, datumPrimitka
                               FROM Narudzba WHERE idNarudzba=%s""",
                            (idNarudzba,))
                r = cur.fetchone()
                if not r:
                    return None
                return Narudzba(
                    idNarudzba=r["idNarudzba"],
                    idKontakt=r["idKontakt"],
                    datumNarudzbe=r["datumNarudzbe"],
                    datumPrimitka=r["datumPrimitka"]
                )
        finally: conn.close()


# ===== DetaljiNarudzbe =======================================================
@dataclass
class DetaljiNarudzbe:
    idDetaljiNarudzbe: Optional[int]
    idNarudzba: int
    idProizvod: int
    kolicina: int

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idDetaljiNarudzbe:
                    cur.execute("""UPDATE DetaljiNarudzbe
                                   SET idNarudzba=%s, idProizvod=%s, kolicina=%s
                                   WHERE idDetaljiNarudzbe=%s""",
                                (self.idNarudzba, self.idProizvod,
                                 self.kolicina, self.idDetaljiNarudzbe))
                else:
                    cur.execute("""INSERT INTO DetaljiNarudzbe
                                      (idNarudzba, idProizvod, kolicina)
                                   VALUES (%s, %s, %s)""",
                                (self.idNarudzba, self.idProizvod, self.kolicina))
                    self.idDetaljiNarudzbe = cur.lastrowid
            conn.commit()
            return self.idDetaljiNarudzbe
        finally: conn.close()

    def delete(self):
        if not self.idDetaljiNarudzbe: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM DetaljiNarudzbe WHERE idDetaljiNarudzbe=%s",
                            (self.idDetaljiNarudzbe,))
            conn.commit()
        finally: conn.close()
    
    @classmethod
    def get(cls, pk: int) -> Optional["DetaljiNarudzbe"]:
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""
                    SELECT idDetaljiNarudzbe, idNarudzba, idProizvod, kolicina
                    FROM DetaljiNarudzbe
                    WHERE idDetaljiNarudzbe=%s
                """, (pk,))
                r = cur.fetchone()
                if not r:
                    return None
                return cls(
                    idDetaljiNarudzbe=r["idDetaljiNarudzbe"],
                    idNarudzba=r["idNarudzba"],
                    idProizvod=r["idProizvod"],
                    kolicina=r["kolicina"]
                )
        finally:
            conn.close()

# ===== Otpremnica ============================================================
@dataclass
class Otpremnica:
    idOtpremnica: Optional[int]
    idKontakt: int
    datumOtpremnice: str   # 'YYYY-MM-DD'
    datumIsporuke: str     # 'YYYY-MM-DD'
    brojOtpremnice: str

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idOtpremnica:
                    cur.execute("""UPDATE Otpremnica
                                   SET idKontakt=%s, datumOtpremnice=%s,
                                       datumIsporuke=%s, brojOtpremnice=%s
                                   WHERE idOtpremnica=%s""",
                                (self.idKontakt, self.datumOtpremnice,
                                 self.datumIsporuke, self.brojOtpremnice, self.idOtpremnica))
                else:
                    cur.execute("""INSERT INTO Otpremnica
                                      (idKontakt, datumOtpremnice, datumIsporuke, brojOtpremnice)
                                   VALUES (%s, %s, %s, %s)""",
                                (self.idKontakt, self.datumOtpremnice,
                                 self.datumIsporuke, self.brojOtpremnice))
                    self.idOtpremnica = cur.lastrowid
            conn.commit()
            return self.idOtpremnica
        finally: conn.close()

    def delete(self):
        if not self.idOtpremnica: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Otpremnica WHERE idOtpremnica=%s",
                            (self.idOtpremnica,))
            conn.commit()
        finally: conn.close()

    @staticmethod
    def get(idOtpremnica: int) -> Optional["Otpremnica"]:
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""SELECT idOtpremnica, idKontakt, datumOtpremnice, datumIsporuke, brojOtpremnice
                               FROM Otpremnica WHERE idOtpremnica=%s""",
                            (idOtpremnica,))
                r = cur.fetchone()
                if not r:
                    return None
                return Otpremnica(
                    idOtpremnica=r["idOtpremnica"],
                    idKontakt=r["idKontakt"],
                    datumOtpremnice=r["datumOtpremnice"],
                    datumIsporuke=r["datumIsporuke"],
                    brojOtpremnice=r["brojOtpremnice"]
                )
        finally: conn.close()


# ===== DetaljiOtpremnice =====================================================
@dataclass
class DetaljiOtpremnice:
    idDetaljiOtpremnice: Optional[int]
    idOtpremnica: int
    idProizvod: int
    kolicina: int
    cijena: float

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idDetaljiOtpremnice:
                    cur.execute("""UPDATE DetaljiOtpremnice
                                   SET idOtpremnica=%s, idProizvod=%s, kolicina=%s, cijena=%s
                                   WHERE idDetaljiOtpremnice=%s""",
                                (self.idOtpremnica, self.idProizvod,
                                 self.kolicina, self.cijena, self.idDetaljiOtpremnice))
                else:
                    cur.execute("""INSERT INTO DetaljiOtpremnice
                                      (idOtpremnica, idProizvod, kolicina, cijena)
                                   VALUES (%s, %s, %s, %s)""",
                                (self.idOtpremnica, self.idProizvod,
                                 self.kolicina, self.cijena))
                    self.idDetaljiOtpremnice = cur.lastrowid
            conn.commit()
            return self.idDetaljiOtpremnice
        finally: conn.close()

    def delete(self):
        if not self.idDetaljiOtpremnice: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM DetaljiOtpremnice WHERE idDetaljiOtpremnice=%s",
                            (self.idDetaljiOtpremnice,))
            conn.commit()
        finally: conn.close()
    
    def get(cls, pk: int) -> Optional["DetaljiOtpremnice"]:
        conn = get_conn()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""
                    SELECT idDetaljiOtpremnice, idOtpremnica, idProizvod, kolicina, cijena
                    FROM DetaljiOtpremnice
                    WHERE idDetaljiOtpremnice=%s
                """, (pk,))
                r = cur.fetchone()
                if not r:
                    return None
                return cls(
                    idDetaljiOtpremnice=r["idDetaljiOtpremnice"],
                    idOtpremnica=r["idOtpremnica"],
                    idProizvod=r["idProizvod"],
                    kolicina=r["kolicina"],
                    cijena=r["cijena"]
                )
        finally:
            conn.close()


# ===== Recept ================================================================
@dataclass
class Recept:
    idRecept: Optional[int]
    naziv: str

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idRecept:
                    cur.execute("""UPDATE Recept SET naziv=%s WHERE idRecept=%s""",
                                (self.naziv, self.idRecept))
                else:
                    cur.execute("""INSERT INTO Recept (naziv) VALUES (%s)""",
                                (self.naziv,))
                    self.idRecept = cur.lastrowid
            conn.commit()
            return self.idRecept
        finally: conn.close()

    def delete(self):
        if not self.idRecept: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Recept WHERE idRecept=%s",
                            (self.idRecept,))
            conn.commit()
        finally: conn.close()


# ===== ReceptSastojci ========================================================
@dataclass
class ReceptSastojci:
    idReceptSastojci: Optional[int]
    idRecept: int
    idProizvod: int
    postotak: float

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idReceptSastojci:
                    cur.execute("""UPDATE ReceptSastojci
                                   SET idRecept=%s, idProizvod=%s, postotak=%s
                                   WHERE idReceptSastojci=%s""",
                                (self.idRecept, self.idProizvod,
                                 self.postotak, self.idReceptSastojci))
                else:
                    cur.execute("""INSERT INTO ReceptSastojci
                                      (idRecept, idProizvod, postotak)
                                   VALUES (%s, %s, %s)""",
                                (self.idRecept, self.idProizvod, self.postotak))
                    self.idReceptSastojci = cur.lastrowid
            conn.commit()
            return self.idReceptSastojci
        finally: conn.close()

    def delete(self):
        if not self.idReceptSastojci: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ReceptSastojci WHERE idReceptSastojci=%s",
                            (self.idReceptSastojci,))
            conn.commit()
        finally: conn.close()


# ===== Bazen =================================================================
@dataclass
class Bazen:
    idBazen: Optional[int]
    naziv: str
    lokacija: str
    kapacitet: int

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idBazen:
                    cur.execute("""UPDATE Bazen
                                   SET naziv=%s, lokacija=%s, kapacitet=%s
                                   WHERE idBazen=%s""",
                                (self.naziv, self.lokacija, self.kapacitet, self.idBazen))
                else:
                    cur.execute("""INSERT INTO Bazen (naziv, lokacija, kapacitet)
                                   VALUES (%s, %s, %s)""",
                                (self.naziv, self.lokacija, self.kapacitet))
                    self.idBazen = cur.lastrowid
            conn.commit()
            return self.idBazen
        finally: conn.close()

    def delete(self):
        if not self.idBazen: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Bazen WHERE idBazen=%s",
                            (self.idBazen,))
            conn.commit()
        finally: conn.close()


# ===== Punjenje ==============================================================
@dataclass
class Punjenje:
    idPunjenje: Optional[int]
    idBazen: int
    idRecept: int
    kolicina: int
    datumPunjenja: str   # 'YYYY-MM-DD'
    datumPraznjenja: str # 'YYYY-MM-DD'

    def save(self) -> int:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if self.idPunjenje:
                    cur.execute("""UPDATE Punjenje
                                   SET idBazen=%s, idRecept=%s, kolicina=%s,
                                       datumPunjenja=%s, datumPraznjenja=%s
                                   WHERE idPunjenje=%s""",
                                (self.idBazen, self.idRecept, self.kolicina,
                                 self.datumPunjenja, self.datumPraznjenja, self.idPunjenje))
                else:
                    cur.execute("""INSERT INTO Punjenje
                                      (idBazen, idRecept, kolicina, datumPunjenja, datumPraznjenja)
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (self.idBazen, self.idRecept, self.kolicina,
                                 self.datumPunjenja, self.datumPraznjenja))
                    self.idPunjenje = cur.lastrowid
            conn.commit()
            return self.idPunjenje
        finally: conn.close()

    def delete(self):
        if not self.idPunjenje: return
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Punjenje WHERE idPunjenje=%s",
                            (self.idPunjenje,))
            conn.commit()
        finally: conn.close()

        