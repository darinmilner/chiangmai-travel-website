#!/usr/bin/env python3
"""
Packaging orchestration script
Reads component paths from config
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


class PackageOrchestrator:
    """Orchestrates packaging for all components"""

    def __init__(self, config_path: Path, artifacts_dir: Path):
        self.config_path = config_path
        self.artifacts_dir = artifacts_dir
        self.config = self._load_config()
        self.components = self.config.get('components', {})
        self.scripts_dir = Path(__file__).parent

        # Create artifacts directory
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return {'components': {}}

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _package_component(self, name: str, comp: Dict[str, Any]) -> bool:
        """Package a single component"""
        path = Path(comp.get('path', ''))
        comp_type = comp.get('type', '')

        if not path.exists():
            logger.error(f"Component {name} path not found: {path}")
            return False

        logger.info(f"📦 Packaging {name} ({path})...")

        if comp_type == 'layer':
            return self._package_layer(name, path)
        elif comp_type == 'lambda':
            return self._package_lambda(name, path)
        else:
            logger.error(f"Unknown component type: {comp_type}")
            return False

    def _package_layer(self, name: str, path: Path) -> bool:
        """Package a Lambda layer"""
        script_path = self.scripts_dir / 'package_layer.sh'

        result = subprocess.run([
            str(script_path),
            str(path),
            str(self.artifacts_dir)
        ], capture_output=False)

        return result.returncode == 0

    def _package_lambda(self, name: str, path: Path) -> bool:
        """Package a Lambda function"""
        script_path = self.scripts_dir / 'package_lambda.sh'

        result = subprocess.run([
            str(script_path),
            name,
            str(path),
            str(self.artifacts_dir)
        ], capture_output=False)

        return result.returncode == 0

    def package_all(self) -> bool:
        """Package all components"""
        success = True

        for name, comp in self.components.items():
            if not self._package_component(name, comp):
                success = False

        return success


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Package Lambda components")
    parser.add_argument('--config', required=True, help='Path to components.yml')
    parser.add_argument('--artifacts', required=True, help='Artifacts directory')

    args = parser.parse_args()

    orchestrator = PackageOrchestrator(
        config_path=Path(args.config),
        artifacts_dir=Path(args.artifacts)
    )

    success = orchestrator.package_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
