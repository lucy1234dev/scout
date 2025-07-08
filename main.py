"""
FastAPI User Auth API for Agric Scout
- Register users
- Login with email
- Update email
- Update password

This version is production-ready and Pylint compliant.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import bcrypt
from mysql.connector import Error
from db_config import get_connection

app = FastAPI()


# -------------------- Models --------------------
class RegisterRequest(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdateEmailRequest(BaseModel):
    email: EmailStr
    password: str
    new_email: EmailStr


class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    current_password: str
    new_password: str


# -------------------- Endpoints --------------------
@app.post("/register")
def register_user(data: RegisterRequest):
    """Register a new user."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already exists.")

        hashed_pw = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (firstname, lastname, email, password) VALUES (%s, %s, %s, %s)",
            (data.firstname, data.lastname, data.email, hashed_pw.decode("utf-8")),
        )
        conn.commit()
        return {"message": "Registration successful."}

    except Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if conn:
            conn.close()


@app.post("/login")
def login_user(data: LoginRequest):
    """Authenticate and log a user in."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(data.password.encode("utf-8"), user[4].encode("utf-8")):
            cursor.execute("INSERT INTO login_logs (user_id) VALUES (%s)", (user[0],))
            conn.commit()
            return {"message": f"Login successful. Welcome, {user[1]} {user[2]}!"}

        raise HTTPException(status_code=401, detail="Invalid email or password.")

    except Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if conn:
            conn.close()


@app.put("/update-email")
def update_email(data: UpdateEmailRequest):
    """Update user's email address."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(data.password.encode("utf-8"), user[4].encode("utf-8")):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        if data.new_email == data.email:
            raise HTTPException(status_code=400, detail="New email is the same as current.")

        cursor.execute("SELECT * FROM users WHERE email = %s", (data.new_email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="New email already in use.")

        cursor.execute("UPDATE users SET email = %s WHERE id = %s", (data.new_email, user[0]))
        cursor.execute(
            "INSERT INTO update_logs (user_id, field_changed, old_value, new_value) VALUES (%s, %s, %s, %s)",
            (user[0], "email", data.email, data.new_email),
        )
        conn.commit()
        return {"message": "Email updated successfully."}

    except Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if conn:
            conn.close()


@app.put("/update-password")
def update_password(data: UpdatePasswordRequest):
    """Update user's password."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(data.current_password.encode("utf-8"), user[4].encode("utf-8")):
            raise HTTPException(status_code=401, detail="Invalid email or current password.")

        hashed_new_pw = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new_pw.decode("utf-8"), user[0]))
        cursor.execute(
            "INSERT INTO update_logs (user_id, field_changed, old_value, new_value) VALUES (%s, %s, %s, %s)",
            (user[0], "password", "****", "****"),
        )
        conn.commit()
        return {"message": "Password updated successfully."}

    except Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if conn:
            conn.close()
