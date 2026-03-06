# Vextra
Växtra or vextra is a platform for users buying and selling plants. Made with Dearpy GUI and MySQL


The trigger might be missing so Im posting it here just in case: DELIMITER $$
CREATE TRIGGER Update_UpForSale
AFTER INSERT 
ON Transactions FOR EACH ROW
BEGIN
DELETE FROM UpForSale
WHERE upforsale.Seller_ID = NEW.Seller_ID
AND upforsale.Plant_ID = NEW.Plant_ID;


END $$

DELIMITER ;
