SELECT name, age FROM students WHERE age >= 22;

## multi-line comment
   This is a comment block
   that spans multiple lines
##
INSERT INTO users VALUES ('Elsdany', 25, 3.14);

UPDATE users
SET age = age + 1
WHERE name = 'Elsdany';

DELETE FROM users WHERE age < 18;

CREATE TABLE employees (
    id INT,
    full_name TEXT,
    salary FLOAT
);

SELECT * FROM employees WHERE salary >= 5000;