from fastapi import FastAPI
from routes import router

app = FastAPI(title="Monitoring Engine")
app.include_router(router)
