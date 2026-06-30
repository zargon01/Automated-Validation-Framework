"""Core check execution — extract → detect → translate → match → highlight."""

from playwright.sync_api import Page, Locator

from .config_loader import CheckDef, GlobalConfig
from .language import detect_language, translate_to_english
from .text_utils import normalize, semantic_score


class CheckResult:
    def __init__(
        self,
        passed:      bool,
        actual_text: str,
        match_type:  str,
        translated:  str = "",   # populated when element text was translated
    ):
        self.passed      = passed
        self.actual_text = actual_text
        self.match_type  = match_type
        self.translated  = translated    # "" means no translation was needed


def run_check(
    page: Page,
    check: CheckDef,
    config: GlobalConfig,
    resolved_expected: str = "",
) -> CheckResult:
    expected = resolved_expected or check.expected
    locator  = page.locator(check.locator)

    try:
        locator.first.wait_for(state="attached", timeout=10_000)
    except Exception:
        print(f"  ❌ No element found for locator: {check.locator}")
        return CheckResult(False, "element not found", "not_found")

    if check.type == "attribute":
        return _run_attribute_check(locator, check, config, expected)
    elif check.type == "head":
        return _run_head_check(locator, check, config, expected)
    else:
        return _run_text_check(locator, check, config, expected)


# ── Text check ────────────────────────────────────────────────────────────────

def _run_text_check(
    locator: Locator, check: CheckDef, config: GlobalConfig, expected: str
) -> CheckResult:
    expected_norm = normalize(expected)
    best_score    = 0.0
    best_idx      = -1
    best_display  = ""
    best_raw      = ""

    indices = [check.nth] if check.nth >= 0 else range(locator.count())

    for i in indices:
        elem = locator.nth(i)
        raw  = elem.inner_text().lstrip("\n").strip()
        if not raw:
            continue

        lang = detect_language(raw)
        print(f"  [#{i}] lang={lang!r} | {raw[:80]}")

        if lang not in ("en", "unknown"):
            print(f"  [#{i}] Translating {lang!r} → en…")
            display = translate_to_english(raw)
            _inject_translation(elem, display)
        else:
            display = raw

        candidate = normalize(display)

        if expected_norm in candidate:
            print(f"  [#{i}] ✅ Exact match")
            _highlight(elem, "exact")
            translated = display if display != raw else ""
            return CheckResult(True, raw, "exact", translated)

        score = semantic_score(candidate, expected_norm)
        print(f"  [#{i}] semantic_score={score:.3f}")
        if score > best_score:
            best_score, best_idx, best_display, best_raw = score, i, display, raw

    print(f"  Best semantic score: {best_score:.3f} (threshold {config.semantic_threshold})")
    if best_score >= config.semantic_threshold and best_idx >= 0:
        print(f"  [#{best_idx}] ✅ Semantic match accepted")
        _highlight(locator.nth(best_idx), "semantic")
        translated = best_display if best_display != best_raw else ""
        return CheckResult(True, best_raw, "semantic", translated)

    print("  ❌ No match")
    return CheckResult(False, best_raw, "none")


# ── Head check (<title>, <meta>) ──────────────────────────────────────────────

def _run_head_check(
    locator: Locator, check: CheckDef, config: GlobalConfig, expected: str
) -> CheckResult:
    expected_norm = normalize(expected)
    best_score    = 0.0
    best_idx      = -1
    best_display  = ""
    best_raw      = ""

    indices = [check.nth] if check.nth >= 0 else range(locator.count())

    for i in indices:
        elem = locator.nth(i)
        raw  = (elem.text_content() or "").lstrip("\n").strip()
        if not raw:
            continue

        lang = detect_language(raw)
        print(f"  [#{i}] lang={lang!r} | {raw[:80]}")

        translated = translate_to_english(raw)
        display    = translated if translated != raw else raw

        if display != raw:
            print(f"  [#{i}] Translated ({lang!r} → en)")

        candidate = normalize(display)

        if expected_norm in candidate:
            print(f"  [#{i}] ✅ Exact match")
            return CheckResult(True, raw, "exact", display if display != raw else "")

        score = semantic_score(candidate, expected_norm)
        print(f"  [#{i}] semantic_score={score:.3f}")
        if score > best_score:
            best_score, best_idx, best_display, best_raw = score, i, display, raw

    print(f"  Best semantic score: {best_score:.3f} (threshold {config.semantic_threshold})")
    if best_score >= config.semantic_threshold and best_idx >= 0:
        print(f"  [#{best_idx}] ✅ Semantic match accepted")
        translated = best_display if best_display != best_raw else ""
        return CheckResult(True, best_raw, "semantic", translated)

    print("  ❌ No match")
    return CheckResult(False, best_raw, "none")


