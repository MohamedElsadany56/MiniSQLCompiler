-- Valid SQL Queries for Semantic Analysis Testing
-- This file contains syntactically and semantically correct SQL queries

-- Create a Students table
CREATE TABLE Students (name TEXT, age INT, gpa FLOAT);

-- Insert valid data into Students
INSERT INTO Students VALUES ('Elsadany', 20, 3.5);
INSERT INTO Students VALUES ('Ziad', 22, 3.8);
INSERT INTO Students VALUES ('Mohamed', 19, 3.2);

-- Create another table
CREATE TABLE Courses (course_name TEXT, credits INT);

-- Insert into Courses
INSERT INTO Courses VALUES ('Database Systems', 3);
INSERT INTO Courses VALUES ('Compilers', 4);

-- Select queries
SELECT name, age FROM Students WHERE age > 18;
SELECT course_name FROM Courses WHERE credits = 3;
SELECT name, gpa FROM Students WHERE gpa >= 3.0 AND age < 25;

-- Update queries
UPDATE Students SET age = 21 WHERE name = 'Mostafa';
UPDATE Courses SET credits = 5 WHERE course_name = 'Compilers';

-- Delete queries
DELETE FROM Students WHERE age < 19;
DELETE FROM Courses WHERE credits > 5;
