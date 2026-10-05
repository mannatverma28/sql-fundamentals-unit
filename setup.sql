-- Builds a fresh employees table with sample data.
-- Safe to run again: it throws away the old table first.
DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    department TEXT NOT NULL
);

INSERT INTO employees (id, name, salary, department) VALUES (1, 'Alice Moreno', 2000.00, 'Sales');
INSERT INTO employees (id, name, salary, department) VALUES (2, 'Ben Okafor', 2500.00, 'Warehouse');
INSERT INTO employees (id, name, salary, department) VALUES (3, 'Chloe Tan', 1200.00, 'Temporary');
INSERT INTO employees (id, name, salary, department) VALUES (4, 'Dev Patel', 1850.50, 'Sales');
INSERT INTO employees (id, name, salary, department) VALUES (5, 'Emma Schulz', 1100.00, 'Temporary');
INSERT INTO employees (id, name, salary, department) VALUES (6, 'Farah Haddad', 3000.00, 'Office');
INSERT INTO employees (id, name, salary, department) VALUES (7, 'Gus Lindqvist', 1150.00, 'Temporary');
INSERT INTO employees (id, name, salary, department) VALUES (8, 'Hana Sato', 3100.00, 'Sales');