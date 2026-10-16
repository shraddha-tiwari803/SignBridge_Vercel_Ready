# SignBridge — Vercel deployment checklist

This version keeps the Flask app and Python/MediaPipe model together as one deployment. The browser opens the visitor's webcam, captures a small JPEG approximately once per second, sends it to `/api/recognize`, and displays the Python inference result.

## Required before deploying

1. Copy `gesture_recognizer.task` from your existing working Sign-Language project folder into this folder, beside `app.py`. Do not rename it.
2. Confirm the model file is around 8 MB and is not empty.
3. The `.gitignore` in this deployment package intentionally does **not** ignore the model. Ensure the model is actually added to the repository; merely removing it from `.gitignore` does not add an already-ignored file. If using Git locally, `git add -f gesture_recognizer.task` can add it.
4. Use Python 3.12 for the Vercel deployment. The `.python-version` file requests it.

## Recommended Vercel deployment steps

1. Keep a backup/copy of your current working project first.
2. Put the files in this folder into the root of the repository you intend Vercel to deploy. Do not put an extra nested copy of the folder inside the repository root. Make sure `app.py`, `requirements.txt`, `vercel.json`, `.python-version`, `templates/`, and `public/` are at the top level.
3. Commit and push these changes to the repository connected to Vercel, including `gesture_recognizer.task`.
4. In Vercel, open the project → Settings → General. Set Root Directory to the repository folder that contains `app.py` (usually `./`).
5. Under Build and Development Settings, leave framework detection/default build settings enabled; don't set a Node.js build command or an output directory for this Flask app.
6. Open Deployments and redeploy the latest commit. Wait for the build to finish.
7. Open the deployment URL. First, open `/api/status` on that same domain. Its JSON should show `"model_found": true`.
8. Open the home page, press **Start camera**, allow permission, and show a supported gesture. Watch the label, confidence score, and caption.

## Local check before pushing

From this folder, with Python 3.12 installed:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000`.

## If Vercel returns HTTP 500

The browser's one-line 500 message does not identify the cause. In Vercel, open the failed deployment and inspect Build Logs. Then open the project's Logs/Runtime Logs, refresh the 500 URL, and read the Python traceback for that request. Common causes include dependency import failures (`cv2`/`mediapipe`), an omitted model asset, a failed model initialization, or a Python version/package wheel mismatch. A missing model should appear as `model_found: false` on `/api/status`; it should not prevent the home page from loading in this version.

## Important behavior and privacy note

A hosted Flask server cannot use a remote visitor's physical webcam through `cv2.VideoCapture(0)`. This version removes the server-side webcam stream and uses `getUserMedia()` in the browser. The browser sends compressed camera frames to the hosted Python endpoint for inference. The app code does not write those frames to a database, but the hosting provider processes the requests. This prototype recognizes a limited set of static hand gestures; it is not a complete sign-language translator.
