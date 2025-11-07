"""Configuration management for the Virtual Mouse project."""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass, field
from typing import Optional, Tuple


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_tuple(name: str, default: Tuple[int, int]) -> Tuple[int, int]:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        width, height = value.split("x", maxsplit=1)
        return int(width), int(height)
    except (ValueError, TypeError):
        return default


@dataclass
class LoggingConfig:
    """Logging-related configuration values."""

    level: str = "INFO"
    log_to_file: bool = False
    filepath: Optional[str] = None


@dataclass
class CameraConfig:
    """Configuration that controls camera behavior."""

    index: int = 0
    resolution: Tuple[int, int] = (960, 540)
    fps: int = 30
    idle_resolution: Tuple[int, int] = (640, 360)
    idle_frame_skip: int = 2
    warmup_frames: int = 12
    mirror: bool = True


@dataclass
class GestureConfig:
    """Configuration for gesture smoothing and thresholds."""

    smoothing_alpha: float = 0.25
    click_threshold: float = 0.035
    drag_threshold: float = 0.04
    scroll_threshold: float = 0.12
    debounce_ms: int = 180
    idle_timeout_sec: float = 2.0


@dataclass
class AppConfig:
    """Application-level configuration."""

    show_debug: bool = False
    exit_key: str = "q"
    activation_hotkey: str = "ctrl+alt+m"
    auto_start: bool = False
    max_inactive_seconds: float = 10.0
    window_title: str = "Virtual Mouse"


@dataclass
class Config:
    """Root dataclass aggregating all configuration domains."""

    camera: CameraConfig = field(default_factory=CameraConfig)
    gesture: GestureConfig = field(default_factory=GestureConfig)
    app: AppConfig = field(default_factory=AppConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigManager:
    """Singleton-style configuration accessor with environment overrides."""

    _instance: Optional["ConfigManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "ConfigManager":  # type: ignore[override]
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._config = Config()
                cls._instance._apply_environment_overrides()
        return cls._instance

    def get(self) -> Config:
        """Return the current configuration object."""

        return self._config

    # ------------------------------------------------------------------
    # Override helpers
    # ------------------------------------------------------------------
    def override_logging_level(self, level: str) -> None:
        self._config.logging.level = level.upper()

    def override_debug(self, enabled: bool) -> None:
        self._config.app.show_debug = enabled

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _apply_environment_overrides(self) -> None:
        camera = self._config.camera
        gesture = self._config.gesture
        app = self._config.app
        logging_cfg = self._config.logging

        camera.index = _env_int("VM_CAMERA_INDEX", camera.index)
        camera.resolution = _env_tuple("VM_CAMERA_RESOLUTION", camera.resolution)
        camera.fps = _env_int("VM_CAMERA_FPS", camera.fps)
        camera.idle_resolution = _env_tuple("VM_CAMERA_IDLE_RESOLUTION", camera.idle_resolution)
        camera.idle_frame_skip = _env_int("VM_CAMERA_IDLE_SKIP", camera.idle_frame_skip)
        camera.warmup_frames = _env_int("VM_CAMERA_WARMUP_FRAMES", camera.warmup_frames)
        camera.mirror = _env_flag("VM_CAMERA_MIRROR", camera.mirror)

        gesture.smoothing_alpha = _env_float("VM_GESTURE_SMOOTHING", gesture.smoothing_alpha)
        gesture.click_threshold = _env_float("VM_GESTURE_CLICK_THRESHOLD", gesture.click_threshold)
        gesture.drag_threshold = _env_float("VM_GESTURE_DRAG_THRESHOLD", gesture.drag_threshold)
        gesture.scroll_threshold = _env_float("VM_GESTURE_SCROLL_THRESHOLD", gesture.scroll_threshold)
        gesture.debounce_ms = _env_int("VM_GESTURE_DEBOUNCE_MS", gesture.debounce_ms)
        gesture.idle_timeout_sec = _env_float("VM_GESTURE_IDLE_TIMEOUT", gesture.idle_timeout_sec)

        app.show_debug = _env_flag("VM_APP_SHOW_DEBUG", app.show_debug)
        app.exit_key = os.getenv("VM_APP_EXIT_KEY", app.exit_key)
        app.activation_hotkey = os.getenv("VM_APP_ACTIVATION_HOTKEY", app.activation_hotkey)
        app.auto_start = _env_flag("VM_APP_AUTO_START", app.auto_start)
        app.max_inactive_seconds = _env_float("VM_APP_MAX_INACTIVE_SECONDS", app.max_inactive_seconds)
        app.window_title = os.getenv("VM_APP_WINDOW_TITLE", app.window_title)

        logging_cfg.level = os.getenv("VM_LOG_LEVEL", logging_cfg.level).upper()
        logging_cfg.log_to_file = _env_flag("VM_LOG_TO_FILE", logging_cfg.log_to_file)
        logging_cfg.filepath = os.getenv("VM_LOG_PATH", logging_cfg.filepath)

