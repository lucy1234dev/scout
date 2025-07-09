# db_config.py

import mysql.connector

def get_connection():
    """Connect to Railway-hosted MySQL database"""
    return mysql.connector.connect(
        host="switchyard.proxy.rlwy.net",
        user="root",
        password="IfsINkrIvQAOjPQLMptkOZyfvLXdAsSS",
        database="railway",
        port=58798
    )


