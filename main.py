"""
FastAPI User Auth API for Agric Scout.

Features:
- Register users
- Login with email
- Update email
- Reset password

This version is production-ready and Pylint compliant.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import bcrypt
from psycopg2 import Error
from db_config import get_connection
from cors import apply_cors

# Initialize app
app = FastAPI()
apply_cors(app)

# -------------------- Models --------------------
class RegisterRequest(BaseModel):
    """Model for user registration."""
    firstname: str
    lastname: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Model for user login."""
    email: EmailStr
    password: str





class ResetPasswordRequest(BaseModel):
    """Model for resetting user password."""
    email: EmailStr
    new_password: str
    reset_method: str = "manual"  # default method


# -------------------- Routes --------------------
@app.get("/")
def home():
    """Root route to avoid 404."""
    return {"message": "Welcome to Agric Scout Auth API"}


@app.post("/register")
def register_user(data: RegisterRequest):
    """Register a new user."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already exists.")

        # Hash password
        hashed_pw = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Insert new user
        cursor.execute(
            "INSERT INTO users (firstname, lastname, email, password) "
            "VALUES (%s, %s, %s, %s)",
            (data.firstname, data.lastname, data.email, hashed_pw),
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

        # Find user
        cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
        user = cursor.fetchone()

        # Validate password
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




@app.put("/reset-password")
def reset_password(data: ResetPasswordRequest):
    """Reset a user's forgotten password and log the reset."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (data.email,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User with this email not found.")

        user_id = user[0]

        # Hash the new password
        hashed_password = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Update the user's password
        cursor.execute(
            "UPDATE users SET password = %s,  WHERE id = %s",
            (hashed_password, user_id)
        )

        # Log the password reset
        cursor.execute(
            "INSERT INTO reset_password (user_id, reset_method) VALUES (%s, %s)",
            (user_id, data.reset_method)
        )

        conn.commit()
        return {"message": "Password reset successfully."}

    except Error as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    finally:
        if conn:
            conn.close()







