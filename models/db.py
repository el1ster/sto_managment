"""
Модуль для підключення до бази даних MySQL через Peewee з драйвером PyMySQL.

Всі параметри зчитуються з config.py.

"""
import pymysql

pymysql.install_as_MySQLdb()

import config
from peewee import MySQLDatabase

# Явно вказуємо драйвер PyMySQL через параметр 'driver'
db = MySQLDatabase(
    config.DB_NAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=config.DB_PORT,
    charset='utf8mb4',
    autocommit=True,
    autorollback=True
)
