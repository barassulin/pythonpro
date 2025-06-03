"""
    Bar Assulin ~ 24/5/2025
    class for handling my sql database
"""

import mysql.connector


class Database:
    """
    A class for handling MySQL database operations related to admins, clients, and apps.

    Methods:
    - create_cursor(): Creates a prepared cursor for executing parameterized queries.
    - add_to_db(): Inserts data into a specified table (admins, apps, clients).
    - password_from_db(): Retrieves a hashed password from the database.
    - get_id(): Gets the ID of a record given its name.
    - get_name(): Gets the name of a record given its ID.
    - get_admins_id(): Retrieves the admin ID associated with a given record.
    - list_from_db(): Returns a list of names or SIDs from a specified table.
    - remove_from_db(): Deletes a record by ID.
    - update_sid(): Updates the SID value of a client.
    - list_to_list(): Converts a list of names to a list of dicts with ID and name.
    """

    def __init__(self, host, user, password, database):
        """
        Initializes the database connection.

        Parameters:
        - host (str): Hostname or IP of the MySQL server.
        - user (str): Username for the database.
        - password (str): Password for the database user.
        - database (str): Name of the database to connect to.
        """
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            db=database
        )

    def create_cursor(self):
        """
        Creates a prepared cursor for executing parameterized queries.

        Returns:
        - cursor (MySQLCursor): A prepared cursor object.
        """
        return self.connection.cursor(prepared=True)

    def add_to_db(self, cursor, tuplei, table):
        """
        Inserts a new record into the specified table.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - tuplei (tuple): The values to insert.
        - table (str): Table name ('admins', 'apps', or 'clients').

        Returns:
        - 'True' if insert succeeded, 'False' otherwise.
        """
        if table == 'admins':
            print("before hash: ", tuplei[1])
            print("apter hash: ", tuplei[1])
            sql_insert_query = "INSERT INTO admins (name, a_password) VALUES (%s,%s)"

        elif table == 'apps':
            sql_insert_query = "INSERT INTO apps (name, admins_id) VALUES (%s,%s)"
        elif table == 'clients':
            sql_insert_query = "INSERT INTO clients (name, c_password, admins_id) VALUES (%s,%s,%s)"
        else:
            return 'False'

        try:
            cursor.execute(sql_insert_query, tuplei)
            self.connection.commit()
            print(f"Data inserted successfully into {table} table")
            return 'True'
        except mysql.connector.Error as error:
            print(f"Parameterized query failed: {error}")
            return 'False'

    def password_from_db(self, cursor, table_name, value):
        """
        Retrieves a password from the specified table.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - table_name (str): 'admins' or 'clients'.
        - value (tuple): The WHERE clause parameters.

        Returns:
        - Password value (hashed).
        """
        sqls = ''
        if table_name == 'admins':
            sqls = "SELECT a_password FROM admins WHERE name=%s"
        elif table_name == 'clients':
            sqls = "SELECT c_password FROM clients WHERE name=%s and admins_id=%s"
        cursor.execute(sqls, value)
        result = cursor.fetchall()
        print('this worked')
        print(result)
        return result

    def get_id(self, cursor, table, value):
        """
        Retrieves the ID of a record given its name.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - table (str): Table name.
        - value (tuple): The name to look up.

        Returns:
        - List of tuples containing the ID(s).
        """
        sql = f"SELECT id FROM {table} WHERE name=%s"
        cursor.execute(sql, value)
        return cursor.fetchall()

    def get_name(self, cursor, table, value):
        """
        Retrieves the name of a record given its ID.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - table (str): Table name.
        - value (tuple): The ID to look up.

        Returns:
        - List of tuples containing the name(s).
        """
        sql = f"SELECT name FROM {table} WHERE id=%s"
        cursor.execute(sql, value)
        return cursor.fetchall()

    def get_admins_id(self, cursor, table, value):
        """
        Retrieves the admins_id associated with a record.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - table (str): Table name.
        - value (tuple): ID value.

        Returns:
        - List of tuples containing the admins_id.
        """
        sql = f"SELECT admins_id FROM {table} WHERE id=%s"
        cursor.execute(sql, value)
        return cursor.fetchall()

    def get_sid(self, cursor, value):
        """
        Retrieves the sid associated with a record.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - value (tuple): ID value.

        Returns:
        - List of tuples containing the sid.
        """
        sql = f"SELECT sid FROM clients WHERE id=%s"
        cursor.execute(sql, value)
        return cursor.fetchall()

    def list_from_db(self, cursor, table_name, row, value):
        """
        Returns a list of items (name or sid) from a table based on admins_id.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - table_name (str): Table name ('apps' or 'clients').
        - row (str): Column to fetch ('name' or 'sid').
        - value (tuple): WHERE value (e.g. admins_id).

        Returns:
        - List of tuples containing the requested values.
        """
        if table_name == 'apps':
            sql = "SELECT name FROM apps WHERE admins_id=%s"
        elif table_name == 'clients' and row == 'name':
            sql = "SELECT name FROM clients WHERE admins_id=%s"
        elif table_name == 'clients' and row == 'sid':
            sql = "SELECT sid FROM clients WHERE admins_id=%s"
        else:
            return 'False'

        cursor.execute(sql, value)
        return cursor.fetchall()

    def remove_from_db(self, cursor, table_name, tuplei):
        """
        Deletes a record from the database by ID.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - table_name (str): Table name.
        - tuple (tuple): Tuple containing the ID to delete.

        Returns:
        - True if deletion succeeded, False otherwise.
        """
        sql = f"DELETE FROM {table_name} WHERE id=%s"
        try:
            cursor.execute(sql, tuplei)
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def update_sid(self, cursor, values):
        """
        Updates the SID of a client.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - values (tuple): (sid, name, c_password)

        Returns:
        - True if update succeeded, False otherwise.
        """
        try:
            #            values = (values[0], values[1], hash(values[2]))
            sql = "UPDATE clients SET sid=%s WHERE name=%s and c_password=%s"
            cursor.execute(sql, values)
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def list_to_list(self, cursor, listi, table):
        """
        Converts a list of names to a list of dictionaries with ID and name.

        Parameters:
        - cursor: Prepared MySQL cursor.
        - list (list): List of names.
        - table (str): Table name.

        Returns:
        - List of dicts: [{'id': id, 'name': name}, ...]
        """
        return [{"id": self.get_id(cursor, table, name)[0], "name": name} for name in listi]
