"""Resolves the `page:` key in a check suite yaml to a BasePage instance.

Convention: page: "ms365_pdp"  →  pages/ms365_pdp.py  →  MS365PDPPage

Class name is derived by converting the filename stem to PascalCase and
appending "Page". So:
    ms365_pdp       → MS365PDPPage
    some_new_page   → SomeNewPagePage

To add support for a new page, just create pages/your_page.py with a class
named YourPagePage that extends BasePage. No other changes needed.
"""

from __future__ import annotations
import importlib

from pages.base_page import BasePage


def load_page(page_key: str) -> BasePage:
    """Import pages/<page_key>.py and return an instance of its Page class."""
    module_path = f"pages.{page_key}"
    class_name  = _to_class_name(page_key)

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise FileNotFoundError(
            f"No page file found at pages/{page_key}.py — "
            f"create it or fix the `page:` key in your checks yaml."
        )

    cls = getattr(module, class_name, None)
    if cls is None:
        raise AttributeError(
            f"pages/{page_key}.py exists but has no class named '{class_name}'."
        )

    return cls()


def _to_class_name(stem: str) -> str:
    return "".join(part.capitalize() for part in stem.split("_")) + "Page"