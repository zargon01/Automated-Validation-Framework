from dataclasses import dataclass, field
from typing import List
import yaml


@dataclass
class CheckDef:
    name:            str
    locator:         str
    expected:        str
    type:            str       = "text"
    attribute:       str       = ""
    nth:             int       = -1
    regions:         List[str] = field(default_factory=list)
    exclude_regions: List[str] = field(default_factory=list)
    semantic:        bool      = False


@dataclass
class GlobalConfig:
    # screenshot_dir and excel_file removed — now live in SuiteConfig
    semantic_threshold:      float
    translation_timeout_s:   int
    translation_poll_s:      float
    after_translate_wait_ms: int
    headless:                bool
    slow_mo:                 int


@dataclass
class SuiteConfig:
    url:            str
    page:           str
    checks:         List[CheckDef]
    screenshot_dir: str   # suite-specific screenshot folder
    excel_file:     str   # suite-specific Excel output file


def load_global(path: str = "config.yaml") -> GlobalConfig:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return GlobalConfig(
        semantic_threshold      = raw.get("semantic_threshold", 0.60),
        translation_timeout_s   = raw.get("translation_timeout_s", 30),
        translation_poll_s      = raw.get("translation_poll_s", 0.5),
        after_translate_wait_ms = raw.get("after_translate_wait_ms", 3000),
        headless                = raw.get("headless", False),
        slow_mo                 = raw.get("slow_mo", 100),
    )


def load_suite(path: str) -> SuiteConfig:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    checks = []
    for c in raw.get("checks", []):
        regions         = [r.lower() for r in (c.pop("regions", []) or [])]
        exclude_regions = [r.lower() for r in (c.pop("exclude_regions", []) or [])]
        checks.append(CheckDef(**c, regions=regions, exclude_regions=exclude_regions))

    return SuiteConfig(
        url            = raw["url"],
        page           = raw["page"],
        checks         = checks,
        screenshot_dir = raw.get("screenshot_dir", "screenshots"),
        excel_file     = raw.get("excel_file", "regions_checks.xlsx"),
    )