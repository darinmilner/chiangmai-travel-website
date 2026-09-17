#!/usr/bin/env python3
"""
Deployment orchestration script
Uses Terraform to deploy Lambda components as full modules
"""
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any
import os
import yaml
import shutil
import subprocess
import zipfile


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from terraform_wrapper import TerraformWrapper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeployOrchestrator:
    """Orchestrates module-level deployment via Terraform"""

    def __init__(self, config_path: Path, environment: str):
        self.config_path = config_path
        self.environment = environment
        self.config = self._load_config()
        self.components = self.config.get('components', {})
        self.terraform_config = self.config.get('deploy/terraform', {})

        # Default root terraform directory if executing global actions
        tf_path = self.terraform_config.get('path', 'deployment/terraform')
        self.tf_dir = Path(__file__).parent.parent / tf_path

        self.terraform = TerraformWrapper(
            environment=environment,
            tf_dir=self.tf_dir
        )

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return {'components': {}, 'deploy/terraform': {}}

        with open(self.config_path) as f:
            return yaml.safe_load(f) or {}

    def deploy_all(self) -> bool:
        """Deploy all infrastructure across configured component modules"""
        logger.info("🚀 Deploying ALL infrastructure components via Terraform")
        success = True

        for name, comp in self.components.items():
            if 'path' in comp:
                if not self.deploy_component(name):
                    success = False

        if success:
            logger.info("✅ All infrastructure deployed successfully")
        else:
            logger.error("❌ One or more components failed during deployment")

        return success

    def deploy_component(self, component_name: str) -> bool:
        """Deploy an entire Terraform module directory for a component"""
        comp = self.components.get(component_name)
        if not comp or 'path' not in comp:
            logger.error(f"Component or 'path' field not found in config: {component_name}")
            return False

        module_dir = Path(__file__).parent.parent / comp['path']
        logger.info(f"📤 Deploying module '{component_name}' at {module_dir}")

        # --- BUILD HOOK FOR IMAGE PROCESSOR ---
        if component_name == "image-processor":
            logger.info(f"⚙️ Pre-building Pillow layer at {module_dir}...")
            self.build_pillow_layer(output_dir=module_dir)
        # --------------------------------------

        extra_env = {}
        tf_var_name = comp.get('tf_var_name')
        artifact_rel_path = comp.get('artifact')

        if tf_var_name and artifact_rel_path:
            abs_artifact_path = (Path(__file__).parent.parent / artifact_rel_path).resolve()

            if not abs_artifact_path.exists():
                logger.error(f"❌ Required deployment zip missing at: {abs_artifact_path}")
                return False

            extra_env[f"TF_VAR_{tf_var_name}"] = str(abs_artifact_path)
            logger.info(f"🔑 Injected variable: TF_VAR_{tf_var_name}={abs_artifact_path}")

        tf = TerraformWrapper(
            environment=self.environment,
            tf_dir=module_dir,
            extra_env_vars=extra_env
        )

        if not tf.init() or not tf.validate():
            return False

        if not tf.plan() or not tf.apply():
            logger.error(f"❌ Deployment failed for module: {component_name}")
            return False

        logger.info(f"✅ Component module '{component_name}' deployed successfully")
        return True

    def destroy_component(self, component_name: str) -> bool:
        """Destroy an entire Terraform module directory for a component"""
        comp = self.components.get(component_name)
        if not comp or 'path' not in comp:
            logger.error(f"Component or 'path' field not found in config: {component_name}")
            return False

        module_dir = Path(__file__).parent.parent / comp['path']
        logger.warning(f"⚠️ Destroying module '{component_name}' at {module_dir}")

        tf = TerraformWrapper(environment=self.environment, tf_dir=module_dir)

        if not tf.init():
            return False

        if not tf.destroy():
            logger.error(f"❌ Destruction failed for module: {component_name}")
            return False

        logger.info(f"✅ Component module '{component_name}' destroyed successfully")
        return True

    def build_pillow_layer(
        self,
        output_dir: Path,
        python_version: str = "3.13",
        platform: str = "manylinux2014_x86_64"
    ) -> Path:
        """
        Downloads platform-specific Pillow wheels for AWS Lambda and packages
        them into a zipped layer structure (python/ directory at archive root).
        """
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        zip_path = target_dir / "pillow-layer.zip"

        build_root = Path(".layer-temp")
        python_dir = build_root / "python"

        if build_root.exists():
            shutil.rmtree(build_root)
        python_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📦 Fetching Pillow binary for Python {python_version} ({platform})...")

        pip_cmd = [
            "python3", "-m", "pip", "install",
            "--platform", platform,
            "--target", str(python_dir),
            "--implementation", "cp",
            "--python-version", python_version,
            "--only-binary=:all:",
            "--upgrade",
            "Pillow"
        ]

        res = subprocess.run(pip_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Pip download failed:\n{res.stderr}")

        logger.info(f"🗜️ Creating layer archive at {zip_path}...")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in build_root.rglob("*"):
                arcname = file.relative_to(build_root)
                zf.write(file, arcname)

        shutil.rmtree(build_root)
        logger.info("✅ Pillow layer prepared successfully.")
        return zip_path


def main():
    default_env = os.environ.get("ENVIRONMENT") or os.environ.get("TF_VAR_environment") or "beta"
    parser = argparse.ArgumentParser(description="Deployer CLI")
    parser.add_argument("--command", choices=["deploy", "destroy", "all", "component"], required=True)
    parser.add_argument("--component", default="all", help="Component name (e.g., layer, kms, ses, image-processor, or all)")
    parser.add_argument("--config", required=True, help="Path to components config file")
    parser.add_argument("--environment", default=default_env, help="Deployment environment")

    args = parser.parse_args()

    deployer = DeployOrchestrator(
        config_path=Path(args.config),
        environment=args.environment
    )

    if args.command in ["deploy", "all", "component"]:
        if args.component == "all":
            if not deployer.deploy_all():
                sys.exit(1)
        else:
            if not deployer.deploy_component(args.component):
                sys.exit(1)

    elif args.command == "destroy":
        if not args.component or args.component == "all":
            logger.error("❌ You must specify a specific --component to destroy (e.g., --component layer).")
            sys.exit(1)

        if not deployer.destroy_component(args.component):
            sys.exit(1)


if __name__ == "__main__":
    main()
