"""Database utils to perform custom CRUD operations"""
import logging
from typing import List, Tuple

import psycopg2
from psycopg2.extras import DictCursor, DictRow


class DBConnectionError(Exception):
    """Raised when cannot connect to database"""


class DataNotFoundError(Exception):
    """Raised when data is not found (query returns empty result)"""


class DBUtils:

    def __init__(self,
                 host: str,
                 database: str,
                 username: str,
                 password: str) -> None:
        self._host = host
        self._database = database
        self._username = username
        self._password = password

    def get_database_connection(self):
        try:
            return psycopg2.connect(host=self._host,
                                    database=self._database,
                                    user=self._username,
                                    password=self._password)
        except (psycopg2.OperationalError, psycopg2.DatabaseError, Exception) as e:
            logging.error("Database connection error: %s", e)
            raise DBConnectionError

    def execute_select(self, query: str) -> List[Tuple]:
        """Return result from SQL select statement.
        :param query: SQL select query to execute
        :type query: str
        :return: Data
        :rtype: list
        """
        connection = self.get_database_connection()
        cur = connection.cursor()
        cur.execute(query)
        fetched_data = cur.fetchall()
        cur.close()
        connection.commit()
        return fetched_data

    def execute_select_to_list_dictrows(self, query: str) -> List[DictRow]:
        """Return result from SQL select statements as list of DictRows so can access values by column name.
        :param query: SQL select query to execute
        :type query: str
        :return: Data
        :rtype: list[psycopg2.extras.DictRow]
        """
        connection = self.get_database_connection()
        cur = connection.cursor(cursor_factory=DictCursor)
        cur.execute(query)
        fetched_data = cur.fetchall()
        cur.close()
        connection.commit()
        return fetched_data
