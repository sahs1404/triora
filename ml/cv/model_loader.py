"""
Loads a YOLOv8 model once at process startup, so every /verify request
reuses the same in-memory model instead of reloading weights per request.

Uses the pretrained YOLOv8n (nano) checkpoint from Ultralytics — trained
on COCO (80 general object classes: person, truck, car, etc). This is
NOT fine-tuned on construction-specific objects (no "switchgear",
"rebar", etc classes exist in COCO). See verify_stage.py for how we work
around that honestly instead of pretending otherwise.
"""

from ultralytics import YOLO

_model = None


def get_model():
    global _model
    if _model is None:
        # Downloads yolov8n.pt automatically on first run (~6MB) if not cached.
        _model = YOLO("yolov8n.pt")
    return _model