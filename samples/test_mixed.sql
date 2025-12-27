-- Comprehensive test with mixed valid and invalid semantics

-- Valid: Create first table
CREATE TABLE Employees (emp_id INT, emp_name TEXT, salary FLOAT);

-- Valid: Insert correct data
INSERT INTO Employees VALUES (1, 'John Doe', 50000.50);
INSERT INTO Employees VALUES (2, 'Jane Smith', 60000.75);

-- ERROR: Type mismatch - string for INT, int for TEXT, string for FLOAT
INSERT INTO Employees VALUES ('Three', 3, 'NotANumber');

-- Valid: Select with WHERE
SELECT emp_name, salary FROM Employees WHERE salary > 55000.00;

-- ERROR: Column doesn't exist
SELECT department FROM Employees;

-- ERROR: Table redeclaration
CREATE TABLE Employees (id INT);

-- Valid: Create second table
CREATE TABLE Departments (dept_name TEXT, budget INT);

-- Valid: Insert into departments
INSERT INTO Departments VALUES ('Engineering', 1000000);

-- ERROR: Wrong value count
INSERT INTO Departments VALUES ('Sales');

-- ERROR: Reference non-existent table
SELECT * FROM Projects;

-- Valid: Complex WHERE clause
SELECT emp_name FROM Employees WHERE emp_id > 0 AND salary < 100000.00;

-- ERROR: Type mismatch in WHERE
SELECT emp_name FROM Employees WHERE emp_name = 123;

-- Valid: UPDATE
UPDATE Employees SET salary = 65000.00 WHERE emp_id = 2;

-- ERROR: Update non-existent column
UPDATE Employees SET age = 30 WHERE emp_id = 1;

-- Valid: DELETE
DELETE FROM Employees WHERE emp_id = 1;
