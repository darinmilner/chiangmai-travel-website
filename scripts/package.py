#!/usr/bin/env python3
"""
Packaging orchestrator script
Packages Lambda layers and Lambda functions into deployment artifacts.
"""
import sys
import shutil
import argparse
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PackageOrchestrator:

    def __init__(self, config_path: Path, artifacts_dir: Path):
        self.config_path = config_path.resolve()
        self.project_root = self.config_path.parent.parent
        self.artifacts_dir = artifacts_dir.resolve()
        self.scripts_dir = Path(__file__).parent.resolve()

        self.config = self._load_config()
        self.components = self.config.get('components', {})

        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return {'components': {}}

        with open(self.config_path) as f:
            return yaml.safe_load(f) or {'components': {}}

    def _get_target_zip_path(self, name: str, comp: Dict[str, Any]) -> Path:
        """Derive target zip path from component config 'artifact' field or fallback to {name}.zip"""
        artifact_path = comp.get('artifact')
        if artifact_path:
            return self.artifacts_dir / Path(artifact_path).name
        return self.artifacts_dir / f"{name}.zip"

    def _package_layer(self, name: str, comp: Dict[str, Any]) -> bool:
        """Package Lambda Layer via package_layer.sh and normalize output artifact path"""
        source_dir = comp.get('source_path') or comp.get('path', '')
        source_path = (self.project_root / source_dir).resolve()
        script_path = self.scripts_dir / 'package_layer.sh'

        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            return False

        logger.info(f"📦 Packaging layer '{name}' from {source_dir}...")

        result = subprocess.run([
            "bash",
            str(script_path),
            str(source_path),
            str(self.artifacts_dir)
        ], capture_output=False)

        if result.returncode != 0:
            logger.error(f"❌ package_layer.sh failed for {name}")
            return False

        target_zip = self._get_target_zip_path(name, comp)

        if target_zip.exists():
            logger.info(f"✅ Created artifact: {target_zip}")
            return True

        # Copy generated zip from dist/ or artifacts/ to target_zip
        search_dirs = [self.project_root / 'dist', self.artifacts_dir]
        found_zip = None

        for d in search_dirs:
            if d.exists():
                zips = list(d.glob("*.zip"))
                if zips:
                    zips.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    found_zip = zips[0]
                    break

        if found_zip and found_zip.exists():
            if found_zip.resolve() != target_zip.resolve():
                shutil.copy2(found_zip, target_zip)
                logger.info(f"✅ Copied {found_zip.name} -> {target_zip.name}")
            else:
                logger.info(f"✅ Found artifact: {target_zip}")
            return True

        logger.error(f"❌ {target_zip.name} not found and could not be resolved.")
        return False

    def _package_lambda(self, name: str, comp: Dict[str, Any]) -> bool:
        """Package standard Lambda component"""
        source_dir = comp.get('source_path') or comp.get('path', '')
        source_path = (self.project_root / source_dir).resolve()

        if not source_path.exists():
            logger.error(f"❌ Source path for '{name}' does not exist: {source_path}")
            return False

        target_zip = self._get_target_zip_path(name, comp)
        logger.info(f"📦 Packaging Lambda '{name}' from {source_dir} -> {target_zip}")

        shutil.make_archive(
            base_name=str(target_zip.with_suffix('')),
            format='zip',
            root_dir=str(source_path)
        )

        if target_zip.exists():
            logger.info(f"✅ Lambda '{name}' successfully packaged: {target_zip}")
            return True

        logger.error(f"❌ Failed to create zip for {name}")
        return False

    def package(self, target_component: str = 'all') -> bool:
        """Package target component or all components"""
        if target_component != 'all':
            comp = self.components.get(target_component)
            if not comp:
                logger.error(f"❌ Component '{target_component}' not found in configuration.")
                return False

            comp_type = comp.get('type', 'lambda')

            # Skip packaging for pure infrastructure / Terraform modules
            if comp_type == 'terraform':
                logger.info(f"ℹ️ Component '{target_component}' is pure Terraform. Skipping packaging.")
                return True

            if comp_type == 'layer':
                return self._package_layer(target_component, comp)
            return self._package_lambda(target_component, comp)

        logger.info("🚀 Packaging all components...")
        success = True
        for name, comp in self.components.items():
            comp_type = comp.get('type', 'lambda')

            # Skip Terraform components during 'all' packaging
            if comp_type == 'terraform':
                logger.info(f"ℹ️ Skipping non-code component: {name}")
                continue

            logger.info(f"📦 Packaging {name} ({comp.get('path')})...")
            if comp_type == 'layer':
                if not self._package_layer(name, comp):
                    success = False
            else:
                if not self._package_lambda(name, comp):
                    success = False

        return success


def main():
    parser = argparse.ArgumentParser(description="Package components for deployment")
    parser.add_argument('--config', required=True, help='Path to components.yml')
    parser.add_argument('--artifacts', required=True, help='Directory to store artifact output zip files')
    parser.add_argument('--component', default='all', help='Component to package (default: all)')

    args = parser.parse_args()

    orchestrator = PackageOrchestrator(
        config_path=Path(args.config),
        artifacts_dir=Path(args.artifacts)
    )

    success = orchestrator.package(args.component)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
