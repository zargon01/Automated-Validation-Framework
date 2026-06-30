"""Entry point.

Usage:
    python run.py --checks checks/ms365_family.yaml
    python run.py --checks checks/ms365_personal.yaml
    python run.py --checks checks/ms365_family.yaml --config config.yaml
"""

import argparse
from qa.config_loader import load_global, load_suite
from qa.orchestrator import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QA Automation Framework")
    parser.add_argument(
        "--checks", required=True,
        help="Path to check suite yaml  e.g. checks/ms365_family.yaml"
    )
    parser.add_argument(
        "--config", default="config.yaml",
        help="Path to global config yaml (default: config.yaml)"
    )
    args = parser.parse_args()

    global_cfg = load_global(args.config)
    suite      = load_suite(args.checks)
    run(global_cfg, suite)