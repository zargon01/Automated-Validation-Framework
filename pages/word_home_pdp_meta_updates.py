"""Word Home PDP Meta Updates page."""

from playwright.sync_api import Page

from qa.config_loader import GlobalConfig
from .base_page import BasePage


class WordHomePdpMetaUpdatesPage(BasePage):

    def setup(self, page: Page, config: GlobalConfig) -> None:
        # super().setup(page, config)

        # Wait until both title and meta description are loaded
        page.wait_for_function(
            """() => {
                const titleReady = document.title && document.title.length > 0;

                const meta = document.querySelector('meta[name="description"]');
                const metaReady = meta && meta.content && meta.content.length > 0;

                return titleReady && metaReady;
            }"""
        )