"""Gesture interpretation for the virtual mouse application."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

import numpy as np

from utils.config import GestureConfig
from utils.logger import get_logger

from .hand_tracking import HandObservation


class GestureType(str, Enum):
    """High level gestures understood by the pointer controller."""

    IDLE = "idle"
    MOVE = "move"
    CLICK = "click"
    DRAG = "drag"
    SCROLL = "scroll"


@dataclass
class GestureResult:
    """Result of gesture inference for a single frame."""

    gesture: GestureType
    pointer: Optional[Tuple[float, float]] = None
    scroll_delta: float = 0.0
    is_click: bool = False
    is_drag: bool = False


class GestureController:
    """Transform landmark observations into high level pointer gestures."""

    def __init__(self, config: GestureConfig) -> None:
        self._config = config
        self._logger = get_logger("gesture_controller")
        self._smoothed_position: Optional[np.ndarray] = None
        self._last_pinched = False
        self._last_event_time = 0.0
        self._drag_active = False

    def process(self, observation: HandObservation) -> GestureResult:
        pointer = self._compute_pointer(observation)
        pinch_distance = self._distance(observation, 4, 8)
        middle_delta = self._vertical_delta(observation, 8, 12)
        now = observation.timestamp

        gesture = GestureType.MOVE
        is_click = False
        is_drag = False
        scroll_delta = 0.0

        # Scroll detection when middle finger tip significantly offset.
        if abs(middle_delta) > self._config.scroll_threshold:
            gesture = GestureType.SCROLL
            scroll_delta = -math.copysign(min(abs(middle_delta), 0.25), middle_delta)

        # Pinch detection for click/drag.
        if pinch_distance < self._config.click_threshold:
            if not self._last_pinched and self._is_debounced(now):
                gesture = GestureType.CLICK
                is_click = True
                self._last_event_time = now
                self._drag_active = True
            else:
                gesture = GestureType.DRAG
                is_drag = True
                self._drag_active = True
            self._last_pinched = True
        else:
            if self._drag_active and self._last_pinched:
                # Release drag when pinch lifted.
                is_drag = False
            self._last_pinched = False
            self._drag_active = False

        pointer_tuple = tuple(pointer.tolist()) if pointer is not None else None
        result = GestureResult(
            gesture=gesture if pointer_tuple else GestureType.IDLE,
            pointer=pointer_tuple,
            scroll_delta=scroll_delta,
            is_click=is_click,
            is_drag=is_drag,
        )

        self._logger.debug("Gesture detected: %s", result)
        return result

    def reset(self) -> None:
        """Reset smoothing state when no hand is detected."""

        self._smoothed_position = None
        self._last_pinched = False
        self._drag_active = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _is_debounced(self, timestamp: float) -> bool:
        return (timestamp - self._last_event_time) > (self._config.debounce_ms / 1000.0)

    def _compute_pointer(self, observation: HandObservation) -> Optional[np.ndarray]:
        try:
            fingertip = observation.landmarks[8]
        except IndexError:
            return None

        position = np.array([fingertip.x, fingertip.y])
        if self._smoothed_position is None:
            self._smoothed_position = position
        else:
            alpha = np.clip(self._config.smoothing_alpha, 0.0, 1.0)
            self._smoothed_position = (
                alpha * position + (1.0 - alpha) * self._smoothed_position
            )

        return np.clip(self._smoothed_position, 0.0, 1.0)

    def _distance(self, observation: HandObservation, idx_a: int, idx_b: int) -> float:
        try:
            pt_a = observation.landmarks[idx_a]
            pt_b = observation.landmarks[idx_b]
        except IndexError:
            return 1.0
        return math.dist((pt_a.x, pt_a.y), (pt_b.x, pt_b.y))

    def _vertical_delta(self, observation: HandObservation, idx_a: int, idx_b: int) -> float:
        try:
            pt_a = observation.landmarks[idx_a]
            pt_b = observation.landmarks[idx_b]
        except IndexError:
            return 0.0
        return pt_b.y - pt_a.y

