#!/usr/bin/env python3
"""
Test orchestration script
Runs pytest for Lambda components with existing test directories
"""
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestOrchestrator:
    def __init__(self, config_path: Path, artifacts_dir: Path):
        self.config_path = config_path
        self.artifacts_dir = artifacts_dir
        self.config = self._load_config()
        self.components = self.config.get('components', {})
        self.reports_dir = self.artifacts_dir / "test-reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return {'components': {}}
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _test_component(self, name: str, comp: Dict[str, Any]) -> bool:
        comp_type = comp.get('type', '')

        # 1. Skip pure infrastructure components (e.g. CloudFront)
        if comp_type == 'infra':
            logger.info(f"⏭️ Skipping {name} (infrastructure-only component)")
            return True

        path = Path(comp.get('path', ''))
        test_dir = path / "tests"

        # 2. Check if the test directory actually exists
        if not test_dir.exists():
            logger.info(f"⏭️ No 'tests/' directory found for {name} ({test_dir}), skipping...")
            return True

        logger.info(f"🧪 Testing {name} ({test_dir})...")

        xml_report = self.reports_dir / f"junit-{name}.xml"
        cmd = [
            "pytest",
            str(test_dir),
            f"--junitxml={xml_report}"
        ]

        result = subprocess.run(cmd, capture_output=False)
        if result.returncode not in (0, 5):  # 5 = no tests collected
            logger.error(f"❌ Tests failed for {name}")
            return False

        return True

    def test_all(self) -> bool:
        success = True
        for name, comp in self.components.items():
            if not self._test_component(name, comp):
                success = False
        return success


def main():
    parser = argparse.ArgumentParser(description="Run component tests")
    parser.add_argument('--config', required=True, help='Path to components.yml')
    parser.add_argument('--artifacts', required=True, help='Artifacts directory')

    args = parser.parse_args()
    orchestrator = TestOrchestrator(
        config_path=Path(args.config),
        artifacts_dir=Path(args.artifacts)
    )

    sys.exit(0 if orchestrator.test_all() else 1)


if __name__ == "__main__":
    main()
