"""CLI entry point for the virtual mouse application."""

from __future__ import annotations

import argparse
import asyncio
import signal
from typing import Optional

from utils.config import Config, ConfigManager
from utils.logger import configure_logging
from .virtual_mouse.virtual_mouse import VirtualMouseApp


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gesture controlled virtual mouse running on top of the system pointer."
    )
    parser.add_argument(
        "--auto-start",
        action="store_true",
        help="Start capturing immediately instead of waiting for activation.",
    )
    parser.add_argument(
        "--show-debug",
        action="store_true",
        help="Render the debug preview window with hand landmarks.",
    )
    parser.add_argument(
        "--log-level",
        default=None,
        help="Override the configured logging level (e.g. DEBUG, INFO).",
    )
    return parser


async def _run_async_app(config: Config, auto_start: bool) -> None:
    app = VirtualMouseApp(config=config)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler(*_: object) -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            # Windows event loop (Proactor) does not support signal handlers.
            signal.signal(sig, lambda *_: stop_event.set())

    app_task = asyncio.create_task(app.run(auto_start=auto_start))
    await stop_event.wait()
    await app.shutdown()
    await app_task


def main(argv: Optional[list[str]] = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    config_manager = ConfigManager()
    config = config_manager.get()

    if args.log_level:
        config_manager.override_logging_level(args.log_level)

    if args.show_debug:
        config_manager.override_debug(True)

    configure_logging(level=config_manager.get().logging.level)

    asyncio.run(_run_async_app(config=config_manager.get(), auto_start=args.auto_start))


if __name__ == "__main__":
    main()

