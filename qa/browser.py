"""Chrome browser lifecycle — launch and teardown."""

from __future__ import annotations

from playwright.sync_api import sync_playwright, BrowserContext, Page

from .config_loader import GlobalConfig


class BrowserManager:
    def __init__(self, config: GlobalConfig):
        self.config      = config
        self._playwright = None
        self._context: BrowserContext | None = None

    def __enter__(self) -> "BrowserManager":
        self._playwright = sync_playwright().start()
        self._context    = self._playwright.chromium.launch(
            headless = self.config.headless,
            slow_mo  = self.config.slow_mo,
        ).new_context(locale="en-US")
        return self

    def __exit__(self, *_):
        if self._context:
            self._context.close()
        if self._playwright:
            self._playwright.stop()

    def new_page(self) -> Page:
        if not self._context:
            raise RuntimeError("BrowserManager not started — use as context manager.")
        return self._context.new_page()