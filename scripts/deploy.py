#!/usr/bin/env python3
"""
Deployment orchestration script
Uses Terraform to deploy Lambda components
"""
import sys
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
        self.terraform_config = self.config.get('deploy/terraform', {})

        # Get terraform path from config
        tf_path = self.terraform_config.get('path', 'deploy/terraform')
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
        """Deploy an entire Terraform module directory for a component"""
        comp = self.components.get(component_name)
        if not comp or 'path' not in comp:
            logger.error(f"Component or path not found: {component_name}")
            return False

        module_dir = Path(__file__).parent.parent / comp['path']
        logger.info(f"📤 Deploying component '{component_name}' at {module_dir}")

        # Initialize Terraform Wrapper scoped to the component's directory
        tf = TerraformWrapper(environment=self.environment, tf_dir=module_dir)

        if not tf.init() or not tf.validate():
            return False

        if not tf.plan() or not tf.apply():
            logger.error(f"❌ Deployment failed for {component_name}")
            return False

        logger.info(f"✅ Component {component_name} deployed successfully")
        return True

    def destroy_component(self, component_name: str) -> bool:
        """Destroy an entire Terraform module directory for a component"""
        comp = self.components.get(component_name)
        if not comp or 'path' not in comp:
            logger.error(f"Component or path not found: {component_name}")
            return False

        module_dir = Path(__file__).parent.parent / comp['path']
        logger.warning(f"⚠️ Destroying component '{component_name}' at {module_dir}")

        tf = TerraformWrapper(environment=self.environment, tf_dir=module_dir)

        if not tf.init():
            return False

        if not tf.destroy():
            logger.error(f"❌ Destruction failed for {component_name}")
            return False

        logger.info(f"✅ Component {component_name} destroyed successfully")
        return True


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
