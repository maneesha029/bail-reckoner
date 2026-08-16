from fastapi import FastAPI
from routes import router

app = FastAPI(title="Compliance Engine")
app.include_router(router)
