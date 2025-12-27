-- SQL Queries with Intentional Semantic Errors
-- This file demonstrates various semantic error detection capabilities

-- Error 1: Table redeclaration
CREATE TABLE Users (id INT, name TEXT);
CREATE TABLE Users (email TEXT);  -- ERROR: Users already declared

-- Error 2: Table doesn't exist
INSERT INTO NonExistent VALUES (1, 'Test');  -- ERROR: Table not found

-- Error 3: Type mismatch in INSERT (wrong number of values)
CREATE TABLE Products (id INT, name TEXT, price FLOAT);
INSERT INTO Products VALUES (1, 'Widget');  -- ERROR: Expected 3 values, got 2

-- Error 4: Type mismatch in INSERT (wrong types)
INSERT INTO Products VALUES ('NotANumber', 123, 'NotAFloat');  -- ERROR: Type mismatches

-- Error 5: Column doesn't exist in SELECT
SELECT invalid_col FROM Products;  -- ERROR: Column not found

-- Error 6: Column doesn't exist in WHERE
SELECT name FROM Products WHERE nonexistent = 5;  -- ERROR: Column not found

-- Error 7: Type mismatch in WHERE comparison
SELECT id FROM Products WHERE id = 'text';  -- ERROR: Comparing INT with TEXT

-- Error 8: Type mismatch in WHERE comparison (opposite)
SELECT name FROM Products WHERE name > 123;  -- ERROR: Comparing TEXT with INT

-- Error 9: Table not found in SELECT
SELECT * FROM InvalidTable;  -- ERROR: Table not found

-- Error 10: Type mismatch in UPDATE
UPDATE Products SET price = 'NotANumber' WHERE id = 1;  -- ERROR: Type mismatch

-- Error 11: Column doesn't exist in UPDATE
UPDATE Products SET invalid_column = 100 WHERE id = 1;  -- ERROR: Column not found

-- Error 12: Table not found in DELETE
DELETE FROM NonExistentTable WHERE id = 1;  -- ERROR: Table not found
