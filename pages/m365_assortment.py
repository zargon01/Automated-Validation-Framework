"""Microsoft 365 Assortment page."""

from playwright.sync_api import Page

from qa.config_loader import GlobalConfig
from .base_page import BasePage


class M365AssortmentPage(BasePage):

    def setup(self, page: Page, config: GlobalConfig) -> None:
        super().setup(page, config)   # Cancel popup

        self._close_popup(
            page,
            selector='button[aria-label="Close dialog window"]',
            timeout_ms=5000,
        )

        self._wait(page, ms=2000)