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
import yaml
from pathlib import Path
from typing import Dict, Any, List


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestOrchestrator:
    def __init__(self, config_path: Path, artifacts_dir: Path):
        self.config_path = config_path.resolve()
        # Anchor relative component paths to the directory containing the config file
        self.repo_root = self.config_path.parent
        self.artifacts_dir = artifacts_dir.resolve()
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

    def _find_test_dirs(self, comp_path: Path) -> List[Path]:
        """Recursively find all 'tests' directories under component path"""
        if not comp_path.exists():
            return []
        return [p for p in comp_path.rglob("tests") if p.is_dir()]

    def _test_component(self, name: str, comp: Dict[str, Any]) -> bool:
        comp_type = comp.get('type', '')

        # Skip pure infrastructure components
        if comp_type == 'infra':
            logger.info(f"⏭️ Skipping {name} (infrastructure-only component)")
            return True

        # Resolve relative to config location
        raw_path = comp.get('path', '')
        path = (self.repo_root / raw_path).resolve()

        test_dirs = self._find_test_dirs(path)

        if not test_dirs:
            logger.info(f"⏭️ No 'tests/' directory found for {name} under ({path}), skipping...")
            return True

        # Install component requirements if present anywhere in module
        for req_file in set(path.rglob("requirements.txt")):
            logger.info(f"📦 Installing dependencies for {name} from {req_file}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)],
                check=False
            )

        component_success = True

        for test_dir in test_dirs:
            logger.info(f"🧪 Testing {name} ({test_dir})...")

            sub_name = test_dir.parent.name if test_dir.parent != path else name
            xml_report = self.reports_dir / f"junit-{name}-{sub_name}.xml"

            # Build PYTHONPATH entries dynamically based on directory layout
            parent = test_dir.parent
            extra_paths = []

            # 1. If sibling 'python' directory exists (e.g., shared-layer/python)
            if (parent / "python").is_dir():
                extra_paths.append(str((parent / "python").resolve()))

            # 2. If sibling 'src' directory exists (e.g., image-processor/src)
            if (parent / "src").is_dir():
                extra_paths.append(str((parent / "src").resolve()))

            # 3. Include parent and component root path
            extra_paths.append(str(parent.resolve()))
            extra_paths.append(str(path.resolve()))

            # Deduplicate paths preserving insertion order
            seen = set()
            unique_paths = [p for p in extra_paths if not (p in seen or seen.add(p))]

            env = os.environ.copy()
            current_pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = ":".join(unique_paths + ([current_pythonpath] if current_pythonpath else []))

            cmd = [
                "pytest",
                str(test_dir),
                f"--junitxml={xml_report}"
            ]

            result = subprocess.run(cmd, env=env, capture_output=False)
            if result.returncode not in (0, 5):  # 0 = passed, 5 = no tests collected
                logger.error(f"❌ Tests failed for {name} in {test_dir}")
                component_success = False

        return component_success

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
