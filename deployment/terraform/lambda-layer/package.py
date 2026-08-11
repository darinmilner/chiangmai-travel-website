#!/usr/bin/env python3
"""
Lambda Layer Packaging Script

Usage:
    python package.py [--output-dir DIR] [--clean]

Examples:
    # Basic packaging
    python package.py

    # Custom output directory
    python package.py --output-dir ../terraform/layers

    # Clean before packaging
    python package.py --clean
"""
import argparse
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import zipfile

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_output(output_dir: Path) -> None:
    """Clean the output directory"""
    if output_dir.exists():
        logger.info(f"🧹 Cleaning {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def install_dependencies(layer_dir: Path, temp_dir: Path) -> None:
    """Install Python dependencies to the layer"""
    req_file = layer_dir / "requirements.txt"
    if not req_file.exists():
        logger.info("⚠️  No requirements.txt found")
        return

    logger.info("📦 Installing dependencies...")
    target_dir = temp_dir / "python"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Install only production dependencies (no dev dependencies)
    cmd = [
        sys.executable, "-m", "pip", "install",
        "-r", str(req_file),
        "-t", str(target_dir),
        "--no-cache-dir",
        "--only-binary", ":all:"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {e.stderr}")
        raise


def copy_layer_files(layer_dir: Path, temp_dir: Path) -> None:
    """Copy layer Python files"""
    logger.info("📁 Copying layer files...")
    source_python_dir = layer_dir / "python"
    target_python_dir = temp_dir / "python"

    if not source_python_dir.exists():
        logger.error(f"❌ Python directory not found: {source_python_dir}")
        sys.exit(1)

    # Copy all Python files
    shutil.copytree(source_python_dir, target_python_dir, dirs_exist_ok=True)

    # Remove __pycache__ directories
    for pycache in target_python_dir.rglob("__pycache__"):
        shutil.rmtree(pycache)

    logger.info("✅ Layer files copied")


def create_zip(temp_dir: Path, output_dir: Path, layer_name: str = "villa-shared-layer") -> Path:
    """Create the layer ZIP file"""
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_path = output_dir / f"{layer_name}-{timestamp}.zip"

    logger.info(f"📦 Creating {zip_path}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    logger.info(f"✅ Created {zip_path} ({size_mb:.2f} MB)")
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="Package Lambda layer")
    parser.add_argument("--output-dir", default="dist", help="Output directory")
    parser.add_argument("--clean", action="store_true", help="Clean output directory")
    args = parser.parse_args()

    # Determine paths
    script_dir = Path(__file__).parent
    layer_dir = script_dir / "shared-layer"
    output_dir = Path(args.output_dir)

    # Validate layer exists
    if not layer_dir.exists():
        logger.error(f"❌ Layer directory not found: {layer_dir}")
        sys.exit(1)

    # Clean output if requested
    if args.clean:
        clean_output(output_dir)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Create temporary directory
    temp_dir = script_dir / "temp_layer"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    try:
        # Package the layer
        copy_layer_files(layer_dir, temp_dir)
        install_dependencies(layer_dir, temp_dir)
        create_zip(temp_dir, output_dir)
        logger.info("🎉 Layer packaged successfully!")

    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()