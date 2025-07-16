import psycopg2

def get_connection():
    return psycopg2.connect(
        host="dpg-d1qhq52dbo4c73chohd0-a.oregon-postgres.render.com",
        port="5432",
        user="agric_scout_user",
        password="LM2YYoWqUkEAXAMlCVzWLub8fBVEWXbd",
        database="agric_scout"
    )



