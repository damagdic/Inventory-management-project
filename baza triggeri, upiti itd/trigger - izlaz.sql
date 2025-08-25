-- IZLAZ (DetaljiOtpremnice) s provjerom
DELIMITER $$
CREATE TRIGGER trg_do_ai
BEFORE INSERT ON DetaljiOtpremnice
FOR EACH ROW
BEGIN
  DECLARE curr INT;
  SELECT StanjeNaSkladistu INTO curr FROM Proizvod WHERE idProizvod = NEW.idProizvod FOR UPDATE;
  IF curr IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Proizvod ne postoji';
  END IF;
  IF curr < NEW.kolicina THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nedovoljno na skladištu';
  END IF;
  UPDATE Proizvod
  SET StanjeNaSkladistu = StanjeNaSkladistu - NEW.kolicina
  WHERE idProizvod = NEW.idProizvod;
END$$

CREATE TRIGGER trg_do_au
BEFORE UPDATE ON DetaljiOtpremnice
FOR EACH ROW
BEGIN
  DECLARE curr INT;
  IF OLD.idProizvod = NEW.idProizvod THEN
    SELECT StanjeNaSkladistu INTO curr FROM Proizvod WHERE idProizvod = NEW.idProizvod FOR UPDATE;
    SET curr = curr + OLD.kolicina;
    IF curr < NEW.kolicina THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nedovoljno na skladištu za ažuriranje';
    END IF;
    UPDATE Proizvod SET StanjeNaSkladistu = curr - NEW.kolicina WHERE idProizvod = NEW.idProizvod;
  ELSE
    UPDATE Proizvod SET StanjeNaSkladistu = StanjeNaSkladistu + OLD.kolicina WHERE idProizvod = OLD.idProizvod;
    SELECT StanjeNaSkladistu INTO curr FROM Proizvod WHERE idProizvod = NEW.idProizvod FOR UPDATE;
    IF curr < NEW.kolicina THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nedovoljno na skladištu za promjenu proizvoda';
    END IF;
    UPDATE Proizvod SET StanjeNaSkladistu = StanjeNaSkladistu - NEW.kolicina WHERE idProizvod = NEW.idProizvod;
  END IF;
END$$

CREATE TRIGGER trg_do_ad
AFTER DELETE ON DetaljiOtpremnice
FOR EACH ROW
BEGIN
  UPDATE Proizvod
  SET StanjeNaSkladistu = StanjeNaSkladistu + OLD.kolicina
  WHERE idProizvod = OLD.idProizvod;
END$$

DELIMITER ;