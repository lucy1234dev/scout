from fastapi import FastAPI
from cors_config import apply_cors
from app import router as auth_router
from agent import router as ai_router

app = FastAPI()
apply_cors(app)

# Include routers with prefixes
app.include_router(auth_router, prefix="/auth")
app.include_router(ai_router, prefix="/ai")
