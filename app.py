from __future__ import annotations

import base64
import binascii
import logging
import threading
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request, send_from_directory

from caption_processor import make_caption
from gesture_recognition import GestureService

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "gesture_recognizer.task"
PUBLIC_STATIC = ROOT / "public" / "static"

# Vercel serves /public assets through its CDN. This small route keeps the same
# assets available when running Flask locally with `python app.py`.
app = Flask(__name__, static_folder=None, template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # Image API requests are intentionally small.
app.logger.setLevel(logging.INFO)

_service: GestureService | None = None
_service_init_lock = threading.Lock()
_inference_lock = threading.Lock()


def get_service() -> GestureService:
    """Load MediaPipe only when the first recognition request arrives."""
    global _service
    if _service is None:
        with _service_init_lock:
            if _service is None:
                _service = GestureService(MODEL)
    return _service


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/static/<path:filename>")
def local_static(filename: str):
    """Serve public/static files during local development."""
    return send_from_directory(PUBLIC_STATIC, filename)


@app.get("/api/status")
def status():
    return jsonify({
        "model_found": MODEL.is_file(),
        "camera_mode": "browser",
        "recognition_mode": "server-side Python/MediaPipe",
    })


@app.post("/api/recognize")
def recognize_frame():
    """Accept one compressed browser-camera frame and return a prediction."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Expected JSON containing an image field."}), 400

    image_data = payload.get("image")
    if not isinstance(image_data, str) or not image_data.startswith("data:image/jpeg;base64,"):
        return jsonify({"error": "The image must be a JPEG data URL."}), 400

    encoded = image_data.split(",", 1)[1]
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        return jsonify({"error": "The image data was not valid base64."}), 400

    if not image_bytes or len(image_bytes) > 1_000_000:
        return jsonify({"error": "The image is empty or too large. Please retry."}), 413

    frame = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({"error": "Could not decode the camera image."}), 400

    if not MODEL.is_file():
        return jsonify({
            "error": "The AI model file is missing. Add gesture_recognizer.task beside app.py and redeploy."
        }), 503

    try:
        service = get_service()
        with _inference_lock:
            label, score = service.recognize(frame)
        return jsonify({
            "label": label,
            "score": round(float(score), 4),
            "confidence_percent": round(float(score) * 100, 1),
            "caption": make_caption(label),
        })
    except Exception:
        # Detailed traceback goes to provider runtime logs; do not expose internals to visitors.
        app.logger.exception("Gesture recognition failed")
        return jsonify({
            "error": "Gesture recognition failed on the server. Check the deployment runtime logs."
        }), 500


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({"error": "The request was too large. Please retry with the camera frame."}), 413


@app.get("/api/caption/<path:label>")
def caption(label: str):
    return jsonify({"label": label, "caption": make_caption(label)})


if __name__ == "__main__":
    if not MODEL.is_file():
        print("Model missing: place gesture_recognizer.task beside app.py")
    print("Open http://127.0.0.1:5000; press Ctrl+C to stop.")
    app.run(host="127.0.0.1", port=5000, debug=False)
