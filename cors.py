# cors_config.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

def apply_cors(app: FastAPI) -> None:
    """
    Applies CORS middleware and preflight OPTIONS handling.
    """
    origins = [
        "https://agric-scout.netlify.app",  #  Replace with your real frontend
        "http://localhost:5500",
        "http://127.0.0.1:5500",
                                # Local frontend
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,  # If you use "*", this must be False
        allow_methods=["*"],      # GET, POST, PUT, DELETE, OPTIONS, etc.
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def cors_preflight_handler(request: Request, call_next):
        if request.method == "OPTIONS":
            response = JSONResponse({"message": "Preflight OK"})
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response

        response = await call_next(request)
        return response
