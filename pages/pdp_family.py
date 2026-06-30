from __future__ import annotations

from playwright.sync_api import Page

from qa.config_loader import GlobalConfig
from .base_page import BasePage


class PdpFamilyPage(BasePage):

    def setup(self, page: Page, config: GlobalConfig) -> None:
        super().setup(page, config) 

        self._close_popup(
            page,
            selector='button[aria-label="Close dialog window"]',
            timeout_ms=5000,
        )

        self._wait(page, ms=2000)
        # Expand accordion
        self._expand_accordion(
            page,
            selector="button.btn-collapse",
            timeout_ms=10_000,
        )

        self._wait(page, ms=1000)