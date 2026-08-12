from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, dashboard, simulation, vendors

app = FastAPI(title="Triora API")

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