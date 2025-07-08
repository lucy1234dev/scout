"""this is a program that
serves as adatabase to send information to mysql

"""
# db_config.py

import mysql.connector


def get_connection():
    """get connection"""
    return mysql.connector.connect(
        host="localhost",
        user = "root",
        password = "newpassword",
        database = "agric_scout"
    )
