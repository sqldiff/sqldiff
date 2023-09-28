import pytest

from sqldiff.sqldiff import generate_sql_diff


def test_sql_diff_add_table():

    old_sql = ""

    new_sql = """
CREATE TABLE foo (
    id serial,
    data1 text,
    data2 integer
);"""

    diff_sql = """
CREATE TABLE foo (
    id serial,
    data1 text,
    data2 integer
);"""

    assert generate_sql_diff(old_sql, new_sql) == diff_sql


def test_sql_diff_remove_table():

    old_sql = """
CREATE TABLE foo (
    id serial,
    data1 text,
    data2 integer
);"""

    new_sql = ""

    diff_sql = "DROP TABLE foo;"

    assert generate_sql_diff(old_sql, new_sql) == diff_sql


def test_sql_diff_column_changed():

    old_sql = """
CREATE TABLE foo (
    id serial,
    data1 text
);"""

    new_sql = """
CREATE TABLE foo (
    id serial,
    data1 text,
    data2 integer
);"""

    diff_sql = """ALTER TABLE foo
ADD
    data2 integer"""

    # generate_sql_diff(old_sql, new_sql)
    assert generate_sql_diff(old_sql, new_sql) == diff_sql
