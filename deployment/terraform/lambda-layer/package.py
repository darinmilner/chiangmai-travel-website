#!/usr/bin/env python3
"""
Lambda Layer Packaging Script

This script packages the shared Lambda layer for deployment.
Can be run locally or in CI/CD pipelines.

Usage:
    python package.py [--output-dir DIR] [--layer-name NAME] [--clean]

Examples:
    # Basic packaging
    python package.py

    # Custom output directory
    python package.py --output-dir dist

    # Clean before packaging
    python package.py --clean

    # Dry run (show what would be done)
    python package.py --dry-run
"""
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LayerPackager:
    """Handles packaging of Lambda layers"""

    def __init__(
        self,
        layer_name: str = "villa-shared-layer",
        version: str = None,
        output_dir: str = "dist",
        clean: bool = False,
        dry_run: bool = False,
        include_tests: bool = False,
        include_examples: bool = False
    ):
        self.layer_name = layer_name
        self.version = version or datetime.now().strftime("%Y%m%d%H%M%S")
        self.output_dir = Path(output_dir)
        self.clean = clean
        self.dry_run = dry_run
        self.include_tests = include_tests
        self.include_examples = include_examples

        # Determine project root
        self.project_root = Path(__file__).parent
        self.layer_dir = self.project_root / "shared-layer"
        self.python_dir = self.layer_dir / "python"
        self.tests_dir = self.layer_dir / "tests"

        # Validate structure
        self._validate_structure()

    def _validate_structure(self) -> None:
        """Validate the layer directory structure"""
        if not self.layer_dir.exists():
            raise FileNotFoundError(f"Layer directory not found: {self.layer_dir}")

        if not self.python_dir.exists():
            raise FileNotFoundError(f"Python directory not found: {self.python_dir}")

        logger.info(f"✅ Found layer directory: {self.layer_dir}")
        logger.info(f"✅ Found Python directory: {self.python_dir}")

    def _get_files_to_include(self) -> List[Path]:
        """Get all files to include in the layer"""
        files = []

        # Include all Python files
        for path in self.python_dir.rglob("*.py"):
            if "__pycache__" not in str(path):
                files.append(path)

        # Include requirements.txt if exists
        req_file = self.layer_dir / "requirements.txt"
        if req_file.exists():
            files.append(req_file)

        # Optionally include tests
        if self.include_tests and self.tests_dir.exists():
            for path in self.tests_dir.rglob("*.py"):
                if "__pycache__" not in str(path):
                    files.append(path)

        return files

    def _get_file_info(self, file_path: Path) -> Dict:
        """Get file information for manifest"""
        rel_path = file_path.relative_to(self.layer_dir)
        stat = file_path.stat()

        return {
            "path": str(rel_path),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "hash": self._calculate_hash(file_path)
        }

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]

    def _install_dependencies(self, temp_dir: Path) -> None:
        """Install Python dependencies"""
        req_file = self.layer_dir / "requirements.txt"
        if not req_file.exists():
            logger.info("⚠️  No requirements.txt found, skipping dependency installation")
            return

        logger.info("📦 Installing dependencies...")
        target_dir = temp_dir / "python"
        target_dir.mkdir(parents=True, exist_ok=True)

        # Install dependencies
        cmd = [
            sys.executable,
            "-m", "pip",
            "install",
            "-r", str(req_file),
            "-t", str(target_dir),
            "--no-cache-dir",
            "--upgrade",
            "--no-deps",  # Don't install dependencies of dependencies
            "--only-binary", ":all:",  # Only use wheels
            "--no-warn-script-location"
        ]

        if self.dry_run:
            logger.info(f"🔍 DRY RUN: Would run: {' '.join(cmd)}")
            return

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"✅ Dependencies installed successfully")
            if result.stdout:
                logger.debug(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e.stderr}")
            raise

    def _copy_layer_files(self, temp_dir: Path) -> None:
        """Copy layer files to temporary directory"""
        logger.info("📁 Copying layer files...")
        target_dir = temp_dir / "python"

        # Copy Python files
        for src_path in self.python_dir.rglob("*.py"):
            if "__pycache__" in str(src_path):
                continue

            rel_path = src_path.relative_to(self.python_dir)
            dst_path = target_dir / rel_path
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            if not self.dry_run:
                shutil.copy2(src_path, dst_path)

        # Copy __init__.py files
        for src_path in self.python_dir.rglob("__init__.py"):
            rel_path = src_path.relative_to(self.python_dir)
            dst_path = target_dir / rel_path
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            if not self.dry_run:
                shutil.copy2(src_path, dst_path)

        # Copy tests if requested
        if self.include_tests and self.tests_dir.exists():
            logger.info("📋 Including tests in layer...")
            tests_target = temp_dir / "tests"
            if not self.dry_run:
                shutil.copytree(self.tests_dir, tests_target, dirs_exist_ok=True)

        logger.info(f"✅ Layer files copied to: {target_dir}")

    def _create_manifest(self, temp_dir: Path) -> None:
        """Create a manifest file for the layer"""
        files = []
        for path in temp_dir.rglob("*"):
            if path.is_file():
                rel_path = path.relative_to(temp_dir)
                stat = path.stat()
                files.append({
                    "path": str(rel_path),
                    "size": stat.st_size,
                    "hash": self._calculate_hash(path)
                })

        manifest = {
            "layer_name": self.layer_name,
            "version": self.version,
            "created": datetime.now().isoformat(),
            "python_version": sys.version.split()[0],
            "file_count": len(files),
            "total_size": sum(f["size"] for f in files),
            "files": files
        }

        manifest_path = temp_dir / "manifest.json"
        if not self.dry_run:
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

        logger.info(f"📄 Manifest created with {len(files)} files")

    def _create_layer_zip(self, temp_dir: Path) -> Path:
        """Create the layer ZIP file"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        zip_filename = self.output_dir / f"{self.layer_name}-{self.version}.zip"

        if self.dry_run:
            logger.info(f"🔍 DRY RUN: Would create: {zip_filename}")
            return zip_filename

        logger.info(f"📦 Creating layer ZIP: {zip_filename}")

        # Create ZIP
        import zipfile
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)

        # Get file size
        size_mb = zip_filename.stat().st_size / (1024 * 1024)
        logger.info(f"✅ Layer ZIP created: {zip_filename} ({size_mb:.2f} MB)")

        return zip_filename

    def _clean_output(self) -> None:
        """Clean the output directory"""
        if self.output_dir.exists():
            logger.info(f"🧹 Cleaning output directory: {self.output_dir}")
            if not self.dry_run:
                shutil.rmtree(self.output_dir)
                self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_dockerfile(self) -> str:
        """Generate a Dockerfile for packaging in CI/CD"""
        return '''FROM public.ecr.aws/lambda/python:3.11

# Install build dependencies
RUN yum install -y gcc g++ make && yum clean all

# Copy layer code
COPY . /layer

# Install dependencies
WORKDIR /layer
RUN pip install -r requirements.txt -t /python

# Cleanup
RUN rm -rf /layer

# The layer will be at /python
CMD ["/bin/bash"]
'''

    def _generate_ci_script(self) -> str:
        """Generate a CI/CD script"""
        return '''#!/bin/bash
# CI/CD script for packaging Lambda layer

set -e

echo "🚀 Building Lambda Layer..."

# Install dependencies
pip install -r shared-layer/requirements.txt -t shared-layer/python

# Package layer
python package_layer.py --output-dir dist --clean

# Upload to AWS
aws lambda publish-layer-version \\
    --layer-name villa-shared-layer \\
    --description "Shared utilities for Villa Lambdas" \\
    --zip-file fileb://dist/villa-shared-layer-$(date +%Y%m%d).zip \\
    --compatible-runtimes python3.11 python3.12 \\
    --license-info "MIT"

echo "✅ Layer published successfully!"
'''

    def _generate_github_actions(self) -> str:
        """Generate a GitHub Actions workflow"""
        return '''name: Package Lambda Layer

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'shared-layer/**'
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  package:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r shared-layer/requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest shared-layer/tests/ -v --cov=shared-layer/python

    - name: Package layer
      run: |
        python package_layer.py --output-dir dist --clean

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: lambda-layer
        path: dist/

    - name: Publish to AWS (main branch only)
      if: github.ref == 'refs/heads/main'
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        AWS_REGION: ${{ secrets.AWS_REGION }}
      run: |
        LAYER_ZIP=$(ls dist/*.zip)
        aws lambda publish-layer-version \\
          --layer-name villa-shared-layer \\
          --description "Shared utilities for Villa Lambdas" \\
          --zip-file fileb://$LAYER_ZIP \\
          --compatible-runtimes python3.11 python3.12
'''

    def _generate_readme(self) -> str:
        """Generate README for the layer"""
        return f'''# {self.layer_name}

## Overview
Shared Lambda layer for Villa application Lambdas.

## Version: {self.version}

## Contents
- Shared configuration
- Structured logging
- AWS clients (S3, SES)
- Common utilities

## Structure