#!/usr/bin/env python3
"""
Testing orchestration script
Reads component paths from config and installs dependencies
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

        # Install dependencies
        self._install_dependencies()
        self._check_pytest()

    def _install_dependencies(self):
        """Install dependencies from all component requirements.txt files"""
        logger.info("📦 Installing dependencies from component requirements.txt files...")

        for name, comp in self.components.items():
            req_file = comp.get('requirements')
            if req_file and Path(req_file).exists():
                logger.info(f"📦 Installing from {req_file}")
                subprocess.run(
                    ['pip', 'install', '-r', req_file],
                    capture_output=False
                )

    def _check_pytest(self):
        """Check if pytest is installed"""
        try:
            subprocess.run(['pytest', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ pytest not found. Please ensure it's in your requirements.txt")
            sys.exit(1)

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

        result = subprocess.run(
            cmd,
            cwd=str(path),
            capture_output=False,
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


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Test Lambda components")
    parser.add_argument('--config', required=True, help='Path to components.yml')
    parser.add_argument('--artifacts', required=True, help='Artifacts directory')

    args = parser.parse_args()

    orchestrator = TestOrchestrator(
        config_path=Path(args.config),
        artifacts_dir=Path(args.artifacts)
    )

    success = orchestrator.test_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
