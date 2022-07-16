import os

import mysql
from mysql.connector import MySQLConnection, Error


def create_db_connection(host_name: str, user_name: str, user_password: str,
                         db_name: str) -> MySQLConnection:
    """ Create a connection to the database stored in <host_name> with name
    <db_name>, and credentials <user_name> and <user_password>.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection


def execute_query(connection: MySQLConnection, query: str) -> None:
    """ Using a <connection> to a database, execute <query>.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")


def execute_search_query(connection: MySQLConnection, query: str) -> list:
    """ Using a <connection> to a database, execute <query>.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        print("Query successful")
        return records
    except Error as err:
        print(f"Error: '{err}'")




