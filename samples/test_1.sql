CREATE TABLE Students (name TEXT, age INT);
INSERT  Students VALUES ('Ali', 20);
SELECT name, age FROM Students WHERE age > 18 AND age < 25;