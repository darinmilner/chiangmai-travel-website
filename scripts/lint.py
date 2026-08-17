#!/usr/bin/env python3
"""
Linting orchestration script
Reads component config and runs flake8 on each component
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


class LintOrchestrator:
    """Orchestrates linting for all components"""

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
            return yaml.safe_load(f)

    def _lint_component(self, name: str, comp: Dict[str, Any]) -> bool:
        """Run flake8 on a single component"""
        path = Path(comp.get('path', ''))

        if not path.exists():
            logger.warning(f"Component {name} path not found: {path}")
            return False

        logger.info(f"📝 Linting {name} ({path})...")

        # Build flake8 command
        cmd = ['flake8', str(path), '--statistics', '--count']

        # Use component-specific .flake8 config if exists
        flake8_config = path / '.flake8'
        if flake8_config.exists():
            cmd.extend(['--config', str(flake8_config)])
        else:
            # Default settings
            cmd.extend(['--max-line-length', '120'])

        # Run flake8
        result = subprocess.run(
            cmd,
            capture_output=False,  # Show output in real-time
            text=True
        )

        if result.returncode == 0:
            logger.info(f"✅ Linting passed for {name}")
            return True
        else:
            logger.error(f"❌ Linting failed for {name}")
            return False

    def lint_all(self) -> bool:
        """Lint all components"""
        success = True

        for name, comp in self.components.items():
            if not self._lint_component(name, comp):
                success = False

        return success

    def lint_component(self, component_name: str) -> bool:
        """Lint a specific component"""
        comp = self.components.get(component_name)
        if not comp:
            logger.error(f"Component not found: {component_name}")
            return False

        return self._lint_component(component_name, comp)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Lint Lambda components")
    parser.add_argument('--config', required=True, help='Path to components.yml')
    parser.add_argument('--component', help='Specific component to lint (default: all)')

    args = parser.parse_args()

    orchestrator = LintOrchestrator(Path(args.config))

    if args.component:
        success = orchestrator.lint_component(args.component)
    else:
        success = orchestrator.lint_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
