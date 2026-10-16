CAPTIONS = {
    "Open_Palm": "Open palm detected.",
    "Closed_Fist": "Closed fist detected.",
    "Thumb_Up": "Thumbs up.",
    "Thumb_Down": "Thumbs down.",
    "Victory": "Victory or peace sign detected.",
    "Pointing_Up": "One finger pointing upward.",
    "ILoveYou": "I love you gesture detected.",
    "No gesture": "Show your hand clearly to the camera.",
    "Unknown": "A gesture was detected, but its label is unknown.",
}


def make_caption(label: str) -> str:
    return CAPTIONS.get(label, "Recognized gesture: " + label.replace("_", " ") + ".")
