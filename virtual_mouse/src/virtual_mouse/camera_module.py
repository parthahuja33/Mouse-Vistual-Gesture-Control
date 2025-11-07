"""Camera management utilities for the virtual mouse application."""

from __future__ import annotations

import asyncio
import threading
import time
from typing import AsyncIterator, Optional, Tuple

import cv2
import numpy as np

from utils.config import CameraConfig
from utils.logger import get_logger


class CameraStream:
    """Thin wrapper around ``cv2.VideoCapture`` with async-friendly access."""

    def __init__(self, config: CameraConfig) -> None:
        self._config = config
        self._logger = get_logger("camera")
        self._capture: Optional[cv2.VideoCapture] = None
        self._frame_lock = threading.Lock()
        self._frame: Optional[np.ndarray] = None
        self._running = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._resolution: Tuple[int, int] = config.resolution
        self._idle = threading.Event()

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------
    def start(self) -> None:
        if self._running.is_set():
            return

        self._logger.info("Opening camera index %s", self._config.index)
        capture = cv2.VideoCapture(self._config.index, cv2.CAP_DSHOW)
        if not capture.isOpened():
            raise RuntimeError(f"Unable to open camera index {self._config.index}")

        self._capture = capture
        self._apply_resolution(self._config.resolution)

        self._running.set()
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

        self._warmup()

    def stop(self) -> None:
        if not self._running.is_set():
            return

        self._running.clear()
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

        if self._capture:
            self._capture.release()
            self._capture = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def read(self) -> Optional[np.ndarray]:
        """Return the latest frame captured by the camera."""

        with self._frame_lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    async def frames(self) -> AsyncIterator[np.ndarray]:
        """Async frame generator, suitable for ``async for`` consumption."""

        while self._running.is_set():
            frame = self.read()
            if frame is not None:
                yield frame
                await asyncio.sleep(max(0.0, 1.0 / self._config.fps))
            else:
                await asyncio.sleep(0.02)

    def set_idle(self, enabled: bool) -> None:
        """Toggle idle mode to reduce capture load."""

        if enabled:
            if not self._idle.is_set():
                self._logger.debug("Entering idle camera mode")
                self._idle.set()
                self._apply_resolution(self._config.idle_resolution)
        else:
            if self._idle.is_set():
                self._logger.debug("Leaving idle camera mode")
                self._idle.clear()
                self._apply_resolution(self._config.resolution)

    # ------------------------------------------------------------------
    # Context management
    # ------------------------------------------------------------------
    def __enter__(self) -> "CameraStream":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.stop()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _warmup(self) -> None:
        if not self._capture:
            return
        for _ in range(self._config.warmup_frames):
            self._capture.read()

    def _apply_resolution(self, resolution: Tuple[int, int]) -> None:
        if not self._capture:
            return
        width, height = resolution
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._resolution = resolution

    def _update_loop(self) -> None:
        assert self._capture is not None

        idle_skip = 0
        while self._running.is_set():
            ret, frame = self._capture.read()
            if not ret:
                self._logger.warning("Failed to read frame from camera")
                time.sleep(0.05)
                continue

            if self._idle.is_set() and self._config.idle_frame_skip > 0:
                idle_skip = (idle_skip + 1) % (self._config.idle_frame_skip + 1)
                if idle_skip != 0:
                    continue

            with self._frame_lock:
                self._frame = frame

            time.sleep(max(0.0, 1.0 / self._config.fps))

