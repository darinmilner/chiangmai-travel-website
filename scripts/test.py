#!/usr/bin/env python3
"""
Test orchestration script
Runs pytest for Lambda components with existing test directories
"""
import os
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

        # Skip pure infrastructure components
        if comp_type == 'infra':
            logger.info(f"⏭️ Skipping {name} (infrastructure-only component)")
            return True

        path = Path(comp.get('path', ''))
        test_dir = path / "tests"

        if not test_dir.exists():
            logger.info(f"⏭️ No 'tests/' directory found for {name} ({test_dir}), skipping...")
            return True

        # Install component requirements if present
        req_file = path / "requirements.txt"
        if req_file.exists():
            logger.info(f"📦 Installing dependencies for {name} from {req_file}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)],
                check=False
            )

        logger.info(f"🧪 Testing {name} ({test_dir})...")

        xml_report = self.reports_dir / f"junit-{name}.xml"

        # Inject component directory into PYTHONPATH for imports
        env = os.environ.copy()
        current_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{path.resolve()}:{current_pythonpath}"

        cmd = [
            "pytest",
            str(test_dir),
            f"--junitxml={xml_report}"
        ]

        result = subprocess.run(cmd, env=env, capture_output=False)
        if result.returncode not in (0, 5):  # 0 = passed, 5 = no tests collected
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
