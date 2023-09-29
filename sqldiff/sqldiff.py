import sqlparse
from sqlparse import filters
from sqlparse.sql import Identifier, Parenthesis, Statement, Token
from sqlparse.tokens import Keyword, Operator, Punctuation, Whitespace
from typing import Dict, List


class CreateTableColumn():
    def __init__(self, token_list: List[Token]):
        self.token_list: List[Token] = token_list


class CreateTableClause():
    def __init__(self, table_name_token, statement):
        self.table_name_token: Identifier = table_name_token
        self.statement: Statement = statement
        self.columns: Dict[str, CreateTableColumn] = {}

    def populate_columns(self, column_tokens: Parenthesis) -> None:
        if column_tokens.tokens[0].ttype != Punctuation:
            raise RuntimeError("Expect column_tokens starts with Punctuation '('")
        column_left_index = 1

        for index, token in enumerate(column_tokens.tokens[1:]):
            if token.ttype == Punctuation:
                _, column_name_token = column_tokens.token_next(column_left_index, skip_cm=True)
                self.columns[column_name_token.value] = CreateTableColumn(
                    column_tokens.tokens[column_left_index:index+1])
                column_left_index = index + 2

    def add_columns(self, base_create_table_clause) -> List[CreateTableColumn]:
        if self.table_name_token.value != base_create_table_clause.table_name_token.value:
            raise RuntimeError("Can't compare columns for different tables")

        add_columns = []
        for column_name, column in self.columns.items():
            if column_name not in base_create_table_clause.columns.keys():
                add_columns.append(column)

            # TODO: what about if column constrains are changed?
        return add_columns

    def remove_columns(self, base_create_table_clause) -> List[CreateTableColumn]:
        raise NotImplementedError


class Clauses():

    sql_filters = [
        filters.StripCommentsFilter(),
        filters.StripWhitespaceFilter(),
        filters.SpacesAroundOperatorsFilter()
    ]

    def __init__(self, statements):
        self.tables: Dict[str, CreateTableClause] = {}
        self.indices = {}

        for statement in statements:
            for sql_filter in self.sql_filters:
                sql_filter.process(statement)

            index, create_token = statement.token_next(0, skip_cm=True)
            if create_token.ttype != Keyword.DDL or create_token.value != "CREATE":
                raise RuntimeError("Don't support clause other than CREATE")

            index, create_keyword = statement.token_next(index, skip_cm=True)
            if create_keyword.ttype != Keyword:
                raise RuntimeError("Don't support CREATE to not follow with a keyword")
            elif create_keyword.value not in ('TABLE', 'INDEX'):
                raise RuntimeError("Don't support CREATE a resource other than TABLE or INDEX")

            if create_keyword.value == "TABLE":
                index, table_name_token = statement.token_next(index, skip_cm=True)
                table = CreateTableClause(table_name_token, statement)
                self.tables[table_name_token.value] = table

                _, columns_parenthesis = statement.token_next(index, skip_cm=True)
                if not isinstance(columns_parenthesis, Parenthesis):
                    raise RuntimeError("Don't support CREATE TABLE <other keywords> ( ...")
                table.populate_columns(columns_parenthesis)

            if create_keyword.value == "INDEX":
                raise NotImplementedError

    def diff(self, base_clauses):
        sql = ""
        for table_name, create_table_clause in self.tables.items():
            if table_name not in base_clauses.tables:
                sql += str(create_table_clause.statement) + "\n"
            else:
                add_columns = create_table_clause.add_columns(base_clauses.tables[table_name])
                statement = sqlparse.parse("ALTER TABLE")[0]
                statement.tokens.append(Token(Whitespace, ' '))
                statement.tokens.append(create_table_clause.table_name_token)
                statement.tokens.append(Token(Whitespace, ' '))

                for add_column in add_columns[:-1]:
                    statement.tokens.append(sqlparse.parse("ADD")[0])
                    statement.tokens.extend(add_column.token_list)
                    statement.tokens.extend([Token(Operator, ','), Token(Whitespace, ' ')])
                add_column = add_columns[-1]
                statement.tokens.append(sqlparse.parse("ADD")[0])
                statement.tokens.extend(add_column.token_list)
                statement.tokens.append(Token(Operator, ';'))

                sql += str(statement) + "\n"

        for table_name, create_table_clause in base_clauses.tables.items():
            if table_name not in self.tables:
                statement = sqlparse.parse("DROP TABLE")[0]
                statement.tokens.append(Token(Whitespace, ' '))
                statement.tokens.append(create_table_clause.table_name_token)
                statement.tokens.append(Token(Operator, ';'))
                sql += str(statement) + "\n"

        return sql


def generate_sql_diff(old_sql: str, new_sql: str) -> str:

    old_clauses = Clauses(sqlparse.parse(old_sql))
    new_clauses = Clauses(sqlparse.parse(new_sql))

    return new_clauses.diff(old_clauses)
