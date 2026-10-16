from pathlib import Path

import cv2
import mediapipe as mp


class GestureService:
    """Runs one-image MediaPipe gesture classification for each API request."""

    def __init__(self, model_path: Path):
        if not model_path.is_file():
            raise FileNotFoundError(f"MediaPipe model not found: {model_path}")

        options = mp.tasks.vision.GestureRecognizerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_hands=1,
        )
        self.recognizer = mp.tasks.vision.GestureRecognizer.create_from_options(options)

    def recognize(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.recognizer.recognize(image)

        if result.gestures and result.gestures[0]:
            item = result.gestures[0][0]
            return item.category_name or "Unknown", float(item.score or 0.0)
        return "No gesture", 0.0
