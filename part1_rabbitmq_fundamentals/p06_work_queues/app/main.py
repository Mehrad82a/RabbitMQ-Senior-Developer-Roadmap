from fastapi import FastAPI
from app.api.routes import router



app = FastAPI(
    title="P06 Work Queue",
    version="1.0.0",
)


app.include_router(
    router,
    prefix="/api/v1",
)