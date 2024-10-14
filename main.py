from contextlib import asynccontextmanager
from fastapi import FastAPI
from logger import logger
from database import create_table, delete_table
from src.auth.router import router as user_router
from src.tasks.router import router as task_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table()
    logger.info("Starting application, initializing database.")
    yield
    # await delete_table()
    logger.info("App stopped.")

app = FastAPI(lifespan=lifespan)

app.include_router(task_router, prefix='/api/v1')
app.include_router(user_router, prefix='/api/v1')
