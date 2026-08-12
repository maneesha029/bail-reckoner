from fastapi import FastAPI
from routes import router

app = FastAPI(title="Eligibility Engine")
app.include_router(router)
