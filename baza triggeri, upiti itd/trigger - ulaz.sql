-- INSERT: +količina
DELIMITER $$
CREATE TRIGGER trg_dn_ai
AFTER INSERT ON DetaljiNarudzbe
FOR EACH ROW
BEGIN
  UPDATE Proizvod
  SET StanjeNaSkladistu = StanjeNaSkladistu + NEW.kolicina
  WHERE idProizvod = NEW.idProizvod;
END$$

-- UPDATE: korekcija po razlici; ako je promijenjen proizvod, vrati staru količinu starom, dodaj novu novom
CREATE TRIGGER trg_dn_au
AFTER UPDATE ON DetaljiNarudzbe
FOR EACH ROW
BEGIN
  IF OLD.idProizvod = NEW.idProizvod THEN
    UPDATE Proizvod
    SET StanjeNaSkladistu = StanjeNaSkladistu + (NEW.kolicina - OLD.kolicina)
    WHERE idProizvod = NEW.idProizvod;
  ELSE
    UPDATE Proizvod
    SET StanjeNaSkladistu = StanjeNaSkladistu - OLD.kolicina
    WHERE idProizvod = OLD.idProizvod;

    UPDATE Proizvod
    SET StanjeNaSkladistu = StanjeNaSkladistu + NEW.kolicina
    WHERE idProizvod = NEW.idProizvod;
  END IF;
END$$

-- DELETE: -količina (poništi ulaz)
CREATE TRIGGER trg_dn_ad
AFTER DELETE ON DetaljiNarudzbe
FOR EACH ROW
BEGIN
  UPDATE Proizvod
  SET StanjeNaSkladistu = StanjeNaSkladistu - OLD.kolicina
  WHERE idProizvod = OLD.idProizvod;
END$$


DELIMITER ;