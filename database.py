
class Database:
    def __init__(self, host, user, password, database):
        self.host = host,
        self.user = user,
        self.password = password,
        self.database = database,

    def create_cursor(self):
        return self.cursor()

    def add_to_db(self, cursor, name_of_table, values):
        try:
            sql = f"INSERT INTO {name_of_table} VALUES ({values})"
            cursor.execute(sql)
            self.commit()
            return True
        except Exception as e:
            # log
            return False

    def read_from_db(self, cursor, name_of_table, rows):
        sql = f"SELECT {rows} FROM {name_of_table}"
        cursor.execute(sql)
        myresult = cursor.fetchall()
        return myresult