# ── Attribute check ───────────────────────────────────────────────────────────

def _run_attribute_check(
    locator: Locator, check: CheckDef, config: GlobalConfig, expected: str
) -> CheckResult:
    idx    = max(check.nth, 0)
    elem   = locator.nth(idx)
    actual = (elem.get_attribute(check.attribute) or "").strip()
    print(f"  [#{idx}] {check.attribute}={actual!r}")

    if not check.semantic:
        if normalize(expected) in normalize(actual) or normalize(actual) in normalize(expected):
            print(f"  [#{idx}] ✅ Exact match")
            _highlight(elem, "exact")
            return CheckResult(True, actual, "exact")
        print(f"  ❌ No match — expected: {expected!r}")
        return CheckResult(False, actual, "none")

    lang = detect_language(actual)
    print(f"  [#{idx}] lang={lang!r}")

    if lang not in ("en", "unknown"):
        print(f"  [#{idx}] Translating attribute {lang!r} → en…")
        display = translate_to_english(actual)
    else:
        display = actual

    candidate     = normalize(display)
    expected_norm = normalize(expected)

    if expected_norm in candidate:
        print(f"  [#{idx}] ✅ Exact match (post-translation)")
        _highlight(elem, "exact")
        translated = display if display != actual else ""
        return CheckResult(True, actual, "exact", translated)

    score = semantic_score(candidate, expected_norm)
    print(f"  [#{idx}] semantic_score={score:.3f}")

    if score >= config.semantic_threshold:
        print(f"  [#{idx}] ✅ Semantic match accepted")
        _highlight(elem, "semantic")
        translated = display if display != actual else ""
        return CheckResult(True, actual, "semantic", translated)

    print(f"  ❌ No match (score={score:.3f})")
    return CheckResult(False, display, "none")


# ── DOM helpers ───────────────────────────────────────────────────────────────

def _inject_translation(elem: Locator, translated: str) -> None:
    escaped = translated.replace("\\", "\\\\").replace("`", "\\`")
    try:
        elem.evaluate(f"""el => {{
            const hasChildren = el.children.length > 0;
            if (!hasChildren) {{
                el.innerText = `{escaped}`;
            }} else {{
                el.setAttribute('data-qa-translation', `{escaped}`);
                const overlay = document.createElement('div');
                overlay.className = 'qa-translation-overlay';
                overlay.textContent = `{escaped}`;
                overlay.style.cssText =
                    'background:#1a73e8;color:white;font-size:11px;'
                    + 'padding:2px 6px;border-radius:3px;margin-bottom:4px;'
                    + 'white-space:pre-wrap;';
                el.parentElement.insertBefore(overlay, el);
            }}
        }}""")
    except Exception:
        pass


def _highlight(elem: Locator, match_type: str) -> None:
    if match_type == "exact":
        bg, outline = "yellow", "3px solid green"
    else:
        bg, outline = "lightyellow", "3px solid red"
    try:
        elem.evaluate(f"""el => {{
            el.scrollIntoView({{behavior:'auto', block:'center'}});
            el.style.backgroundColor = '{bg}';
            el.style.outline = '{outline}';
            el.style.borderRadius = '3px';
        }}""")
    except Exception:
        pass