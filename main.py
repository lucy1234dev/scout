# main.py
from fastapi import FastAPI
from app import router as auth_router
from agent import router as ai_router
from cors_config import apply_cors

app = FastAPI(title="Agric Scout API")

apply_cors(app)


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])

@app.get("/")
def root():
    return {"message": "Welcome to Agric Scout Backend API"}
