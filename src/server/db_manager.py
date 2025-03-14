import os

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from argon2 import PasswordHasher

from server.models import Base, Role, Collaborator


class DBManager:

    def __init__(self):
        load_dotenv()
        ph = PasswordHasher()
        self.db_app = os.getenv('DB_APP')
        self.db_test = os.getenv('DB_TEST')
        self.db_root = os.getenv('DB_ROOT')

        self.credentials = {
            "user": os.getenv('DB_USER'),
            "password": os.getenv('DB_PWD'),
        }

        self.engine = create_engine(f"postgresql+psycopg2://{os.getenv('DB_APP_URL')}")
        self.engine_test = create_engine(f"postgresql+psycopg2://{os.getenv('DB_TEST_URL')}")

        self.first_user = {
            "name": os.getenv('USER_NAME'),
            "email": os.getenv('USER_EMAIL'),
            "phone": os.getenv('USER_PHONE'),
            "password": ph.hash(os.getenv('USER_PASSWORD')),
            "role_id": 1
        }

    def init_database(self) -> None:
        print(f"\n ===== Database: {self.db_app} =====")

        db_exist = self._check_database_exist(self.db_app)
        if db_exist:
            print("***** WARNING *****")
            res = input("Do you remove existing database and create new empty database (Y/n)? ")
            if res == "Y":
                self._delete_database(self.db_app)
                self._create_database(self.db_app)
            else:
                print("Stay in the same database.")
        else:
            self._create_database(self.db_app)

    def init_test_database(self) -> None:
        db_exist = self._check_database_exist(self.db_test)
        if db_exist:
            self._delete_database(self.db_test)
        self._create_database(self.db_test, test=True)

    def stop_test_db(self) -> None:
        self.engine_test.dispose()
        self.engine.dispose()
        self._delete_database(self.db_test)

    def get_session(self) -> sessionmaker:
        return sessionmaker(self.engine)

    def get_test_session(self) -> sessionmaker:
        return sessionmaker(self.engine_test)

    # Try to connect to the database and check if database exist
    def _check_database_exist(self, db_name: str) -> bool:
        try:
            conn = psycopg2.connect(dbname=db_name, **self.credentials)
            conn.close()
            print('Database already exist!')
            return True
        except psycopg2.OperationalError:
            return False

    # Create new database
    def _create_database(self, db_name: str, test=False) -> None:
        print(f"\n ===== Create database: {db_name} =====")
        query = f"CREATE DATABASE {db_name}"
        if self._root_query(query):
            print(f"New database {db_name} created.")
            Base.metadata.create_all(self.engine_test if test else self.engine)
            self._add_roles_and_first_user(test=test)

    # add role values and first user in database
    def _add_roles_and_first_user(self, test=False) -> None:
        roles = [
            Role(role="gestion"),
            Role(role="commercial"),
            Role(role="support")
        ]
        user = Collaborator(**self.first_user)
        Session = sessionmaker(self.engine_test if test else self.engine)
        try:
            with Session.begin() as session:
                session.add_all(roles)
                session.add(user)
        except Exception as e:
            print("Error in database:")
            print(e)
            self._delete_database(self.db_app)

    # Delete database
    def _delete_database(self, db_name: str) -> None:
        print(f"\n ===== Deleted database {db_name} =====")
        query = f"DROP DATABASE {db_name}"
        if self._root_query(query):
            print(f"Old database {db_name} deleted.")

    # Execute query on root database
    def _root_query(self, query: str) -> bool:
        try:
            conn = psycopg2.connect(dbname=self.db_root, **self.credentials)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            cursor.execute(sql.SQL(query))
            cursor.close()
            conn.close()
            return True
        except psycopg2.OperationalError:
            print('Connexion failed! Check credentials...')
            return False
        except Exception as e:
            print(e)
            return False
