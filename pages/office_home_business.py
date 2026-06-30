"""Office Home & Business 2024 PDP page."""

from playwright.sync_api import Page

from qa.config_loader import GlobalConfig
from .base_page import BasePage


class OfficeHomeBusinessPage(BasePage):

    def setup(self, page: Page, config: GlobalConfig) -> None:
        super().setup(page, config)   # Cancel popup

        # Second popup — Close dialog window
        self._close_popup(
            page,
            selector='button[aria-label="Close dialog window"]',
            timeout_ms=5000,
        )

        self._wait(page, ms=2000)

        # Expand first accordion item via li h3 button
        self._expand_accordion(
            page,
            selector="li h3 button",
            timeout_ms=10_000,
        )

        self._wait(page, ms=1000)