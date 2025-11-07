"""Virtual mouse engine and application orchestration."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional, Protocol, Tuple

import cv2

from utils.config import Config
from utils.logger import get_logger

from .camera_module import CameraStream
from .gesture_controller import GestureController, GestureResult, GestureType
from .hand_tracking import HandObservation, HandTracker


class PointerController(Protocol):
    """Protocol describing pointer operations used by the engine."""

    def screen_size(self) -> Tuple[int, int]:
        ...

    def move(self, x: int, y: int, duration: float = 0.0) -> None:
        ...

    def click(self, button: str = "left") -> None:
        ...

    def press(self, button: str = "left") -> None:
        ...

    def release(self, button: str = "left") -> None:
        ...

    def scroll(self, dy: float, dx: float = 0.0) -> None:
        ...


class PyAutoGuiPointerController:
    """Cross-platform pointer controller backed by ``pyautogui``."""

    def __init__(self) -> None:
        try:
            import pyautogui
        except ImportError as exc:  # pragma: no cover - import guard
            raise RuntimeError(
                "pyautogui is required for pointer control. Install it via `pip install pyautogui`."
            ) from exc

        pyautogui.FAILSAFE = False
        self._lib = pyautogui

    def screen_size(self) -> Tuple[int, int]:
        size = self._lib.size()
        return int(size.width), int(size.height)

    def move(self, x: int, y: int, duration: float = 0.0) -> None:
        self._lib.moveTo(x, y, duration=duration, _pause=False)

    def click(self, button: str = "left") -> None:
        self._lib.click(button=button, _pause=False)

    def press(self, button: str = "left") -> None:
        self._lib.mouseDown(button=button, _pause=False)

    def release(self, button: str = "left") -> None:
        self._lib.mouseUp(button=button, _pause=False)

    def scroll(self, dy: float, dx: float = 0.0) -> None:
        if dy:
            self._lib.scroll(int(dy), _pause=False)
        if dx:
            self._lib.hscroll(int(dx), _pause=False)




@dataclass
class EngineResult:
    """Return metadata after the engine loop exits."""

    reason: str


class VirtualMouseEngine:
    """Core engine for frame acquisition, gesture detection, and pointer control."""

    def __init__(
        self,
        config: Config,
        pointer: Optional[PointerController] = None,
        camera: Optional[CameraStream] = None,
        tracker: Optional[HandTracker] = None,
    ) -> None:
        self._config = config
        self._logger = get_logger("engine")
        self._pointer = pointer or PyAutoGuiPointerController()
        self._camera = camera or CameraStream(config.camera)
        self._tracker = tracker or HandTracker()
        self._gestures = GestureController(config.gesture)
        self._dragging = False

    async def run(self, stop_event: asyncio.Event) -> EngineResult:
        self._logger.info("Engine starting")
        self._camera.start()
        screen_w, screen_h = self._pointer.screen_size()
        last_seen = asyncio.get_running_loop().time()
        reason = "stopped"

        try:
            async for frame in self._camera.frames():
                if stop_event.is_set():
                    reason = "stopped"
                    break

                processed = cv2.flip(frame, 1) if self._config.camera.mirror else frame
                observation = self._tracker.detect(processed)
                now = asyncio.get_running_loop().time()

                if observation is None:
                    self._gestures.reset()
                    self._camera.set_idle(True)
                    if self._config.app.show_debug:
                        self._render_debug(processed, None, None)
                        if self._poll_exit_key():
                            stop_event.set()
                            reason = "stopped"
                            break

                    if (
                        self._config.app.max_inactive_seconds > 0
                        and now - last_seen > self._config.app.max_inactive_seconds
                    ):
                        reason = "idle_timeout"
                        break
                    await asyncio.sleep(0.01)
                    continue

                last_seen = observation.timestamp
                self._camera.set_idle(False)

                gesture = self._gestures.process(observation)
                self._apply_gesture(gesture, screen_w, screen_h)

                if self._config.app.show_debug:
                    self._render_debug(processed, observation, gesture)
                    if self._poll_exit_key():
                        stop_event.set()
                        reason = "stopped"
                        break

        finally:
            self._camera.stop()
            if self._dragging:
                self._pointer.release()
                self._dragging = False

        return EngineResult(reason=reason)

    async def shutdown(self) -> None:
        """Release resources such as tracker and debug windows."""

        self._tracker.close()
        if self._config.app.show_debug:
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _apply_gesture(self, gesture: GestureResult, screen_w: int, screen_h: int) -> None:
        if gesture.pointer:
            x = int(gesture.pointer[0] * screen_w)
            y = int(gesture.pointer[1] * screen_h)
            self._pointer.move(x, y)

        if gesture.gesture == GestureType.CLICK and gesture.is_click:
            self._pointer.click()
            if self._dragging:
                self._pointer.release()
                self._dragging = False

        elif gesture.gesture == GestureType.DRAG:
            if not self._dragging:
                self._pointer.press()
                self._dragging = True
        else:
            if self._dragging:
                self._pointer.release()
                self._dragging = False

        if gesture.gesture == GestureType.SCROLL and gesture.scroll_delta:
            self._pointer.scroll(dy=gesture.scroll_delta * 120.0)

    def _render_debug(
        self,
        frame,
        observation: Optional[HandObservation],
        gesture: Optional[GestureResult],
    ) -> None:
        debug_frame = frame.copy()

        if observation:
            for point in observation.to_pixels():
                cv2.circle(debug_frame, point, 3, (0, 255, 0), -1)

        if gesture and gesture.pointer:
            px = int(gesture.pointer[0] * debug_frame.shape[1])
            py = int(gesture.pointer[1] * debug_frame.shape[0])
            cv2.circle(debug_frame, (px, py), 6, (0, 0, 255), -1)

        try:
            cv2.imshow(self._config.app.window_title, debug_frame)
        except cv2.error:
            self._logger.warning("OpenCV GUI backend not available; disabling debug view")
            self._config.app.show_debug = False

    def _poll_exit_key(self) -> bool:
        try:
            key = cv2.waitKey(1) & 0xFF
        except cv2.error:
            return False
        return key == ord(self._config.app.exit_key)


class VirtualMouseApp:
    """High-level application wrapper controlling activation and shutdown."""

    def __init__(self, config: Config, engine: Optional[VirtualMouseEngine] = None) -> None:
        self._config = config
        self._engine = engine or VirtualMouseEngine(config)
        self._logger = get_logger("app")
        self._shutdown = asyncio.Event()
        self._engine_stop: Optional[asyncio.Event] = None

    async def run(self, auto_start: bool | None = None) -> None:
        should_auto_start = self._config.app.auto_start if auto_start is None else auto_start

        while not self._shutdown.is_set():
            if not should_auto_start:
                await self._await_activation()

            if self._shutdown.is_set():
                break

            self._engine_stop = asyncio.Event()
            result = await self._engine.run(self._engine_stop)

            if self._shutdown.is_set() or (self._engine_stop and self._engine_stop.is_set()):
                break

            self._logger.info("Engine exited (%s). Waiting for the next activation.", result.reason)
            should_auto_start = False
            self._engine_stop = None

    async def shutdown(self) -> None:
        self._shutdown.set()
        if self._engine_stop:
            self._engine_stop.set()
        await self._engine.shutdown()

    async def _await_activation(self) -> None:
        self._logger.info(
            "Virtual mouse idle. Press ENTER to activate or use hotkey %s.",
            self._config.app.activation_hotkey,
        )
        await asyncio.to_thread(input, "Press ENTER to activate the virtual mouse...")

