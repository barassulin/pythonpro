import pymysql

class Database:
    def __init__(self, host, user, password, database):
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        """
        self.connection = pymysql.connect(
            host = host,
            user=user,
            password=password,
            db=database
        )

    def create_cursor(self):
        cursor = self.connection.cursor()
        return cursor

    def add_to_db(self, cursor, table_name, values):
        try:
            sql = f"INSERT INTO {table_name} VALUES ({values})"
            cursor.execute(sql)
            self.connection.commit()
            return True
        except Exception as e:
            # log
            return False

    def read_from_db(self, cursor, table_name, rows):
        sql = f"SELECT {rows} FROM {table_name}"
        cursor.execute(sql)
        myresult = cursor.fetchall()
        return myresult

    def remove_from_db(self, cursor, table_name, condition):
        try:
            sql = f"DELETE FROM {table_name} WHERE ({condition})"
            cursor.execute(sql)
            self.connection.commit()
            return True
        except Exception as e:
            # log
            return False


    def client_idedtify(self, cursor, name, password, ws_pass):
        try:
            sql = (f"select c_password from clients where name = {name} and workspace_id = (select id from workspaces"
                   f" where ws_pass = {ws_pass})")
            cursor.execute(sql)
            myresult = cursor.fetchall()
            if myresult == password:
                return True
        except Exception as e:
            # log
            print('log')
        return False

    def read_all_t(self, cursor):
        sql = f'show * tables in {self.database}'
        cursor.execute(sql)
        myresult = cursor.fetchall()
        return myresult

    def update_val_in_db(self, cursor, table_name, values, condition):
        try:
            sql = f"UPDATE {table_name} SET {values} WHERE {condition}"
            cursor.execute(sql)
            self.connection.commit()
            return True
        except Exception as e:
            # log
            print(e)
            return False


