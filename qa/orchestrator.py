"""Orchestrator — wires every module together. Contains no business logic."""

import os
import json

from playwright.sync_api import Page

from .config_loader import GlobalConfig, SuiteConfig
from .browser import BrowserManager
from .page_loader import load_page
from .check_runner import run_check
from .reporter import load_regions, write_results
from .text_utils import get_model


def _should_run(check, region: str) -> bool:
    r = region.lower()
    if check.regions and r not in check.regions:
        return False
    if check.exclude_regions and r in check.exclude_regions:
        return False
    return True


def _inject_verification_banner(page: Page, checks, results) -> None:
    rows = []
    for check, result in zip(checks, results):
        if result is None:
            continue
        icon   = "✅" if result.passed else "❌"
        status = result.match_type.upper() if result.passed else "FAIL"
        actual = (result.actual_text or "")[:120]
        rows.append({"icon": icon, "name": check.name, "status": status, "actual": actual})

    rows_json = json.dumps(rows)
    page.evaluate(f"""() => {{
        const rows = {rows_json};
        const banner = document.createElement('div');
        banner.style.cssText = [
            'position:fixed','top:0','left:0','right:0','z-index:999999',
            'background:#1e1e2e','color:#cdd6f4','font-family:monospace',
            'font-size:12px','padding:8px 12px','box-shadow:0 2px 8px rgba(0,0,0,0.5)',
            'max-height:40vh','overflow-y:auto'
        ].join(';');
        const title = document.createElement('div');
        title.textContent = '🔍 QA Verification Report';
        title.style.cssText = 'font-weight:bold;font-size:13px;margin-bottom:6px;color:#cba6f7';
        banner.appendChild(title);
        rows.forEach(r => {{
            const row = document.createElement('div');
            row.style.cssText = 'display:flex;gap:8px;padding:2px 0;border-bottom:1px solid #313244';
            const icon   = document.createElement('span');
            icon.textContent = r.icon; icon.style.minWidth = '20px';
            const status = document.createElement('span');
            status.textContent = '[' + r.status + ']';
            status.style.cssText = 'min-width:80px;color:' + (r.icon==='✅'?'#a6e3a1':'#f38ba8');
            const name = document.createElement('span');
            name.textContent = r.name; name.style.cssText = 'min-width:220px;color:#89b4fa';
            const actual = document.createElement('span');
            actual.textContent = r.actual; actual.style.cssText = 'color:#a6adc8';
            row.appendChild(icon); row.appendChild(status);
            row.appendChild(name); row.appendChild(actual);
            banner.appendChild(row);
        }});
        document.body.insertBefore(banner, document.body.firstChild);
        document.body.style.marginTop = banner.offsetHeight + 'px';
    }}""")
    page.wait_for_timeout(300)


def run(global_cfg: GlobalConfig, suite: SuiteConfig) -> None:
    get_model()
    os.makedirs(suite.screenshot_dir, exist_ok=True)

    regions = load_regions(global_cfg, suite)
    if not regions:
        print("❌ No regions found in Excel. Add region codes in column A.")
        return

    print(f"\n📋 {len(regions)} region(s): {[r['region'] for r in regions]}")
    print(f"📄 Page class: {suite.page}")
    print(f"🔍 Checks: {[c.name for c in suite.checks]}\n")

    page_obj = load_page(suite.page)

    with BrowserManager(global_cfg) as bm:
        page: Page = bm.new_page()

        for entry in regions:
            region = entry["region"]
            row    = entry["row"]
            url    = suite.url.format(region=region)

            print(f"\n{'='*60}")
            print(f"▶  {region}  →  {url}")
            print(f"{'='*60}")

            page.goto(url, wait_until="domcontentloaded")
            page_obj.setup(page, global_cfg)

            results    = []
            all_passed = True

            for check in suite.checks:
                if not _should_run(check, region):
                    print(f"\n  ⏭  Skipped (not applicable for {region}): {check.name}")
                    results.append(None)
                    continue

                print(f"\n  🔍 {check.name}")
                resolved_expected = check.expected.replace("{region}", region.lower())
                result = run_check(page, check, global_cfg, resolved_expected)
                results.append(result)

                status = "✅ PASS" if result.passed else "❌ FAIL"
                tag    = f"[{result.match_type}]" if result.passed else ""
                print(f"  {status} {tag}: {check.name}")

                if not result.passed:
                    all_passed = False

            active_checks  = [c for c in suite.checks if _should_run(c, region)]
            active_results = [r for r in results if r is not None]
            _inject_verification_banner(page, active_checks, active_results)

            shot_path = os.path.join(
                suite.screenshot_dir, f"{suite.page} {region}.png"
            )
            page.screenshot(path=shot_path, full_page=True)
            print(f"\n  📌 Screenshot: {shot_path}")

            write_results(global_cfg, suite, row, region, url, results)
            print(f"  {'🎉 All passed' if all_passed else '⚠️  Some checks failed'} for {region}")

    print(f"\n✅ Results written to {suite.excel_file}")