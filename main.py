import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import auth
from db_engine import engine, Base

app = FastAPI()

app.include_router(auth.router)
app.mount("/static", StaticFiles(directory="./static"), name="static")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Messenger!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")