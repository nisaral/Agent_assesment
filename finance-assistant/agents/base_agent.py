from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_base_app(name: str) -> FastAPI:
    app = FastAPI(title=name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:5500", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    return app