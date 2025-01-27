# 介绍

本项目是一个酒店管理系统，旨在提供用户注册、登录、预订房间、查看订单、退订和充值等功能。管理员可以添加、删除房间，修改房间信息，增加房间类型和修改类型信息。

# 功能

- 用户注册
- 用户登录
- 查看房间列表
- 预订房间
- 查看订单
- 退订房间
- 账户充值
- 管理员添加房间
- 管理员删除房间
- 管理员更改房间信息
- 管理员增加房间类型
- 管理员修改房间类型信息

# 技术栈

本项目使用 Python 语言开发，主要用到了以下语法和特性：

- 类和对象：使用类来封装用户、房间数据。
- 类型注解：为函数参数和返回值添加类型注解，提高代码可读性和可维护性。
- 信号处理：使用 signal 模块处理系统信号，实现优雅退出。
- 数据库操作：使用自定义的 Database 类与 SQLite 数据库进行交互，存储和查询用户、房间、订单等信息。
- 数据验证：通过自定义的 check_value 函数验证用户输入的数据是否合法。
- 控制流：使用 if-elif-else 语句和循环语句控制程序流程，根据用户输入执行相应的操作。
- 格式化输出：使用 f-string 格式化字符串，输出用户信息、房间信息、订单信息等。

# 提示

修改数据库 `database.db` 中的 `USER` 表下的 `PERMISSION` 为 1 可将此用户更改为管理员。