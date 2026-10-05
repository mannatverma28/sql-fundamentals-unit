import os
import sqlite3
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SETUP_SQL = os.path.join(HERE, "setup.sql")
CLEANUP_SQL = os.path.join(HERE, "cleanup.sql")


def read_sql(path):
    # utf-8-sig skips a byte-order mark if an editor added one;
    # text mode turns Windows "\r\n" line endings into "\n".
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def run_script(conn, path):
    """Run every statement in the file in order, like DBeaver's Execute Script.

    Returns the column names and rows of the last statement that produced rows.
    """
    columns, rows = None, None
    statement = ""
    for line in read_sql(path).splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            cursor = conn.execute(statement)
            if cursor.description is not None:
                columns = [d[0] for d in cursor.description]
                rows = cursor.fetchall()
            statement = ""
    leftover = [l for l in statement.splitlines() if l.strip() and not l.strip().startswith("--")]
    if leftover:
        raise AssertionError("Statement without a closing semicolon: " + " ".join(leftover))
    conn.commit()
    return columns, rows


def make_table(conn, rows):
    # id is not a PRIMARY KEY here, so SQLite returns rows in insert order
    # unless the query asks for ORDER BY id.
    conn.execute(
        "CREATE TABLE employees (id INTEGER, name TEXT NOT NULL, "
        "salary DECIMAL(10, 2) NOT NULL, department TEXT NOT NULL)"
    )
    conn.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", rows)
    conn.commit()


class CleanupWithOwnDataTest(unittest.TestCase):
    """Runs cleanup.sql against data the script has never seen."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        make_table(self.conn, [
            (12, "Zoe", 2000, "Sales"),
            (3, "Yan", 1000, "Temporary"),
            (40, "Xavi", 1500, "Kitchen"),
            (7, "Wren", 1234.56, "Sales"),
            (25, "Vic", 900, "Temporary"),
            (31, "Uma", 1800, "Sales Support"),
            (19, "Tom", 950, "Temporary"),
        ])
        self.columns, self.rows = run_script(self.conn, CLEANUP_SQL)

    def tearDown(self):
        self.conn.close()

    def salary_of(self, emp_id):
        return self.conn.execute(
            "SELECT salary FROM employees WHERE id = ?", (emp_id,)
        ).fetchone()[0]

    def test_sales_salary_2000_becomes_2200(self):
        self.assertEqual(self.salary_of(12), 2200)

    def test_raise_is_rounded_to_cents(self):
        # 1234.56 * 1.10 = 1358.016 -> 1358.02
        self.assertEqual(self.salary_of(7), 1358.02)

    def test_other_departments_keep_their_salary(self):
        self.assertEqual(self.salary_of(40), 1500)
        self.assertEqual(self.salary_of(31), 1800)

    def test_all_three_temporary_employees_are_deleted(self):
        count = self.conn.execute(
            "SELECT COUNT(*) FROM employees WHERE department = 'Temporary'"
        ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_nobody_else_is_deleted(self):
        count = self.conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        self.assertEqual(count, 4)

    def test_final_query_shows_the_four_columns(self):
        self.assertEqual(self.columns, ["id", "name", "salary", "department"])

    def test_final_query_is_ordered_by_id(self):
        self.assertEqual([r[0] for r in self.rows], [7, 12, 31, 40])


class CleanupWithSampleDataTest(unittest.TestCase):
    """Runs setup.sql then cleanup.sql, exactly as the student does in DBeaver."""

    def test_final_employee_list(self):
        conn = sqlite3.connect(":memory:")
        try:
            run_script(conn, SETUP_SQL)
            _, rows = run_script(conn, CLEANUP_SQL)
        finally:
            conn.close()
        self.assertEqual(rows, [
            (1, "Alice Moreno", 2200, "Sales"),
            (2, "Ben Okafor", 2500, "Warehouse"),
            (4, "Dev Patel", 2035.55, "Sales"),
            (6, "Farah Haddad", 3000, "Office"),
            (8, "Hana Sato", 3410, "Sales"),
        ])

    def test_setup_can_be_run_twice(self):
        conn = sqlite3.connect(":memory:")
        try:
            run_script(conn, SETUP_SQL)
            run_script(conn, SETUP_SQL)
            count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(count, 8)


if __name__ == "__main__":
    unittest.main()