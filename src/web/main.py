
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.web.routes import router

WEB_DIR = Path(__file__).resolve().parent

app = FastAPI(title="OuDiaExcel Web")

app.mount(
    "/static",
    StaticFiles(directory=WEB_DIR / "static"),
    name="static",
)

app.include_router(router)

