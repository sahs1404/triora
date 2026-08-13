"""
Compares what YOLO actually detects in a site photo against what we'd
plausibly expect to see for a given construction stage, and returns an
annotated image (with bounding boxes drawn) as base64 for display.

Honest limitation: YOLOv8n's pretrained COCO classes are general-purpose
(person, truck, car, backpack, etc) -- there is no "switchgear installed"
or "rebar placed" class. So instead of pretending to verify construction-
specific claims, we verify a weaker but honest signal: does the photo
contain objects consistent with this stage of work.

If nothing stage-relevant is detected, we return "uncertain" rather than
a false "mismatch" -- a robust system says "I could not verify", not
"you skipped this".
"""

import base64
import cv2

from cv.model_loader import get_model

STAGE_EXPECTATIONS = {
    "delivery": ["truck", "car"],
    "fabrication": ["person"],
    "installation": ["person"],
    "inspection": ["person"],
    "site_prep": ["truck", "car", "person"],
}

CONFIDENCE_THRESHOLD = 0.35


def verify_stage(image_path: str, expected_stage: str) -> dict:
    model = get_model()
    results = model(image_path, verbose=False)[0]

    detected_classes = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        if conf >= CONFIDENCE_THRESHOLD:
            detected_classes.append(model.names[cls_id])

    expected_classes = STAGE_EXPECTATIONS.get(expected_stage, [])
    matched = [c for c in detected_classes if c in expected_classes]

    if not expected_classes:
        match_result = "unsupported_stage"
        explanation = "No verification rule exists yet for stage '" + expected_stage + "'."
    elif matched:
        match_result = "match"
        explanation = "Detected " + ", ".join(set(matched)) + " -- consistent with '" + expected_stage + "' stage."
    elif detected_classes:
        match_result = "mismatch"
        explanation = (
            "Detected " + ", ".join(set(detected_classes)) + ", none of which are expected "
            "for '" + expected_stage + "' stage (" + ", ".join(expected_classes) + ")."
        )
    else:
        match_result = "uncertain"
        explanation = "No relevant objects detected with sufficient confidence -- could not verify."

    # results.plot() draws bounding boxes + labels on the image (BGR numpy array).
    # Encode as JPEG then base64 so it can be sent as a JSON string and
    # displayed directly in the frontend as an <img> data URI.
    annotated_frame = results.plot()
    success, buffer = cv2.imencode(".jpg", annotated_frame)
    annotated_image_base64 = base64.b64encode(buffer).decode("utf-8") if success else None

    return {
        "match_result": match_result,
        "explanation": explanation,
        "detected_classes": list(set(detected_classes)),
        "expected_classes": expected_classes,
        "annotated_image_base64": annotated_image_base64,
    }