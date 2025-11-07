"""Unit tests for gesture interpretation logic."""

from __future__ import annotations

import math

from utils.config import GestureConfig
from src.virtual_mouse.gesture_controller import GestureController, GestureType
from src.virtual_mouse.hand_tracking import HandLandmark, HandObservation


def _make_landmarks(
    index_tip: tuple[float, float],
    thumb_tip: tuple[float, float],
    middle_tip: tuple[float, float],
) -> list[HandLandmark]:
    landmarks = [HandLandmark(0.5, 0.5, 0.0, 1.0) for _ in range(21)]
    landmarks[8] = HandLandmark(index_tip[0], index_tip[1], 0.0, 1.0)
    landmarks[4] = HandLandmark(thumb_tip[0], thumb_tip[1], 0.0, 1.0)
    landmarks[12] = HandLandmark(middle_tip[0], middle_tip[1], 0.0, 1.0)
    return landmarks


def _observation(
    index_tip: tuple[float, float],
    thumb_tip: tuple[float, float],
    middle_tip: tuple[float, float],
    timestamp: float,
) -> HandObservation:
    return HandObservation(
        frame_size=(640, 480),
        landmarks=_make_landmarks(index_tip, thumb_tip, middle_tip),
        handedness="Right",
        timestamp=timestamp,
    )


def test_pinch_triggers_click() -> None:
    config = GestureConfig(click_threshold=0.05, debounce_ms=50)
    controller = GestureController(config)

    obs = _observation((0.5, 0.5), (0.48, 0.5), (0.5, 0.7), timestamp=0.1)
    result = controller.process(obs)

    assert result.gesture == GestureType.CLICK
    assert result.is_click is True


def test_pointer_smoothing_applies() -> None:
    config = GestureConfig(smoothing_alpha=0.5)
    controller = GestureController(config)

    first = _observation((0.1, 0.1), (0.0, 0.0), (0.1, 0.2), timestamp=0.1)
    controller.process(first)

    second = _observation((0.9, 0.9), (0.0, 0.0), (0.9, 0.8), timestamp=0.2)
    result = controller.process(second)

    assert result.pointer is not None
    assert math.isclose(result.pointer[0], 0.5, abs_tol=0.05)
    assert math.isclose(result.pointer[1], 0.5, abs_tol=0.05)


def test_scroll_detects_vertical_delta() -> None:
    config = GestureConfig(scroll_threshold=0.05)
    controller = GestureController(config)

    obs = _observation((0.5, 0.4), (0.0, 0.0), (0.5, 0.7), timestamp=0.1)
    result = controller.process(obs)

    assert result.gesture == GestureType.SCROLL
    assert result.scroll_delta < 0

