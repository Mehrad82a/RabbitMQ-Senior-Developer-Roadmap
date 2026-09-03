from fastapi import FastAPI
from app.api.routes import router



app = FastAPI(
    title="P07 Message Persistence",
    version="1.0.0",
)


app.include_router(
    router,
    prefix="/api/v1",
)