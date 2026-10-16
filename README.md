# SignBridge — Vercel-ready Flask + MediaPipe prototype

A small full-stack gesture-recognition demo using Flask, Python, OpenCV, MediaPipe, and a browser webcam. The frontend and backend deploy together as one Flask application.

**Before deploying:** copy `gesture_recognizer.task` into this folder beside `app.py`. This model file is not included in this ZIP because it is already present in your existing local project. Follow `DEPLOY_TO_VERCEL.md` for deployment steps.

This project processes static hand-gesture frames only. It does not translate full sign language, understand facial expressions, or infer complete sentences. The hosted version sends camera snapshots to the Python endpoint for recognition; the app code does not save frames to a database.
