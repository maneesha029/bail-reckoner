from fastapi import FastAPI
from routes import router

app = FastAPI(title="Trust & Access Layer")
app.include_router(router)
