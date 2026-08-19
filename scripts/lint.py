#!/usr/bin/env python3
"""
Linting orchestration script
Reads component paths from config and runs flake8 using local .flake8 configs.
"""
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LintOrchestrator:
    """Orchestrates flake8 static code analysis for components using local .flake8 configs"""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()
        self.components = self.config.get('components', {})

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return {'components': {}}

        with open(self.config_path) as f:
            return yaml.safe_load(f) or {'components': {}}

    def check_flake8(self) -> bool:
        """Verify flake8 executable is available"""
        try:
            subprocess.run(['flake8', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ flake8 not found. Please ensure 'flake8' is installed in the environment.")
            return False

    def _find_flake8_config(self, component_path: Path) -> Optional[Path]:
        """
        Search for .flake8 file starting at the component path
        and walking up to the repository root directory.
        """
        current = component_path.resolve()
        root = Path.cwd().resolve()

        while True:
            config_file = current / '.flake8'
            if config_file.exists():
                return config_file
            if current == root or current.parent == current:
                break
            current = current.parent

        return None

    def _lint_component(self, name: str, comp: Dict[str, Any]) -> bool:
        """Run flake8 on a single component path using its local .flake8 config"""
        path_str = comp.get('path')
        if not path_str:
            logger.warning(f"⚠️ Component '{name}' has no path defined. Skipping.")
            return True

        path = Path(path_str)
        if not path.exists():
            logger.warning(f"⚠️ Component '{name}' path not found: {path}")
            return False

        logger.info(f"📝 Linting component '{name}' at {path}...")

        # Base flake8 command
        cmd = ['flake8', str(path), '--statistics', '--count']

        # Discover and attach local .flake8 config file
        config_file = self._find_flake8_config(path)
        if config_file:
            logger.info(f"   Using configuration: {config_file}")
            cmd.extend(['--config', str(config_file)])
        else:
            logger.info("   No .flake8 file found; using default flake8 rules.")

        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode == 0:
            logger.info(f"✅ Linting passed for {name}\n")
            return True
        else:
            logger.error(f"❌ Linting failed for {name}\n")
            return False

    def lint(self, component_name: Optional[str] = 'all') -> bool:
        """Lint specific component or all components"""
        if not self.check_flake8():
            return False

        if component_name and component_name != 'all':
            if component_name not in self.components:
                logger.error(f"❌ Component '{component_name}' not found in {self.config_path}")
                return False
            return self._lint_component(component_name, self.components[component_name])

        success = True
        for name, comp in self.components.items():
            if not self._lint_component(name, comp):
                success = False

        return success


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Lint Lambda components")
    parser.add_argument('--config', required=True, help='Path to components.yml')
    parser.add_argument('--component', default='all', help='Target component to lint (default: all)')

    args = parser.parse_args()

    orchestrator = LintOrchestrator(Path(args.config))
    success = orchestrator.lint(args.component)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
