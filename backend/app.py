from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, dashboard, simulation, vendors
from database.session import Base, engine
from database import models

app = FastAPI(title="Triora API")

@app.on_event("startup")
def on_startup():
    # Creates all tables if they don't already exist yet — safe to run
    # every startup. This is what was missing on Render: locally we ran
    # `python -m database.init_db` once by hand, but that never ran on
    # the deployed server, so its triora.db had zero tables.
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(simulation.router)
app.include_router(vendors.router)


@app.get("/")
def root():
    return {"status": "Triora API is running"}