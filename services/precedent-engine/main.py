from fastapi import FastAPI
from routes import router

app = FastAPI(title="Precedent Engine")
app.include_router(router)
