#!/usr/bin/env python3
"""
Deployment orchestration script
Uses Terraform to deploy Lambda components
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

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

        # Initialize Terraform
        if not self.terraform.init():
            return False

        # Validate
        if not self.terraform.validate():
            return False

        # Plan
        if not self.terraform.plan():
            return False

        # Apply
        if not self.terraform.apply():
            return False

        logger.info("✅ All infrastructure deployed successfully")
        return True

    def deploy_component(self, component_name: str) -> bool:
        """Deploy a specific component via Terraform"""
        resource = self._get_component_resource(component_name)
        if not resource:
            return False

        logger.info(f"📤 Deploying {component_name} (resource: {resource})")

        # Initialize Terraform
        if not self.terraform.init():
            return False

        # Validate
        if not self.terraform.validate():
            return False

        # Plan with target
        tf_dir = self.tf_dir
        plan_cmd = ['terraform', 'plan', '-target', resource, '-out=plan.tfplan']

        result = subprocess.run(
            plan_cmd,
            cwd=str(tf_dir),
            capture_output=False
        )

        if result.returncode != 0:
            logger.error(f"Plan failed for {component_name}")
            return False

        # Apply with target
        apply_cmd = ['terraform', 'apply', '-target', resource, '-auto-approve', 'plan.tfplan']

        result = subprocess.run(
            apply_cmd,
            cwd=str(tf_dir),
            capture_output=False
        )

        if result.returncode == 0:
            logger.info(f"✅ {component_name} deployed successfully")
            return True
        else:
            logger.error(f"❌ {component_name} deployment failed")
            return False


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Deploy Lambda components via Terraform")
    parser.add_argument('--command', choices=['all', 'component'], required=True)
    parser.add_argument('--component', help='Component to deploy (required if command=component)')
    parser.add_argument('--config', required=True, help='Path to components.yml')
    parser.add_argument('--environment', required=True, help='Environment name')

    args = parser.parse_args()

    orchestrator = DeployOrchestrator(
        config_path=Path(args.config),
        environment=args.environment
    )

    success = False
    if args.command == 'all':
        success = orchestrator.deploy_all()
    elif args.command == 'component':
        if not args.component:
            logger.error("Component name is required for component deployment")
            sys.exit(1)
        success = orchestrator.deploy_component(args.component)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
