from sqlite import Database
from datetime import datetime

class User:
    def __init__(self, db:dict):
        self.id:int = db[0]
        self.name:str = db[1]
        self.password:str = db[2]
        self.permission:int = db[3]
        self.balance:float = db[4]

class Room:
    def __init__(self, db:dict):
        self.id:int = db[0]
        self.type:int = db[1]
        self.status:int = db[2]
        self.booking_status = self.__check_status()
        self.__get_type_info()

    def __check_status(self) -> int:
        if self.status == 0:
            return 0 # 维护
        if Database().check_room_is_avaliabe(self.id, datetime.now().strftime('%Y.%m.%d')):
            return 1 # 可用
        return 2 # 已订
    
    def __get_type_info(self):
        info = Database().get_type_info(self.type)
        self.type_name = info[1]
        self.price = info[2]