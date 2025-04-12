#!/usr/bin/env python
"""
Build script for image-to-excel package.

This script:
1. Builds an executable using PyInstaller
2. Creates a deployment package (zip) containing:
   - The executable
   - Configuration directory with default settings
3. Optionally performs automated builds on a schedule

Usage:
  python build_package.py [--schedule HOURS]

Options:
  --schedule HOURS  Optional hours between automated builds (e.g., 24 for daily)
"""

import os
import sys
import shutil
import subprocess
import argparse
import time
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('build_log.txt')
    ]
)
logger = logging.getLogger(__name__)

# Project directories
PROJECT_ROOT = Path(__file__).parent.absolute()
DIST_DIR = PROJECT_ROOT / 'dist'
BUILD_DIR = PROJECT_ROOT / 'build'
CONF_DIR = PROJECT_ROOT / 'conf'
OUTPUT_DIR = PROJECT_ROOT / 'package'

# Application name and main script
APP_NAME = 'image_to_excel'
MAIN_SCRIPT = 'src/main.py'
VERSION = '1.0.0'  # Update as needed


def clean_build_directories():
    """Clean build and dist directories before building."""
    logger.info("Cleaning build directories")
    
    # Remove previous build artifacts
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)


def build_executable():
    """Build the executable using PyInstaller."""
    logger.info("Building executable with PyInstaller")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name', APP_NAME,
        '--onefile',  # Create a single executable file
        '--clean',    # Clean PyInstaller cache
        '--log-level', 'INFO',
        # Add any needed hidden imports
        '--hidden-import', 'pandas',
        '--hidden-import', 'openai',
        '--hidden-import', 'PyPDF2',
        '--hidden-import', 'easyocr',
        '--hidden-import', 'fitz',  # PyMuPDF
        # Add data files (including config)
        '--add-data', f'{CONF_DIR}:conf',
        # Main script
        MAIN_SCRIPT
    ]
    
    # Run PyInstaller
    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Successfully built executable: {DIST_DIR/APP_NAME}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build executable: {e}")
        return False


def create_config_template():
    """Create a default configuration file template."""
    logger.info("Creating default configuration")
    
    # Create conf directory in the package
    package_conf_dir = OUTPUT_DIR / 'conf'
    package_conf_dir.mkdir(exist_ok=True)
    
    # Copy the example config file as the default template
    example_config = CONF_DIR / 'api_config.yaml.example'
    if example_config.exists():
        target_config = package_conf_dir / 'api_config.yaml.example'
        shutil.copy(example_config, target_config)
        
        # Also create an empty api_config.yaml file that users can fill in
        with open(package_conf_dir / 'api_config.yaml', 'w') as f:
            f.write("""# Configure your API keys and settings here
# See api_config.yaml.example for all available options

openai:
  api_key: ""  # Add your OpenAI API key here

output:
  excel:
    default_filename: "output.xlsx"
""")
        
        logger.info(f"Created configuration template at {package_conf_dir}")
    else:
        logger.error(f"Config example file not found: {example_config}")


def create_package():
    """Create a packaged zip file with executable and configuration."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    package_name = f"{APP_NAME}_v{VERSION}_{timestamp}"
    package_dir = OUTPUT_DIR / package_name
    
    logger.info(f"Creating package: {package_name}")
    
    # Create package directory
    package_dir.mkdir(exist_ok=True)
    
    # Copy executable
    executable = DIST_DIR / APP_NAME
    if sys.platform.startswith('win'):
        executable = Path(f"{executable}.exe")
    
    if executable.exists():
        shutil.copy(executable, package_dir)
    else:
        logger.error(f"Executable not found: {executable}")
        return False
    
    # Create configuration directory and default files
    package_conf_dir = package_dir / 'conf'
    package_conf_dir.mkdir(exist_ok=True)
    
    # Copy configuration files
    for config_file in CONF_DIR.glob('*'):
        if config_file.is_file():
            shutil.copy(config_file, package_conf_dir)
    
    # Create README file
    with open(package_dir / 'README.txt', 'w') as f:
        f.write(f"""Image to Excel Invoice Parser v{VERSION}
=================================

This application extracts invoice data and exports it to Excel.

Getting Started:
1. Configure your API keys in conf/api_config.yaml
2. Run the application with: 
   {APP_NAME} <input_directory> <output_excel_file>

For example:
   {APP_NAME} ./invoices ./output.xlsx
   
Requirements:
- OpenAI API key for processing invoices

For more information, please refer to the documentation.
""")
    
    # Create zip file
    zip_file = f"{package_dir}.zip"
    shutil.make_archive(str(package_dir), 'zip', package_dir)
    
    logger.info(f"Package created: {zip_file}")
    return True


def perform_build():
    """Perform the complete build process."""
    logger.info("Starting build process")
    
    # Clean directories
    clean_build_directories()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create config template
    create_config_template()
    
    # Create package
    create_package()
    
    logger.info("Build process completed successfully")
    return True


def scheduled_build(hours):
    """Run builds on a schedule."""
    seconds = int(hours * 3600)
    logger.info(f"Starting scheduled builds every {hours} hours ({seconds} seconds)")
    
    while True:
        try:
            perform_build()
            logger.info(f"Next build scheduled in {hours} hours")
            time.sleep(seconds)
        except KeyboardInterrupt:
            logger.info("Scheduled builds stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in scheduled build: {e}")
            # Still continue with the schedule
            time.sleep(seconds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build the image-to-excel package')
    parser.add_argument('--schedule', type=float, help='Hours between automated builds')
    
    args = parser.parse_args()
    
    if args.schedule:
        scheduled_build(args.schedule)
    else:
        perform_build()
