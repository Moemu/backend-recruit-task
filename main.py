from sqlite import Database
from custom_types import *
from utils import *
import signal
import os

db = Database()

def signal_handler(sig, frame):
    print('退出系统...')
    exit()

signal.signal(signal.SIGINT, signal_handler)

class App:
    def __init__(self):
        self.user:User = None

    def welcome(self): 
        print('-' * 20) 
        print('欢迎进入酒店管理系统')
        print('1. 登录')
        print('2. 注册')
        print('0. 退出')
        print('-' * 20)
        choice = input('请选择：')
        os.system('cls')
        if choice == '1':
            self.login()
        elif choice == '2':
            self.register()
        elif choice == '0':
            exit()
        else:
            print('输入有误，请重新输入')
            self.welcome()
        return

    def login(self):
        print('-'*9, '登录', '-'*9)
        username = input('请输入用户名：')
        password = input('请输入密码：')
        login_result = db.login(username, password)
        if login_result == -1:
            print('用户名或密码错误')
            self.welcome()
            return
        self.user = User(login_result)
        os.system('cls')
        if self.user.permission == 1:
            self.admin_menu()
        else:
            self.main_menu()
        return

    def register(self):
        print('-'*9, '注册', '-'*9)
        username = input('请输入用户名：')
        password = input('请输入密码：')
        db.add_user(username, password)
        print('注册成功')
        os.system('cls')
        self.login()
    
    def main_menu(self):
        print(f'欢迎您，{self.user.name}，您的账户余额为 {self.user.balance:.2f} 元')
        print('-'*8, '主菜单', '-'*8)
        print('1. 查看房间')
        print('2. 预订房间')
        print('3. 查看订单')
        print('4. 退订')
        print('5. 充值')
        print('0. 退出')
        choice = input('请选择：')
        os.system('cls')
        if choice == '1':
            self.show_room()
        elif choice == '2':
            self.book_room()
        elif choice == '3':
            self.show_booking()
        elif choice == '4':
            self.cancel_booking()
        elif choice == '5':
            self.recharge()
        elif choice == '0':
            self.welcome()
        else:
            print('输入有误，请重新输入')
            self.main_menu()

    def show_room(self):
        print('-'*8, '房间列表', '-'*8)
        rooms = db.get_room_info()
        for room in rooms:
            room = Room(room)
            status = '维护' if room.booking_status == 0 else '可用' if room.booking_status == 1 else '已订'
            print(f'房间号：{room.id}，类型：{room.type_name}，价格：{room.price}，状态：{status}')
        input('按任意键返回')
        os.system('cls')
        self.main_menu()

    def book_room(self):
        print('-'*8, '预订房间', '-'*8)
        room_id = input('请输入房间号：')
        is_valid, room_id = check_value(room_id, 'int')
        if not is_valid:
            print('房间号输入有误，请重新输入')
            self.book_room()
            return
        date = input('请输入日期(格式：年.月.日)：')
        is_valid, date = check_value(date, 'date')
        if not is_valid:
            print('时间格式输入有误，请重新输入')
            self.book_room()
            return
        room = db.get_room_info(room_id)[0]
        if not room:
            print('房间不存在')
            input('按任意键返回')
            os.system('cls')
            self.main_menu()
            return
        room = Room(room)
        print(f'您即将要预定房间为：{room.id}，类型：{room.type_name}，价格：{room.price}，日期：{date}')
        print('[Y. 确认预订] N. 取消预订')
        if input('请选择：').upper() == 'N':
            os.system('cls')
            print('已取消预订')
            self.main_menu()
        if self.user.balance < room.price:
            print('余额不足')
            input('按任意键返回')
            os.system('cls')
            self.main_menu()
            return
        if db.booking(self.user.id, room_id, date, room.price):
            db.recharge(self.user.id, -room.price)
            self.user.balance -= room.price
            print('预订成功')
        else:
            print('预订失败，房间被预订或维护')
        input('按任意键返回')
        os.system('cls')
        self.main_menu()

    def show_booking(self, admin = False):
        print('-'*8, '订单列表', '-'*8)
        if admin:
            bookings = db.show_bookings()
        else:
            bookings = db.show_bookings(self.user.id)
        if not bookings:
            print('暂无订单')
            input('按任意键返回')
            os.system('cls')
            self.main_menu()
            return
        for booking in bookings:
            print(f'订单号：{booking[0]}，房间号：{booking[2]}，日期：{booking[3]}，金额：{booking[4]}')
        input('按任意键返回')
        os.system('cls')
        self.main_menu()

    def cancel_booking(self):
        print('-'*9, '退订', '-'*9)
        print('当前的订单列表：')
        bookings = db.show_bookings(self.user.id)
        if not bookings:
            print('暂无订单')
            input('按任意键返回')
            os.system('cls')
            self.main_menu()
            return
        for booking in bookings:
            print(f'订单号：{booking[0]}，房间号：{booking[2]}，日期：{booking[3]}，金额：{booking[4]}')
        booking_id = input('请输入订单号：')
        is_valid, booking_id = check_value(booking_id, 'int')
        if not is_valid:
            print('订单号输入有误，请重新输入')
            self.cancel_booking()
            return
        booking = db.get_booking_info(booking_id, self.user.id)
        if not booking:
            print('订单不存在')
            input('按任意键返回')
            os.system('cls')
            self.main_menu()
            return
        db.cancel_booking(booking_id)
        db.recharge(self.user.id, booking[4])
        self.user.balance += booking[4]
        print('退房成功，已退款')
        input('按任意键返回')
        os.system('cls')
        self.main_menu()

    def recharge(self):
        print('-'*9, '充值', '-'*9)
        amount = input('请输入充值金额：')
        is_valid, amount = check_value(amount, 'float')
        if not is_valid:
            print('金额输入有误，请重新输入')
            self.recharge()
            return
        db.recharge(self.user.id, amount)
        self.user.balance += amount
        print('充值成功')
        input('按任意键返回')
        os.system('cls')
        self.main_menu()

    def admin_menu(self):
        print(f'欢迎您，{self.user.name}')
        print('-'*7, '管理员菜单', '-'*7)
        print('1. 添加房间')
        print('2. 删除房间')
        print('3. 更改房间信息')
        print('4. 增加房间类型')
        print('5. 修改类型信息')
        print('0. 退出')
        print('-'*25)
        choice = input('请选择：')
        os.system('cls')
        if choice == '1':
            self.add_room()
        elif choice == '2':
            self.delete_room()
        elif choice == '3':
            self.change_room_status()
        elif choice == '4':
            self.add_room_type()
        elif choice == '5':
            self.change_type_info()
        elif choice == '0':
            self.welcome()
        else:
            print('输入有误，请重新输入')
            self.admin_menu()

    def add_room(self):
        print('-'*8, '添加房间', '-'*8)
        room_id = input('请输入房间号：')
        is_valid, room_id = check_value(room_id, 'int')
        if not is_valid:
            print('房间号输入有误，请重新输入')
            self.add_room()
            return
        if db.get_room_info(room_id):
            print('房间已存在')
            input('按任意键返回')
            os.system('cls')
            self.admin_menu()
            return
        available_types = db.get_available_room_types()
        available_types = [room_type[1] for room_type in available_types]
        print(f"可用房间类型：{'、'.join([str(index + 1) + '-' + value for index,value in enumerate(available_types)]) }")
        room_type = input('请输入房间类型对应的ID：')
        is_valid, room_type = check_value(room_type, 'int')
        if not is_valid:
            print('类型ID输入有误，请重新输入')
            self.add_room()
            return
        db.add_room(room_id, room_type)
        print('添加成功')
        input('按任意键返回')
        os.system('cls')
        self.admin_menu()

    def delete_room(self):
        print('-'*8, '删除房间', '-'*8)
        room_id = input('请输入房间号：')
        is_valid, room_id = check_value(room_id, 'int')
        if not is_valid:
            print('房间号输入有误，请重新输入')
            self.delete_room()
            return
        if not db.get_room_info(room_id):
            print('房间不存在')
            input('按任意键返回')
            os.system('cls')
            self.admin_menu()
            return
        db.delete_room(room_id)
        print('删除成功')
        input('按任意键返回')
        os.system('cls')
        self.admin_menu()

    def change_room_status(self):
        print('-'*7, '更改房间信息', '-'*7)
        room_id = input('请输入房间号：')
        is_valid, room_id = check_value(room_id, 'int')
        if not is_valid:
            print('房间号输入有误，请重新输入')
            self.change_room_status()
            return
        if not db.get_room_info(room_id):
            print('房间不存在')
            input('按任意键返回')
            os.system('cls')
            self.admin_menu()
            return
        status = input('请输入状态(0-维护，1-可用)：')
        is_valid, status = check_value(status, 'int')
        if not is_valid or status not in [0, 1]:
            print('状态输入有误，请重新输入')
            self.change_room_status()
        type_id = input('请输入房间类型ID：')
        is_valid, type_id = check_value(type_id, 'int')
        if not is_valid or not db.get_room_type_info(type_id):
            print('类型ID输入有误，请重新输入')
            self.change_room_status()
            return
        db.update_room(room_id, status=status, room_type=type_id)
        print('更改成功')
        input('按任意键返回')
        os.system('cls')
        self.admin_menu()

    def add_room_type(self):
        print('-'*7, '增加房间类型', '-'*7)
        room_type_name = input('请输入房间类型名称：')
        room_price = input('请输入房间价格：')
        is_valid, room_price = check_value(room_price, 'float')
        if not is_valid or room_price <= 0 or room_type_name == '':
            print('类型名称或价格输入有误，请重新输入')
            self.add_room_type()
            return
        db.add_room_type(room_type_name, room_price)
        print('添加成功')
        input('按任意键返回')
        os.system('cls')
        self.admin_menu()

    def change_type_info(self):
        print('-'*7, '修改类型信息', '-'*7)
        available_types = db.get_available_room_types()
        available_types = [room_type[1] for room_type in available_types]
        print(f"可用房间类型：{'、'.join([str(index + 1) + '-' + value for index,value in enumerate(available_types)]) }")
        room_type = input('请输入房间类型ID：')
        is_valid, room_type = check_value(room_type, 'int')
        if not is_valid or room_type not in range(1, len(available_types) + 1):
            print('类型ID输入有误，请重新输入')
            self.change_type_info()
            return
        if not db.get_room_type_info(room_type):
            print('类型不存在')
            input('按任意键返回')
            os.system('cls')
            self.admin_menu()
            return
        room_type_name = input('请输入房间类型名称：')
        room_price = input('请输入房间价格：')
        is_valid, room_price = check_value(room_price, 'float')
        if not is_valid or room_price <= 0 or room_type_name == '':
            print('类型名称或价格输入有误，请重新输入')
            self.change_type_info()
            return
        db.update_room_type(room_type, room_type_name, room_price)
        print('更改成功')
        input('按任意键返回')
        os.system('cls')
        self.admin_menu()


if __name__ == '__main__':
    app = App()
    app.welcome()