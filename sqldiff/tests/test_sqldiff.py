from sqldiff.sqldiff import generate_sql_diff


def test_sql_diff_add_table():

    old_sql = ""

    new_sql = """
        CREATE TABLE foo (
            id serial,
            data1 text,
            data2 integer
        );"""

    diff_sql = "CREATE TABLE foo (id serial, data1 text, data2 integer);\n"

    assert generate_sql_diff(old_sql, new_sql) == diff_sql


def test_sql_diff_remove_table():

    old_sql = """
        CREATE TABLE foo (
            id serial,
            data1 text,
            data2 integer
        );"""

    new_sql = ""

    diff_sql = "DROP TABLE foo;\n"

    assert generate_sql_diff(old_sql, new_sql) == diff_sql


def test_sql_diff_change_columns():

    old_sql = """
        CREATE TABLE foo (
            id serial,
            data1 text
        );"""

    new_sql = """
        CREATE TABLE foo (
            id serial,
            data1 text,
            data2 integer,
            data3 boolean
        );
    """

    diff_sql = "ALTER TABLE foo ADD data2 integer, ADD data3 boolean;\n"

    assert generate_sql_diff(old_sql, new_sql) == diff_sql


def test_sql_diff_add_remove_table_change_columns():

    old_sql = """
        CREATE TABLE foo (
            id serial,
            data1 text
        );

        CREATE TABLE baz (
            pk serial,
            data3 text
        )"""

    new_sql = """
        CREATE TABLE bar (
            id serial,
            data2 text
        );

        CREATE TABLE baz (
            pk serial,
            data3 text,
            data4 integer,
            data5 boolean
        );
    """

    diff_sql = """CREATE TABLE bar (id serial, data2 text);
ALTER TABLE baz ADD data4 integer, ADD data5 boolean;
DROP TABLE foo;
"""

    assert generate_sql_diff(old_sql, new_sql) == diff_sql
