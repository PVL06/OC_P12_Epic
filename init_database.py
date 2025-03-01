import os

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv


load_dotenv()

credentials = {
    "dbname": os.getenv('DB_APP'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PWD'),
}


def init_database():
    db_exist = _check_database_exist()
    if db_exist:
        res = input("Do you remove existing database and create new database (Y/n)? ")
        if res == "Y":
            _delete_database()
            _create_database()
        else:
            print("Stay in the same database.")
    else:
        _create_database()


# Try to connect to the application database and check if database exist
def _check_database_exist():
    try:
        conn = psycopg2.connect(**credentials)
        conn.close()
        print('Database already exist!')
        return True
    except psycopg2.OperationalError:
        return False


# Create new database for app
def _create_database():
    query = f"CREATE DATABASE {os.getenv('DB_APP')}"
    _root_query(query)
    print(f"Database {os.getenv('DB_APP')} created.")


# Delete app database
def _delete_database():
    query = f"DROP DATABASE {os.getenv('DB_APP')}"
    _root_query(query)
    print(f"Old database {os.getenv('DB_APP')} deleted.")


# Execute query on root database
def _root_query(query):
    try:
        credentials['dbname'] = os.getenv('DB_ROOT')

        conn = psycopg2.connect(**credentials)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(sql.SQL(query))
        cursor.close()
        conn.close()
    except psycopg2.OperationalError:
        print('Connexion failed! Check credentials...')

    except Exception as e:
        print(e)


if __name__ == "__main__":
    init_database()
