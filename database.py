import re

import mysql.connector


class Database:
    def __init__(self, host, user, password, database):
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        """
        self.connection = mysql.connector.connect(
            host = host,
            user=user,
            password=password,
            db=database
        )

    def create_cursor(self):
        cursor = self.connection.cursor(prepared=True)
        return cursor

    def add_to_db(self, cursor, tuple, table):
        print('prob')
        if table == 'admins' :
            sql_insert_query = """ INSERT INTO admins
                                   (name, a_password) VALUES (%s,%s)"""
        elif table == 'apps':
            sql_insert_query = """ INSERT INTO apps
                                               (name, admins_id) VALUES (%s,%s)"""
        elif table == 'clients':
            print('worked')
            sql_insert_query = """ INSERT INTO clients
                                               (name, c_password, admins_id) VALUES (%s,%s,%s)"""
            print('didnt')
        else:
            return 'False'
        try:
            cursor.execute(sql_insert_query, tuple)
            self.connection.commit()
            print(f"Data inserted successfully into {table} table using the prepared statement")
            return 'True'
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
            return 'False'
        finally:
            if self.connection.is_connected():
                cursor.close()
                # self.connection.close()
            # print("MySQL connection is closed")

        """
    def add_to_db(self, cursor, table_name, values):
        try:
            sql = f"INSERT INTO {table_name} VALUES ({values})"
            cursor.execute(sql)
            self.connection.commit()
            return True
        except Exception as e:
            # log
            return False
        """

    def password_from_db(self, cursor, table_name, value):
        if table_name == 'admins':
            sql = f"""SELECT a_password FROM admins WHERE name=%s"""
        elif table_name == 'clients':
            sql = f"""SELECT c_password FROM clients WHERE name=%s and admins_id=%s"""
        cursor.execute(sql, value)
        myresult = cursor.fetchall()
        print("pass ", myresult)
        # myresult = re.split(r'[;,\s]+:', myresult)
        myresult = myresult[0][0]
        return myresult

    def get_id(self, cursor, table, value):
        sql = f"""SELECT id FROM {table} WHERE name=%s"""
        cursor.execute(sql, value)
        myresult = cursor.fetchall()
        print("pass ", myresult)
        # myresult = re.split(r'[;,\s]+:', myresult)
        #myresult = myresult[0][0]
        print(myresult)
        return myresult

    def list_from_db(self, cursor, table_name, row, value):
        if table_name=='apps':
            sql = f"""SELECT name FROM apps WHERE admins_id=%s"""
        elif table_name=='clients' and row == 'name':
            sql = f"SELECT name FROM clients WHERE admins_id=%s"
        elif table_name == 'clients' and row == 'socket':
            sql = f"SELECT socket FROM clients WHERE admins_id=%s"
        else:
            return 'False'
        cursor.execute(sql, value)
        myresult = cursor.fetchall()
        print("pass ", myresult)
        # myresult = re.split(r'[;,\s]+:', myresult)

        return myresult

    def remove_from_db(self, cursor, table_name, tuple):
        sql = f"""DELETE FROM {table_name} WHERE id=%s"""

        try:
            cursor.execute(sql, tuple)
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    """
    def client_identify(self, cursor, name, password, admin_id):
         
        #Securely check a client's password.
        
        sql = (
            "SELECT c_password "
            "FROM clients "
            "WHERE name = %s AND admins_id = %s"
        )
        cursor.execute(sql, (name, admin_id))
        row = cursor.fetchone()
        return str(bool(row and row[0] == password))
    
    
    def read_all_t(self, cursor):
        sql = f'show * tables in {self.database}'
        cursor.execute(sql)
        myresult = cursor.fetchall()
        return myresult
    """

    def update_socket(self, cursor, values):
        try:
            sql = f"UPDATE clients SET socket=%s WHERE name=%s and c_password=%s"
            cursor.execute(sql, values)
            self.connection.commit()
            return True
        except Exception as e:
            # log
            print(e)
            return False

    def list_to_list(self, cursor, list, table):
        listi = [{"id": self.get_id(cursor, table, name)[0], "name": name} for name in list]
        return listi
