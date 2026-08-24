#!/usr/bin/env python3
"""
Terraform wrapper with OIDC support
Used by deploy.py for Terraform operations
"""

import os
import json
import subprocess
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


class TerraformWrapper:
    """Terraform operations with OIDC support"""

    def __init__(self, environment: str, tf_dir: Path = None):
        self.environment = environment
        self.tf_dir = tf_dir or Path(__file__).parent.parent / "terraform"
        self.plan_file = self.tf_dir / "plan.tfplan"

        # Setup OIDC
        self._setup_oidc()

    def _setup_oidc(self):
        """Setup OIDC authentication from environment"""
        jwt_token = os.getenv("CI_JOB_JWT_V2")
        role_arn = os.getenv("AWS_ROLE_ARN")

        if jwt_token and role_arn:
            logger.info("Setting up OIDC authentication")
            token_file = Path("/tmp/web_identity_token")
            token_file.write_text(jwt_token)
            token_file.chmod(0o600)

            os.environ["AWS_WEB_IDENTITY_TOKEN_FILE"] = str(token_file)
            os.environ["AWS_ROLE_ARN"] = role_arn
            os.environ["AWS_SESSION_TOKEN"] = ""
            os.environ["AWS_ACCESS_KEY_ID"] = ""
            os.environ["AWS_SECRET_ACCESS_KEY"] = ""

            # Verify auth
            try:
                result = subprocess.run(
                    ["aws", "sts", "get-caller-identity", "--output", "json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                identity = json.loads(result.stdout)
                logger.info(f"✅ Authenticated as: {identity.get('Arn')}")
            except Exception as e:
                logger.error(f"❌ Authentication failed: {e}")

    def _run_command(self, cmd: list) -> bool:
        """Run terraform command"""
        full_cmd = ["terraform"] + cmd
        logger.info(f"Running: {' '.join(full_cmd)}")

        env = os.environ.copy()
        env["TF_IN_AUTOMATION"] = "true"

        try:
            subprocess.run(
                full_cmd,
                cwd=str(self.tf_dir),
                env=env,
                capture_output=False,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Command failed with exit code {e.returncode}")
            return False

    def init(self) -> bool:
        """Initialize Terraform"""
        logger.info(f"🏗️ Initializing Terraform for {self.environment}")
        return self._run_command(["init"])

    def validate(self) -> bool:
        """Validate Terraform configuration"""
        logger.info("🔍 Validating Terraform configuration")
        return self._run_command(["validate"])

    def plan(self) -> bool:
        """Generate Terraform plan"""
        logger.info(f"📋 Planning Terraform changes for {self.environment}")

        cmd = ["plan", "-out", str(self.plan_file)]

        # Add variables from environment
        artifacts_dir = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
        commit_sha = os.getenv("CI_COMMIT_SHORT_SHA", "local")

        # Get component zip files
        for name in ['layer', 'ses', 'image-processor']:
            zip_file = artifacts_dir / f"{name}-{commit_sha}.zip"
            if zip_file.exists():
                var_name = f"{name.replace('-', '_')}_zip"
                cmd.extend(["-var", f"{var_name}={zip_file}"])

        return self._run_command(cmd)

    def apply(self) -> bool:
        """Apply Terraform changes"""
        if not self.plan_file.exists():
            logger.error("❌ Plan file not found. Run plan first.")
            return False

        logger.info(f"🚀 Applying Terraform changes for {self.environment}")

        cmd = ["apply"]
        if self.environment != "prod":
            cmd.append("-auto-approve")
        cmd.append(str(self.plan_file))

        success = self._run_command(cmd)

        if success:
            self.plan_file.unlink(missing_ok=True)

        return success

    def destroy(self) -> bool:
        """Destroy Terraform infrastructure"""
        logger.warning(f"🔥 Destroying Terraform infrastructure for {self.environment}")

        cmd = ["destroy"]
        if self.environment != "prod":
            cmd.append("-auto-approve")

        return self._run_command(cmd)

