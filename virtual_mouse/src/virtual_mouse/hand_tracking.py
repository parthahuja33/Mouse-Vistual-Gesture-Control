"""Hand tracking utilities built on top of MediaPipe."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

import cv2

from utils.logger import get_logger

try:
    import mediapipe as mp
except ImportError as exc:  # pragma: no cover - defensive guard
    mp = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


@dataclass
class HandLandmark:
    """Single landmark in MediaPipe normalised coordinates."""

    x: float
    y: float
    z: float
    visibility: float


@dataclass
class HandObservation:
    """Represents a detected hand and its metadata."""

    frame_size: Tuple[int, int]
    landmarks: List[HandLandmark]
    handedness: str
    timestamp: float

    def to_pixels(self) -> List[Tuple[int, int]]:
        width, height = self.frame_size
        return [(int(lm.x * width), int(lm.y * height)) for lm in self.landmarks]


class HandTracker:
    """Wrapper around MediaPipe Hands with simplified results."""

    def __init__(
        self,
        max_hands: int = 1,
        detection_confidence: float = 0.6,
        tracking_confidence: float = 0.5,
    ) -> None:
        if mp is None:  # pragma: no cover - import guard
            raise RuntimeError(
                "mediapipe is required for hand tracking. Install it via `pip install mediapipe`."
            ) from _IMPORT_ERROR

        self._logger = get_logger("hand_tracking")
        self._hands = mp.solutions.hands.Hands(
            max_num_hands=max_hands,
            model_complexity=0,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def detect(self, frame) -> Optional[HandObservation]:
        """Run hand detection on a BGR frame and return the first observation."""

        height, width = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        if not results.multi_hand_landmarks:
            return None

        hand_landmarks = results.multi_hand_landmarks[0]
        handedness = "Unknown"
        if results.multi_handedness:
            classification = results.multi_handedness[0].classification
            if classification:
                handedness = classification[0].label

        landmarks = [
            HandLandmark(
                x=lm.x,
                y=lm.y,
                z=lm.z,
                visibility=getattr(lm, "visibility", 1.0),
            )
            for lm in hand_landmarks.landmark
        ]

        observation = HandObservation(
            frame_size=(width, height),
            landmarks=landmarks,
            handedness=handedness,
            timestamp=time.monotonic(),
        )

        self._logger.debug("Detected %s hand with %s landmarks", handedness, len(landmarks))
        return observation

    def close(self) -> None:
        self._hands.close()

    def __enter__(self) -> "HandTracker":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()

