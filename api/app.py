from fastapi import FastAPI

from .routes import router as main_router


app = FastAPI(
    title="api",
    version="0.1.0",
    description="API",
)

app.include_router(main_router)
