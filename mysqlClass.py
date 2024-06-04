import sys
from mysql.connector import Error
from mysql.connector import pooling


class MySQLClass:
    __instance = None

    def getInstance():
        """ Static access method. """
        if MySQLClass.__instance == None:
            MySQLClass()
        return MySQLClass.__instance

    def __init__(self):
        if MySQLClass.__instance != None:
            print("Already set ")
        else:
            try:
                self.myConnectionPool = pooling.MySQLConnectionPool(pool_name="face_recognition_pool",
                                                                    pool_size=5,
                                                                    pool_reset_session=True,
                                                                    host='localhost',
                                                                    database='face_recognition',
                                                                    user='root',
                                                                    password='Adhawk01')

                print("Printing connection pool properties ")
                print("Connection Pool Name - ", self.myConnectionPool.pool_name)
                print("Connection Pool Size - ", self.myConnectionPool.pool_size)
                # self.update_query("SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''))", "dummy")
                MySQLClass.__instance = self

            except Error as e:
                print("Error while connecting to MySQL using Connection pool ", e)

    def select_query(self, query, params, user):
        globals()[f"Connect_object_{user}"] = self.myConnectionPool.get_connection()
        print(query)
        if globals()[f"Connect_object_{user}"].is_connected():
            try:
                my_cursor = globals()[f"Connect_object_{user}"].cursor()
                my_cursor.execute(query, params)
            except Error as e:
                print("Error while creating cursor and executing ", e)
        results_list = []
        for row in my_cursor:
            results_list.append(row)
        if globals()[f"Connect_object_{user}"].is_connected():
            my_cursor.close()
            print("returning " + str(type(results_list)))
            globals()[f"Connect_object_{user}"].close()

        return results_list

    def update_query(self, query, params, user):
        globals()[f"Connect_object_{user}"] = self.myConnectionPool.get_connection()
        print(query)
        if globals()[f"Connect_object_{user}"].is_connected():
            try:
                my_cursor = globals()[f"Connect_object_{user}"].cursor()
                my_cursor.execute(query, params)
            except Error as e:
                print("Error while creating cursor and executing ", e)

        globals()[f"Connect_object_{user}"].commit()
        globals()[f"Connect_object_{user}"].close()
        return True

    def check(self, query, user):
        globals()[f"Connect_object_{user}"] = self.myConnectionPool.get_connection()
        print(query)
        try:
            my_cursor = globals()[f"Connect_object_{user}"].cursor()
            my_cursor.execute(query)
        except Error as e:
            print("Error while creating cursor and executing ", e)

        num_of_records = 0
        for row in my_cursor:
            num_of_records = num_of_records + 1

        globals()[f"Connect_object_{user}"].close()

        if num_of_records > 0:
            return True
        else:
            return False
