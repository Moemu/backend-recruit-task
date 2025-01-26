import sqlite3,os,time
import hashlib

class Database:
    def __init__(self) -> None:
        if not os.path.isfile('database.db'):
            self.__create_database()
            self.__init_room()
            self.__init_room_type()

    def __create_database(self) -> None:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        # 用户表
        cursor.execute('''CREATE TABLE USER(
            ID INT PRIMARY KEY NOT NULL,
            NAME TEXT NOT NULL,
            PASSWORD TEXT NOT NULL,
            PERMISSION INT NOT NULL,
            BALANCE NUMERIC NOT NULL);''')
        # 房间表
        cursor.execute('''CREATE TABLE ROOM(
            ID INT PRIMARY KEY NOT NULL,
            TYPE INT NOT NULL,
            STATUS INT NOT NULL);''')
        # 房间类型表
        cursor.execute('''CREATE TABLE ROOMTYPE(
            ID INT PRIMARY KEY NOT NULL,
            NAME TEXT NOT NULL,
            PRICE NUMERIC NOT NULL);''')
        # 预订表
        cursor.execute('''CREATE TABLE BOOKINGS(
            ID INT PRIMARY KEY NOT NULL,
            USERID INT NOT NULL,
            ROOMID INT NOT NULL,
            DATE TEXT NOT NULL,
            PRICE NUMERIC NOT NULL,
            STATUS INT NOT NULL);''')
        connection.commit()
        connection.close()

    def __init_room(self) -> None:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        for floor in range(1, 6):
            for room in range(1, 11):
                if room in [1, 2, 3]:
                    cursor.execute('''INSERT INTO ROOM (ID, TYPE, STATUS) VALUES (?, ?, ?);''', (floor * 100 + room, 2, 1)) # 双人间
                else:
                    cursor.execute('''INSERT INTO ROOM (ID, TYPE, STATUS) VALUES (?, ?, ?);''', (floor * 100 + room, 1, 1)) # 单人间
        connection.commit()
        connection.close()

    def __init_room_type(self) -> None:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f'''INSERT INTO ROOMTYPE VALUES (1, '单人间', 100.0);''')
        cursor.execute(f'''INSERT INTO ROOMTYPE VALUES (2, '双人间', 150.0);''')
        connection.commit()
        connection.close()

    def __get_lastest_id(self, TABLE:str = 'USER') -> int:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        data_cursor = cursor.execute(f'''SELECT * FROM {TABLE} ORDER BY ID DESC LIMIT 1''')
        lastest_id = 0
        for data in data_cursor:
            lastest_id = data[0]
        connection.close()
        return lastest_id
    
    def add_user(self, Username:str, Password:str, Permission:int = 0):
        # 添加用户
        available_id = self.__get_lastest_id() + 1
        secure_password = hashlib.md5(Password.encode()).hexdigest()
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f'''INSERT INTO USER VALUES (?, ?, ?, ?, 0);''', (available_id, Username, secure_password, Permission))
        connection.commit()
        connection.close()

    def add_room(self, Roomid:int, Type:int, Status:int = 1):
        # 添加房间
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f'''INSERT INTO ROOM VALUES (?, ?, ?);''', (Roomid, Type, Status))
        connection.commit()
        connection.close()

    def add_room_type(self, Name:str, Price:float):
        # 添加房间类型
        available_id = self.__get_lastest_id('ROOMTYPE') + 1
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f'''INSERT INTO ROOMTYPE VALUES (?, ?, ?);''', (available_id, Name, Price))
        connection.commit()
        connection.close()

    def booking(self, UserID:int, RoomID:int, Date:str, Price:float) -> bool:
        # 预订
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        if cursor.execute(f'''SELECT * FROM BOOKINGS WHERE ROOMID = ? AND DATE = ? AND STATUS = 1;''',(RoomID, Date)).fetchone():
            return False
        cursor.execute(f'''INSERT INTO BOOKINGS VALUES (?, ?, ?, ?, ?, 1);''', (self.__get_lastest_id('BOOKINGS') + 1, UserID, RoomID, Date, Price))
        connection.commit()
        connection.close()
        return True

    def change_room_info(self, RoomID:int, Type:int = None, Price:int = None, Status:int = None):
        # 更改房间信息
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        if Type:
            cursor.execute(f'''UPDATE ROOM SET TYPE = ? WHERE ID = ?;''', (Type, RoomID))
        if Price:
            cursor.execute(f'''UPDATE ROOM SET PRICE = ? WHERE ID = ?;''', (Price, RoomID))
        if Status:
            cursor.execute(f'''UPDATE ROOM SET STATUS = ? WHERE ID = ?;''', (Status, RoomID))
        connection.commit()
        connection.close()

    def change_type_info(self, Type:int, Name:str = None, Price:float = None):
        # 更改房间类型信息
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        if Name:
            cursor.execute(f'''UPDATE ROOMTYPE SET NAME = ? WHERE ID = ?;''', (Name, Type))
        if Price:
            cursor.execute(f'''UPDATE ROOMTYPE SET PRICE = ? WHERE ID = ?;''', (Price, Type))
        connection.commit()
        connection.close()

    def get_available_types(self) -> list[list[int, str, float]]:
        # 获取可用房间类型
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        data_cursor = cursor.execute(f'''SELECT * FROM ROOMTYPE;''')
        types = []
        for data in data_cursor:
            types.append(data[1])
        return types

    def get_type_info(self, Type:int) -> dict:
        # 获取指定房间类型信息
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        data_cursor = cursor.execute(f'''SELECT * FROM ROOMTYPE WHERE ID = ?;''', (Type,))
        for data in data_cursor:
            return data
        return None
    
    def get_room_info(self, RoomID:int = -1) -> dict:
        # 获取指定房间信息
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        if RoomID == -1:
            data_cursor = cursor.execute(f'''SELECT * FROM ROOM;''')
            return list(data_cursor)
        else:
            data_cursor = cursor.execute(f'''SELECT * FROM ROOM WHERE ID = ?;''', (RoomID,))
        for data in data_cursor:
            return data
        return None
    
    def get_booking_info(self, BookingID:int, Userid:int) -> dict:
        # 获取预订信息
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        data_cursor = cursor.execute(f'''SELECT * FROM BOOKINGS WHERE ID = ? AND USERID = ?;''', (BookingID, Userid))
        for data in data_cursor:
            return data
        return None
    
    def delete_room(self, RoomID:int):
        # 删除房间
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f'''DELETE FROM ROOM WHERE ID = ?;''', (RoomID,))
        connection.commit()
        connection.close()

    def login(self, Username:str, Password:str) -> dict|int:
        # 登录
        secure_password = hashlib.md5(Password.encode()).hexdigest()
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        data_cursor = cursor.execute(f'''SELECT * FROM USER WHERE NAME = ? AND PASSWORD = ?;''', (Username, secure_password))
        for data in data_cursor:
            return data
        return -1
    
    def check_room_is_avaliabe(self, RoomID:int, Date:str) -> bool:
        # 检查房间是否可用
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        data_cursor = cursor.execute(f'''SELECT * FROM BOOKINGS WHERE ROOMID = ? AND DATE = ? AND STATUS = 1;''', (RoomID, Date))
        for data in data_cursor:
            return False
        return True
    
    def cancel_booking(self, BookingID:int) -> bool:
        # 取消预订
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f'''UPDATE BOOKINGS SET STATUS = 0 WHERE ID = ?;''', (BookingID,))
        connection.commit()
        connection.close()
        return True

    def recharge(self, UserID:int, Money:float) -> bool:
        # 充值
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f'''UPDATE USER SET BALANCE = BALANCE + ? WHERE ID = ?;''', (Money, UserID))
        connection.commit()
        connection.close()
        return True

    def show_booking(self, UserID:int = -1) -> list:
        # 查看预订
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        if UserID == -1:
            data_cursor = cursor.execute(f'''SELECT * FROM BOOKINGS;''')
        else:
            data_cursor = cursor.execute(f'''SELECT * FROM BOOKINGS WHERE USERID = ? AND STATUS = 1;''', (UserID,))
        bookings = []
        for data in data_cursor:
            bookings.append(data)
        return bookings