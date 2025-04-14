
class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def create_cursor(self):
        return self.cursor()

    def add_to_db(self, cursor, table_name, values):
        try:
            sql = f"INSERT INTO {table_name} VALUES ({values})"
            cursor.execute(sql)
            self.commit()
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
            self.commit()
            return True
        except Exception as e:
            # log
            return False

