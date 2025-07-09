"""
This module provides a reusable function to connect
to a MySQL database using environment variables.
"""

import mysql.connector
import os

def get_connection():
    """
    Establish and return a connection to the MySQL database
    using environment variables for credentials.
    """
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "newpassword"),
        database=os.getenv("MYSQL_DB", "agric_scout"),
        port=int(os.getenv("MYSQL_PORT", "3306"))
    )

