import sqlite3
import pandas as pd
import mysql.connector

print(mysql.connector.__version__)

db = mysql.connector.connect(
    host="localhost",
    user="root",             
    password="Salopekselo2",
    port = 3306,
    database="SkladisteDB"  
)

print("Spojen na bazu:", db.is_connected())

mycursor = db.cursor()

# 2. Definicije tablica
tables = {}

tables['JedinicaMjere'] = """
CREATE TABLE IF NOT EXISTS JedinicaMjere (
    idJedinicaMjere INT PRIMARY KEY,
    oznaka VARCHAR(20) NOT NULL,
    opis VARCHAR(100) NOT NULL
);
"""

tables['Recept'] = """
CREATE TABLE IF NOT EXISTS Recept (
    idRecept INT PRIMARY KEY,
    naziv VARCHAR(100) NOT NULL
);
"""

tables['Bazen'] = """
CREATE TABLE IF NOT EXISTS Bazen (
    idBazen INT PRIMARY KEY,
    naziv VARCHAR(100) NOT NULL,
    lokacija VARCHAR(200) NOT NULL,
    kapacitet INT NOT NULL
);
"""

tables['Kontakt'] = """
CREATE TABLE IF NOT EXISTS Kontakt (
    idKontakt INT PRIMARY KEY,
    naziv VARCHAR(100) NOT NULL,
    OIB BIGINT NOT NULL,
    adresa VARCHAR(200),
    kontaktOsoba VARCHAR(100),
    telefon VARCHAR(50)
);
"""

tables['Proizvod'] = """
CREATE TABLE IF NOT EXISTS Proizvod (
    idProizvod INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(100) NOT NULL,
    idJedinicaMjere INT NOT NULL,
    StanjeNaSkladistu INT NOT NULL,
    cijena DECIMAL(10,2),
    FOREIGN KEY (idJedinicaMjere) REFERENCES JedinicaMjere(idJedinicaMjere)
);
"""
tables['Otpremnica'] = """
CREATE TABLE IF NOT EXISTS Otpremnica (
    idOtpremnica INT PRIMARY KEY,
    idKontakt INT NOT NULL,
    datumOtpremnice DATE NOT NULL,
    datumIsporuke DATE NOT NULL,
    brojOtpremnice VARCHAR(50) NOT NULL,
    FOREIGN KEY (idKontakt) REFERENCES Kontakt(idKontakt)
);
"""

tables['Narudzba'] = """
CREATE TABLE IF NOT EXISTS Narudzba (
    idNarudzba INT PRIMARY KEY,
    idKontakt INT NOT NULL,
    datumNarudzbe DATE NOT NULL,
    datumPrimitka DATE NOT NULL,
    FOREIGN KEY (idKontakt) REFERENCES Kontakt(idKontakt)
);
"""
tables['ReceptSastojci'] = """
CREATE TABLE IF NOT EXISTS ReceptSastojci (
    idReceptSastojci INT PRIMARY KEY,
    idRecept INT NOT NULL,
    idProizvod INT NOT NULL,
    postotak DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (idRecept) REFERENCES Recept(idRecept),
    FOREIGN KEY (idProizvod) REFERENCES Proizvod(idProizvod)
);
"""

tables['Punjenje'] = """
CREATE TABLE IF NOT EXISTS Punjenje (
    idPunjenje INT PRIMARY KEY,
    idBazen INT NOT NULL,
    idRecept INT NOT NULL,
    kolicina INT NOT NULL,
    datumPunjenja DATE NOT NULL,
    datumPraznjenja DATE NOT NULL,
    FOREIGN KEY (idBazen) REFERENCES Bazen(idBazen),
    FOREIGN KEY (idRecept) REFERENCES Recept(idRecept)
);
"""


tables['DetaljiOtpremnice'] = """
CREATE TABLE IF NOT EXISTS DetaljiOtpremnice (
    idDetaljiOtpremnice INT PRIMARY KEY,
    idOtpremnica INT NOT NULL,
    idProizvod INT NOT NULL,
    kolicina INT NOT NULL,
    cijena DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (idOtpremnica) REFERENCES Otpremnica(idOtpremnica),
    FOREIGN KEY (idProizvod) REFERENCES Proizvod(idProizvod)
);
"""


tables['DetaljiNarudzbe'] = """
CREATE TABLE IF NOT EXISTS DetaljiNarudzbe (
    idDetaljiNarudzbe INT PRIMARY KEY,
    idNarudzba INT NOT NULL,
    idProizvod INT NOT NULL,
    kolicina INT NOT NULL,
    FOREIGN KEY (idNarudzba) REFERENCES Narudzba(idNarudzba),
    FOREIGN KEY (idProizvod) REFERENCES Proizvod(idProizvod)
);
"""

# 3. Izvrši sve CREATE TABLE upite
for name, ddl in tables.items():
    try:
        print(f"Kreiram tablicu {name} ... ", end="")
        mycursor.execute(ddl)
        print("OK")
    except mysql.connector.Error as err:
        print(f"Greška: {err}")

mycursor.execute("SHOW TABLES;")
print("Tablice u bazi:")
for (table_name,) in mycursor:
    print("-", table_name)
    
# 4. Zatvori konekciju
mycursor.close()
db.close()
