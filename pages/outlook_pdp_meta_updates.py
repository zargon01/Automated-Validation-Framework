"""Outlook PDP Meta Updates page."""

from playwright.sync_api import Page

from qa.config_loader import GlobalConfig
from .base_page import BasePage


class OutlookPdpMetaUpdatesPage(BasePage):

    def setup(self, page: Page, config: GlobalConfig) -> None:
        super().setup(page, config)   # Cancel popup

        # Second popup — Close dialog window
        self._close_popup(
            page,
            selector='button[aria-label="Close dialog window"]',
            timeout_ms=5000,
        )