from fastapi import FastAPI
from routes import router
from models import Base
from config import engine

app = FastAPI(title="Compliance Engine")
app.include_router(router)

# Creates procedural_requirements / bond_waiver_flags if they don't exist
# yet - this service owns those two tables (never Member 1's
# case_offenses/offenses). No migration tooling exists yet elsewhere in
# the repo, so this is the simplest thing that lets the service run
# against a fresh DB.
Base.metadata.create_all(bind=engine)
