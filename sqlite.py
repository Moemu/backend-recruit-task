import sqlite3
import os
import hashlib

class Database:
    DB_NAME = 'database.db'

    def __init__(self):
        if not os.path.isfile(self.DB_NAME):
            self.__create_database()
            self.__init_room()
            self.__init_room_type()

    def __connect(self):
        return sqlite3.connect(self.DB_NAME)

    def __execute(self, query, params=(), fetchone=False, fetchall=False):
        with self.__connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()
            conn.commit()

    def __create_database(self):
        queries = [
            '''CREATE TABLE USER(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NAME TEXT NOT NULL,
                PASSWORD TEXT NOT NULL,
                PERMISSION INTEGER NOT NULL,
                BALANCE REAL NOT NULL DEFAULT 0
            );''',
            '''CREATE TABLE ROOM(
                ID INTEGER PRIMARY KEY NOT NULL,
                TYPE INTEGER NOT NULL,
                STATUS INTEGER NOT NULL
            );''',
            '''CREATE TABLE ROOMTYPE(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NAME TEXT NOT NULL,
                PRICE REAL NOT NULL
            );''',
            '''CREATE TABLE BOOKINGS(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USERID INTEGER NOT NULL,
                ROOMID INTEGER NOT NULL,
                DATE TEXT NOT NULL,
                PRICE REAL NOT NULL,
                STATUS INTEGER NOT NULL
            );'''
        ]
        for query in queries:
            self.__execute(query)

    def __init_room(self):
        for floor in range(1, 6):
            for room in range(1, 11):
                room_type = 2 if room in [1, 2, 3] else 1
                self.__execute('INSERT INTO ROOM (ID, TYPE, STATUS) VALUES (?, ?, ?);', 
                               (floor * 100 + room, room_type, 1))

    def __init_room_type(self):
        self.__execute('INSERT INTO ROOMTYPE (NAME, PRICE) VALUES (?, ?);', ('单人间', 100.0))
        self.__execute('INSERT INTO ROOMTYPE (NAME, PRICE) VALUES (?, ?);', ('双人间', 150.0))

    def __get_lastest_id(self, table='USER'):
        result = self.__execute(f'SELECT MAX(ID) FROM {table};', fetchone=True)
        return result[0] if result[0] else 0

    def add_user(self, username:str, password:str, permission:int=0):
        secure_password = hashlib.sha256(password.encode()).hexdigest()
        self.__execute('INSERT INTO USER (NAME, PASSWORD, PERMISSION) VALUES (?, ?, ?);', 
                       (username, secure_password, permission))

    def add_room(self, room_id:int, room_type:int, status:int=1):
        self.__execute('INSERT INTO ROOM (ID, TYPE, STATUS) VALUES (?, ?, ?);', 
                       (room_id, room_type, status))

    def add_room_type(self, name:str, price:float):
        self.__execute('INSERT INTO ROOMTYPE (NAME, PRICE) VALUES (?, ?);', (name, price))

    def booking(self, user_id:int, room_id:int, date:str, price:float) -> bool:
        if self.__execute('SELECT 1 FROM BOOKINGS WHERE ROOMID = ? AND DATE = ? AND STATUS = 1;', 
                          (room_id, date), fetchone=True):
            return False
        self.__execute('INSERT INTO BOOKINGS (USERID, ROOMID, DATE, PRICE, STATUS) VALUES (?, ?, ?, ?, 1);', 
                       (user_id, room_id, date, price))
        return True

    def update_room(self, room_id:int, room_type:int=None, status:int=None):
        if room_type:
            self.__execute('UPDATE ROOM SET TYPE = ? WHERE ID = ?;', (room_type, room_id))
        if status:
            self.__execute('UPDATE ROOM SET STATUS = ? WHERE ID = ?;', (status, room_id))

    def update_room_type(self, type_id:int, name:str=None, price:float=None):
        if name:
            self.__execute('UPDATE ROOMTYPE SET NAME = ? WHERE ID = ?;', (name, type_id))
        if price:
            self.__execute('UPDATE ROOMTYPE SET PRICE = ? WHERE ID = ?;', (price, type_id))

    def get_available_room_types(self):
        return self.__execute('SELECT * FROM ROOMTYPE;', fetchall=True)

    def get_room_info(self, room_id:int=None):
        query = 'SELECT * FROM ROOM' if room_id is None else 'SELECT * FROM ROOM WHERE ID = ?'
        return self.__execute(query, (room_id,) if room_id else (), fetchall=True)

    def get_booking_info(self, booking_id:int, user_id:int):
        return self.__execute('SELECT * FROM BOOKINGS WHERE ID = ? AND USERID = ?;', 
                              (booking_id, user_id), fetchone=True)
    
    def get_room_type_info(self, type_id:int):
        return self.__execute('SELECT * FROM ROOMTYPE WHERE ID = ?;', (type_id,), fetchone=True)

    def delete_room(self, room_id:int):
        self.__execute('DELETE FROM ROOM WHERE ID = ?;', (room_id,))

    def login(self, username:str, password:str):
        secure_password = hashlib.sha256(password.encode()).hexdigest()
        return self.__execute('SELECT * FROM USER WHERE NAME = ? AND PASSWORD = ?;', 
                              (username, secure_password), fetchone=True) or -1

    def is_room_available(self, room_id:int, date:str):
        return not self.__execute('SELECT 1 FROM BOOKINGS WHERE ROOMID = ? AND DATE = ? AND STATUS = 1;', 
                                  (room_id, date), fetchone=True)

    def cancel_booking(self, booking_id:int):
        self.__execute('UPDATE BOOKINGS SET STATUS = 0 WHERE ID = ?;', (booking_id,))
        return True

    def recharge(self, user_id:int, amount:float):
        self.__execute('UPDATE USER SET BALANCE = BALANCE + ? WHERE ID = ?;', (amount, user_id))
        return True

    def show_bookings(self, user_id:int=None):
        query = 'SELECT * FROM BOOKINGS' if user_id is None else 'SELECT * FROM BOOKINGS WHERE USERID = ? AND STATUS = 1;'
        return self.__execute(query, (user_id,) if user_id else (), fetchall=True)
