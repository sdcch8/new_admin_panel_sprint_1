import os

from dotenv import load_dotenv

from data_classes import TABLE_CLASS_MAPPING
from load_data import (PostgresSaver, SQLiteLoader, get_pg_connection,
                       get_sqlite_connection)

load_dotenv()


def check_rows_count():
    dsl = {'dbname': os.environ.get('DB_NAME'),
           'user': os.environ.get('DB_USER'),
           'password': os.environ.get('DB_PASSWORD'),
           'host': os.environ.get('DB_HOST', '127.0.0.1'),
           'port': os.environ.get('DB_PORT', 5432),
           }
    with (get_sqlite_connection() as sqlite_connection,
          get_pg_connection(dsl) as pg_connection):

        sqlite = SQLiteLoader(sqlite_connection)
        postgres = PostgresSaver(pg_connection)

        for table in TABLE_CLASS_MAPPING.keys():
            sqlite.cursor.execute(f'SELECT COUNT(*) FROM {table};')
            postgres.cursor.execute(f'SELECT COUNT(*) FROM {table};')

            sql_rows_count = sqlite.cursor.fetchall()[0][0]
            postgres_rows_count = postgres.cursor.fetchall()[0][0]

            assert sql_rows_count == postgres_rows_count


def check_data():
    dsl = {'dbname': os.environ.get('DB_NAME'),
           'user': os.environ.get('DB_USER'),
           'password': os.environ.get('DB_PASSWORD'),
           'host': os.environ.get('DB_HOST', '127.0.0.1'),
           'port': os.environ.get('DB_PORT', 5432),
           }
    with (get_sqlite_connection() as sqlite_connection,
          get_pg_connection(dsl) as pg_connection):

        sqlite = SQLiteLoader(sqlite_connection)
        postgres = PostgresSaver(pg_connection)

        for table in TABLE_CLASS_MAPPING.keys():
            sqlite.cursor.execute(f'SELECT * FROM {table} ORDER BY id;')
            postgres.cursor.execute(f'SELECT * FROM {table} ORDER BY id;')

            sql_rows = sqlite.cursor.fetchall()
            postgres_rows = postgres.cursor.fetchall()

            for sql_row, postgres_row in zip(sql_rows, postgres_rows):
                fields = [field for field in postgres_row.keys()
                          if field not in ['created', 'modified']]

                for field in fields:
                    assert sql_row[field] == postgres_row[field]


check_rows_count()
check_data()
