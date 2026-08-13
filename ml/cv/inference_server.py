"""
Standalone CV inference service — separate from the main Triora backend.
Exposes POST /verify, accepting an uploaded photo + expected_stage,
returns YOLO detection results + match/mismatch verdict.

Run locally:
    cd ml
    uvicorn cv.inference_server:app --reload --port 8100
"""

import shutil
import tempfile
import os

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from cv.verify_stage import verify_stage

app = FastAPI(title="Triora CV Inference Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "Triora CV inference service is running"}


@app.post("/verify")
async def verify(photo: UploadFile = File(...), expected_stage: str = Form(...)):
    suffix = os.path.splitext(photo.filename)[1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(photo.file, tmp)
        tmp_path = tmp.name

    try:
        result = verify_stage(tmp_path, expected_stage)
    finally:
        os.remove(tmp_path)

    return result