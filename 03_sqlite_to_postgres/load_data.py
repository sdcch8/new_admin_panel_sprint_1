import os
import sqlite3
from dataclasses import astuple
from dataclasses import fields as dataclass_fields

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_values

from data_classes import TABLE_CLASS_MAPPING, TABLE_FIELDS_MAPPING

BATCH_SIZE = 500
load_dotenv()


class SQLiteLoader():
    def __init__(self, connection):
        self.connection = connection

    def load_data(self):
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        for table, data_class in TABLE_CLASS_MAPPING.items():
            cursor.execute(f'SELECT * FROM {table};')
            fields = [field.name for field in dataclass_fields(data_class)]

            while True:
                batch = cursor.fetchmany(BATCH_SIZE)
                if not batch:
                    break
                for index, row in enumerate(batch):
                    batch[index] = data_class(
                        **{key: value for key, value in dict(row).items()
                           if key in fields}
                    )
                yield batch


class PostgresSaver:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def truncate_tables(self):
        for table in TABLE_CLASS_MAPPING.keys():
            self.cursor.execute(f'TRUNCATE TABLE {table} CASCADE;')

    def save_data(self, batch):
        table = batch[0].table

        fields = [field.name for field in dataclass_fields(batch[0])]
        fields = [TABLE_FIELDS_MAPPING[field]
                  if field in TABLE_FIELDS_MAPPING.keys()
                  else field for field in fields]
        fields = ', '.join(fields)

        values = [astuple(row) for row in batch]

        sql_string = f'''
            INSERT INTO {table} ({fields})
            VALUES %s
            ON CONFLICT (id) DO NOTHING;'''
        execute_values(self.cursor, sql_string, values)
        self.connection.commit()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    postgres_saver.truncate_tables()

    for batch in sqlite_loader.load_data():
        postgres_saver.save_data(batch)


if __name__ == '__main__':
    dsl = {'dbname': os.environ.get('DB_NAME'),
           'user': os.environ.get('DB_USER'),
           'password': os.environ.get('DB_PASSWORD'),
           'host': os.environ.get('DB_HOST', '127.0.0.1'),
           'port': os.environ.get('DB_PORT', 5432),
           }
           
    with (sqlite3.connect('db.sqlite') as sqlite_conn,
          psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn):
        load_from_sqlite(sqlite_conn, pg_conn)
