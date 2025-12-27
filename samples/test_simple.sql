-- Simple test
CREATE TABLE Test (id INT, name TEXT);
INSERT INTO Test VALUES (1, 'Elsadany');
SELECT name FROM Test WHERE id = 1;
