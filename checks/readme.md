# Creating Check Files

Check files are YAML files inside the `checks/` folder. Each file defines one test suite — a URL to test, which page class to use, and a list of checks to run.

---

## File location

```
checks/your_suite_name.yaml
```

---

## Full structure

```yaml
url:            "https://www.microsoft.com/{region}/your/page/path"
page:           "your_page"
screenshot_dir: "screenshots/your_suite_name"
excel_file:     "results/your_suite_name.xlsx"

checks:
  - name:     "Check name shown in logs and Excel"
    locator:  "css or xpath selector"
    expected: "text you expect to find"
```

`{region}` in the URL is automatically replaced with each region code from column A of your Excel file at runtime.

---

## Check types

### 1. Text check (default)
Reads the visible text of an element. Translates if not English, then does exact substring match, then falls back to semantic match.

```yaml
- name:     "Promo text"
  locator:  '[data-automation-test-id="buy-box-promo"] p'
  expected: "Subscription automatically renews at the regular price"
```

---

### 2. Head check
Use this for `<title>` and `<meta>` tags — elements that are not visible on the page. Works exactly like a text check but uses a different DOM method to read the value.

```yaml
- name:    "Page Title"
  locator: "title"
  type:    head
  expected: "Buy Microsoft Outlook | Microsoft Store"
```

---

### 3. Attribute check
Reads a DOM attribute value instead of text content. Use for `href`, `aria-label`, `data-*` attributes etc.

```yaml
- name:      "CTA aria-label"
  locator:   "a.primary-buy-button"
  type:      attribute
  attribute: aria-label
  expected:  "Try Microsoft 365 Personal free for 1 month."
```

Add `semantic: true` if the attribute may be in another language and needs translation + semantic matching:

```yaml
- name:      "Terms link aria-label"
  locator:   "div.disclaimer p a"
  type:      attribute
  attribute: aria-label
  expected:  "Learn more about the Microsoft Store Terms of Sale."
  semantic:  true
```

---

## Targeting a specific element when a locator returns multiple

Use `nth` (0-indexed) to target a specific element:

```yaml
- name:    "CTA 1 text"
  locator: "a.primary-buy-button"
  nth:     0
  expected: "Try free for 1 month"

- name:    "CTA 2 text"
  locator: "a.primary-buy-button"
  nth:     1
  expected: "See other options"
```

---

## Dynamic region in expected values

Use `{region}` inside any `expected:` value and it will be replaced with the current region at runtime:

```yaml
- name:    "CTA URL"
  locator: "a.primary-buy-button"
  type:    attribute
  attribute: href
  expected: "https://www.microsoft.com/{region}/microsoft-365/try-prs"
```

---

## Region filtering

### Run a check only for specific regions

```yaml
- name:    "First month free badge"
  locator: "span.badge"
  expected: "First month free"
  regions:
    - en-us
    - en-gb
    - en-ca
```

### Run a check for all regions except some

```yaml
- name:    "Promo text"
  locator: "div.disclaimer p"
  expected: "Subscription automatically renews..."
  exclude_regions:
    - de-de
```

### Reuse a region list across multiple checks (DRY)

Define the list once at the top with a YAML anchor and reference it:

```yaml
_my_regions: &my_regions
  - en-us
  - en-gb
  - en-ca

checks:
  - name:    "Badge"
    locator: "span.badge"
    expected: "First month free"
    regions: *my_regions

  - name:    "CTA text"
    locator: "a.primary-buy-button"
    expected: "Try free for 1 month"
    regions: *my_regions
```

---

## Creating a new page class

If you are testing a page that has a different setup (different popup, accordion, etc.) you need to create a page class in the `pages/` folder.

**Naming rule:** the `page:` value in your yaml maps directly to the filename and class name.

| yaml `page:` value | file to create | class name |
|--------------------|---------------|------------|
| `my_page` | `pages/my_page.py` | `MyPagePage` |
| `outlook_pdp` | `pages/outlook_pdp.py` | `OutlookPdpPage` |

**Template:**

```python
from playwright.sync_api import Page
from qa.config_loader import GlobalConfig
from .base_page import BasePage

class MyPagePage(BasePage):

    def setup(self, page: Page, config: GlobalConfig) -> None:
        super().setup(page, config)   # handles Cancel popup

        # Add any page-specific steps here, for example:
        self._close_popup(
            page,
            selector='button[aria-label="Close dialog window"]',
        )
        self._expand_accordion(
            page,
            selector="button.btn-collapse",
        )
        self._wait(page, ms=1000)
```

Available methods from `BasePage`:

| Method | What it does |
|--------|-------------|
| `_close_popup(page, selector, timeout_ms)` | Clicks a button if it appears within timeout |
| `_expand_accordion(page, selector, timeout_ms)` | Clicks an accordion button if not already expanded |
| `_wait(page, ms)` | Waits a fixed number of milliseconds |

---

## Complete example

```yaml
url:            "https://www.microsoft.com/{region}/microsoft-365/p/outlook/CFQ7TTC0PBMD"
page:           "outlook_pdp"
screenshot_dir: "screenshots/outlook_pdp"
excel_file:     "results/outlook_pdp.xlsx"

_en_regions: &en_regions
  - en-us
  - en-gb
  - en-ca

checks:

  - name:    "Page Title"
    locator: "title"
    type:    head
    expected: "Buy Microsoft Outlook | Microsoft Store"

  - name:      "Page Meta Description"
    locator:   'meta[name="description"]'
    type:      attribute
    attribute: content
    expected:  "Get the Microsoft Outlook app to master your email."
    semantic:  true

  - name:    "Badge"
    locator: "span.badge"
    expected: "First month free"
    regions: *en_regions

  - name:    "CTA 1 text"
    locator: "a.primary-buy-button"
    nth:     0
    expected: "Try free for 1 month"
    regions: *en_regions

  - name:      "CTA 1 URL"
    locator:   "a.primary-buy-button"
    nth:       0
    type:      attribute
    attribute: href
    expected:  "https://www.microsoft.com/{region}/microsoft-365/try-prs"
    regions:   *en_regions
```