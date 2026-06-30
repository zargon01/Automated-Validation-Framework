"""BasePage — shared Playwright actions that apply to every page."""

from __future__ import annotations
from abc import ABC, abstractmethod

from playwright.sync_api import Page

from qa.config_loader import GlobalConfig


class BasePage(ABC):

    @abstractmethod
    def setup(self, page: Page, config: GlobalConfig) -> None:
        """Subclasses call super().setup() first, then add page-specific steps."""
        self._close_popup(page)

    def _close_popup(
        self,
        page: Page,
        selector: str = 'xpath=//*[@id="geo-selector-modal"]/div/div/div[1]/button[1]',
        timeout_ms: int = 8000,
    ) -> None:
        try:
            btn = page.locator(selector)
            # Wait for visible specifically — this blocks until the popup
            # actually renders on screen, however long that takes up to timeout
            btn.wait_for(state="visible", timeout=timeout_ms)
            btn.click()
            print("Popup closed")
        except Exception:
            print("No popup — continuing")

    def _expand_accordion(
        self,
        page: Page,
        selector: str = "button.btn-collapse",
        timeout_ms: int = 10_000,
    ) -> None:
        try:
            btn = page.locator(selector).first
            btn.wait_for(state="attached", timeout=timeout_ms)
            if btn.get_attribute("aria-expanded") != "true":
                btn.click(force=True)
                page.wait_for_timeout(1500)
            print("Accordion expanded")
        except Exception as exc:
            print(f"Accordion expand failed: {exc}")

    def _wait(self, page: Page, ms: int) -> None:
        page.wait_for_timeout(ms)
        print(f"  ⏱  Waited {ms}ms")