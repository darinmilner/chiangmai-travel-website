import os
import subprocess
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

class TerraformWrapper:
    def __init__(self, working_dir: Path, binary_path: str = "terraform"):
        self.working_dir = Path(working_dir).resolve()
        # Use system binary "terraform" unless a specific existing path is passed
        self.binary_path = binary_path if os.path.isabs(binary_path) else "terraform"

    def _run_command(self, args: List[str], env_vars: Optional[dict] = None) -> bool:
        if not self.working_dir.exists():
            logger.error(f"❌ Terraform directory does not exist: {self.working_dir}")
            return False

        full_cmd = [self.binary_path] + args
        cmd_env = os.environ.copy()
        if env_vars:
            cmd_env.update(env_vars)

        logger.info(f"Running command in {self.working_dir}: {' '.join(full_cmd)}")

        result = subprocess.run(
            full_cmd,
            cwd=str(self.working_dir),
            env=cmd_env,
            check=True
        )
        return result.returncode == 0

    def init(self) -> bool:
        return self._run_command(["init"])

    def validate(self) -> bool:
        return self._run_command(["validate"])

    def plan(self, out_file: Optional[str] = None) -> bool:
        args = ["plan"]
        if out_file:
            args.append(f"-out={out_file}")
        return self._run_command(args)

    def apply(self, plan_file: Optional[str] = None) -> bool:
        args = ["apply", "-auto-approve"]
        if plan_file:
            args.append(plan_file)
        return self._run_command(args)