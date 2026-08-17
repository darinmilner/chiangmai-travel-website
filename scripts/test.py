#!/usr/bin/env python3
"""
Testing orchestration script
Reads component config and runs pytest on each component
"""
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestOrchestrator:
    """Orchestrates testing for all components"""

    def __init__(self, config_path: Path, artifacts_dir: Path):
        self.config_path = config_path
        self.artifacts_dir = artifacts_dir
        self.config = self._load_config()
        self.components = self.config.get('components', {})

        # Create artifacts directory
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.test_reports_dir = self.artifacts_dir / 'test-reports'
        self.test_reports_dir.mkdir(exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return {'components': {}}

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _test_component(self, name: str, comp: Dict[str, Any]) -> bool:
        """Run pytest on a single component"""
        path = Path(comp.get('path', ''))
        tests_path = path / 'tests'

        if not tests_path.exists():
            logger.info(f"No tests found for {name}, skipping")
            return True

        logger.info(f"🧪 Testing {name} ({path})...")

        # Build pytest command
        cmd = [
            'pytest',
            str(tests_path),
            '-v',
            '--maxfail', '5',
            '--tb', 'short'
        ]

        # Add coverage if src exists
        src_path = path / 'src'
        if src_path.exists():
            cmd.extend([
                '--cov', str(src_path),
                '--cov-report', 'term',
                '--cov-report', f'html:{self.test_reports_dir}/coverage-{name}',
                '--cov-report', f'xml:{self.test_reports_dir}/coverage-{name}.xml'
            ])

        # Add junit reporting
        junit_path = self.test_reports_dir / f'junit-{name}.xml'
        cmd.extend(['--junitxml', str(junit_path)])

        # Run pytest
        result = subprocess.run(
            cmd,
            cwd=str(path),
            capture_output=False,  # Show output in real-time
            text=True
        )

        if result.returncode == 0:
            logger.info(f"✅ Tests passed for {name}")
            return True
        else:
            logger.error(f"❌ Tests failed for {name}")
            return False

    def test_all(self) -> bool:
        """Test all components"""
        success = True

        for name, comp in self.components.items():
            if not self._test_component(name, comp):
                success = False

        return success

    def test_component(self, component_name: str) -> bool:
        """Test a specific component"""
        comp = self.components.get(component_name)
        if not comp:
            logger.error(f"Component not found: {component_name}")
            return False

        return self._test_component(component_name, comp)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Test Lambda components")
    parser.add_argument('--config', required=True, help='Path to components.yml')
    parser.add_argument('--artifacts', required=True, help='Artifacts directory')
    parser.add_argument('--component', help='Specific component to test (default: all)')

    args = parser.parse_args()

    orchestrator = TestOrchestrator(
        config_path=Path(args.config),
        artifacts_dir=Path(args.artifacts)
    )

    if args.component:
        success = orchestrator.test_component(args.component)
    else:
        success = orchestrator.test_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
