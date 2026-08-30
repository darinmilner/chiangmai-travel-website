import os
import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class TerraformWrapper:
    """Wrapper around the Terraform CLI"""

    def __init__(
        self,
        environment: str = "dev",
        tf_dir: Optional[Path] = None,
        binary_path: str = "terraform"
    ):
        self.environment = environment
        self.tf_dir = Path(tf_dir).resolve() if tf_dir else Path.cwd().resolve()
        self.binary_path = binary_path if os.path.isabs(binary_path) else "terraform"

    def _run_command(self, args: List[str], env_vars: Optional[Dict[str, str]] = None) -> bool:
        """Executes a terraform CLI command in self.tf_dir"""
        if not self.tf_dir.exists():
            logger.error(f"❌ Directory does not exist: {self.tf_dir}")
            return False

        full_cmd = [self.binary_path] + args
        cmd_env = os.environ.copy()
        cmd_env["TF_VAR_environment"] = self.environment

        if env_vars:
            cmd_env.update(env_vars)

        logger.info(f"Running command in {self.tf_dir}: {' '.join(full_cmd)}")

        result = subprocess.run(
            full_cmd,
            cwd=str(self.tf_dir),
            env=cmd_env,
            check=False
        )
        return result.returncode == 0

    def init(self) -> bool:
        """Runs terraform init"""
        return self._run_command(["init"])

    def validate(self) -> bool:
        """Runs terraform validate"""
        return self._run_command(["validate"])

    def plan(self, out_file: Optional[str] = None) -> bool:
        """Runs terraform plan"""
        args = ["plan"]
        if out_file:
            args.append(f"-out={out_file}")
        return self._run_command(args)

    def apply(self, plan_file: Optional[str] = None) -> bool:
        """Runs terraform apply"""
        args = ["apply", "-auto-approve"]
        if plan_file:
            args.append(plan_file)
        return self._run_command(args)

    def destroy(self) -> bool:
        """Runs terraform destroy"""
        return self._run_command(["destroy", "-auto-approve"])
