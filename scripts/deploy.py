#!/usr/bin/env python3
"""
Deployment orchestration script
Uses Terraform to deploy Lambda components
"""

import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

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
    """Orchestrates deployment via Terraform"""

    def __init__(self, config_path: Path, environment: str):
        self.config_path = config_path
        self.environment = environment
        self.config = self._load_config()
        self.components = self.config.get('components', {})
        self.terraform_config = self.config.get('terraform', {})

        # Get terraform path from config
        tf_path = self.terraform_config.get('path', 'terraform')
        self.tf_dir = Path(__file__).parent.parent / tf_path

        # Initialize Terraform wrapper
        self.terraform = TerraformWrapper(
            environment=environment,
            tf_dir=self.tf_dir
        )

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return {'components': {}, 'terraform': {}}

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _get_component_resource(self, component_name: str) -> Optional[str]:
        """Get Terraform resource for a component"""
        comp = self.components.get(component_name)
        if not comp:
            logger.error(f"Component not found: {component_name}")
            return None

        return comp.get('terraform_resource')

    def deploy_all(self) -> bool:
        """Deploy all infrastructure via Terraform"""
        logger.info("🚀 Deploying ALL infrastructure via Terraform")

        if not self.terraform.init() or not self.terraform.validate():
            return False

        if not self.terraform.plan() or not self.terraform.apply():
            return False

        logger.info("✅ All infrastructure deployed successfully")
        return True

    def deploy_component(self, component_name: str) -> bool:
        """Deploy a specific component via Terraform"""
        resource = self._get_component_resource(component_name)
        if not resource:
            return False

        logger.info(f"📤 Deploying {component_name} (resource: {resource})")

        if not self.terraform.init() or not self.terraform.validate():
            return False

        tf_dir = self.tf_dir

        # Plan with target
        plan_cmd = ['terraform', 'plan', '-target', resource, '-out=plan.tfplan']
        if subprocess.run(plan_cmd, cwd=str(tf_dir), capture_output=False).returncode != 0:
            logger.error(f"Plan failed for {component_name}")
            return False

        # Apply with target
        apply_cmd = ['terraform', 'apply', '-target', resource, '-auto-approve', 'plan.tfplan']
        if subprocess.run(apply_cmd, cwd=str(tf_dir), capture_output=False).returncode == 0:
            logger.info(f"✅ {component_name} deployed successfully")
            return True

        logger.error(f"❌ {component_name} deployment failed")
        return False

    def destroy_component(self, component_name: str) -> bool:
        """Destroy a specific component via Terraform"""
        resource = self._get_component_resource(component_name)
        if not resource:
            return False

        logger.warning(f"⚠️ Initiating DESTROY for '{component_name}' (resource: {resource})")

        if not self.terraform.init():
            return False

        tf_dir = self.tf_dir
        destroy_cmd = ['terraform', 'destroy', '-target', resource, '-auto-approve']

        if subprocess.run(destroy_cmd, cwd=str(tf_dir), capture_output=False).returncode == 0:
            logger.info(f"✅ {component_name} destroyed successfully")
            return True

        logger.error(f"❌ {component_name} destruction failed")
        return False


def main():
    parser = argparse.ArgumentParser(description="Deployer CLI")
    parser.add_argument("--command", choices=["all", "component", "destroy"], required=True)
    parser.add_argument("--component", help="Component name (e.g., image-processor)")
    parser.add_argument("--config", required=True, help="Path to components config file")
    parser.add_argument("--environment", default="dev", help="Deployment environment")

    args = parser.parse_args()

    # Instantiate DeployOrchestrator with Path object
    deployer = DeployOrchestrator(
        config_path=Path(args.config),
        environment=args.environment
    )

    if args.command == "all":
        if not deployer.deploy_all():
            sys.exit(1)

    elif args.command == "component":
        if not args.component:
            logger.error("❌ Component name is required for --command component")
            sys.exit(1)

        if not deployer.deploy_component(args.component):
            sys.exit(1)

    elif args.command == "destroy":
        if not args.component or args.component == "all":
            logger.error("❌ You must specify a specific --component to destroy (e.g., --component image-processor).")
            sys.exit(1)

        if not deployer.destroy_component(args.component):
            sys.exit(1)


if __name__ == "__main__":
    main()
