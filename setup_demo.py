#!/usr/bin/env python3
"""
🚀 OptiHire Setup Script - Automated Deployment for Presentation
This script handles all setup steps: venv, dependencies, models, data

Usage:
    python setup_demo.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_step(step_num, message):
    """Print a step message"""
    print(f"\n{Colors.CYAN}[Step {step_num}] {message}{Colors.END}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def run_command(cmd, description="Running command"):
    """Run a shell command and return success status"""
    try:
        print_info(f"{description}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            print_error(f"Command failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def main():
    print(f"\n{Colors.CYAN}{'='*60}")
    print("🚀 OptiHire - Automated Setup Script")
    print(f"{'='*60}{Colors.END}\n")

    # Get current directory
    script_dir = Path(__file__).parent.absolute()
    tax_dir = script_dir / "tax"

    # Check if we're in the right directory
    if not (tax_dir / "run.py").exists():
        print_error(f"run.py not found in {tax_dir}")
        print_info("Make sure you're running this script from the project root directory")
        sys.exit(1)

    os.chdir(tax_dir)
    print_info(f"Working directory: {os.getcwd()}")

    # Step 1: Create virtual environment if it doesn't exist
    print_step(1, "Setting up Python virtual environment")
    venv_dir = ".venv"
    if os.path.exists(venv_dir):
        print_warning("Virtual environment already exists")
    else:
        if not run_command(f"python -m venv {venv_dir}", "Creating virtual environment"):
            print_error("Failed to create virtual environment")
            sys.exit(1)
        print_success("Virtual environment created")

    # Determine Python executable in venv
    if sys.platform.startswith('win'):
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        venv_pip = os.path.join(venv_dir, "bin", "pip")

    # Step 2: Upgrade pip
    print_step(2, "Upgrading pip")
    if not run_command(f"{venv_pip} install --upgrade pip", "Upgrading pip"):
        print_warning("Pip upgrade failed, continuing anyway...")

    # Step 3: Install requirements
    print_step(3, "Installing Python dependencies")
    if not run_command(f"{venv_pip} install -r requirements.txt", "Installing dependencies from requirements.txt"):
        print_error("Failed to install dependencies")
        print_warning("Trying alternative PyTorch installation...")
        run_command(f"{venv_pip} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu", "Installing PyTorch (CPU only)")

    # Verify key packages
    packages_to_check = ["flask", "spacy", "sentence-transformers"]
    for package in packages_to_check:
        result = subprocess.run(f"{venv_python} -c 'import {package.replace('-', '_')}'", shell=True, capture_output=True)
        if result.returncode == 0:
            print_success(f"{package} installed correctly")
        else:
            print_warning(f"{package} may not be installed correctly")

    # Step 4: Download spaCy model
    print_step(4, "Downloading spaCy language model")
    if run_command(f"{venv_python} -m spacy download en_core_web_sm", "Downloading en_core_web_sm model"):
        print_success("spaCy model downloaded")
    else:
        print_warning("spaCy model download failed - you can run this manually later")

    # Step 5: Configure .env file
    print_step(5, "Setting up environment configuration")
    env_file = ".env"
    env_example_file = ".env.example"

    if os.path.exists(env_file):
        print_warning(".env file already exists")
    else:
        if os.path.exists(env_example_file):
            shutil.copy(env_example_file, env_file)
            print_success(".env file created from template")

            # Generate SECRET_KEY
            try:
                import secrets
                secret_key = secrets.token_hex(32)
                with open(env_file, 'r') as f:
                    content = f.read()
                content = content.replace("SECRET_KEY=change-me-to-a-long-random-string", f"SECRET_KEY={secret_key}")
                with open(env_file, 'w') as f:
                    f.write(content)
                print_success("SECRET_KEY generated and set")
            except Exception as e:
                print_warning(f"Could not auto-generate SECRET_KEY: {e}")
        else:
            print_error(".env.example not found")

    # Step 6: Create data directories
    print_step(6, "Creating data directories")
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    print_success("Data directories ready")

    # Step 7: Optional - Create demo data
    print_step(7, "Setting up demo data")
    if os.path.exists("create_test_data.py"):
        try:
            response = input("Create demo data? (y/n): ").strip().lower()
            if response == 'y':
                result = subprocess.run(f"{venv_python} create_test_data.py", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print_success("Demo data created")
                else:
                    print_warning(f"Demo data creation output: {result.stdout}")
            else:
                print_info("Skipping demo data creation")
        except Exception as e:
            print_warning(f"Could not create demo data: {e}")
    else:
        print_warning("create_test_data.py not found")

    # Final summary
    print(f"\n{Colors.GREEN}{'='*60}")
    print("✅ Setup Complete!")
    print(f"{'='*60}{Colors.END}")

    print_info("Next steps:")
    print_info(f"1. Edit .env file to add GEMINI_API_KEY (optional)")
    print_info(f"2. Activate virtual environment:")
    if sys.platform.startswith('win'):
        print(f"   {Colors.CYAN}.venv\\Scripts\\activate{Colors.END}")
    else:
        print(f"   {Colors.CYAN}source .venv/bin/activate{Colors.END}")
    print_info(f"3. Start the application:")
    print(f"   {Colors.CYAN}python run.py{Colors.END}")
    print_info(f"4. Open browser to {Colors.CYAN}http://localhost:5000{Colors.END}")

    print_info("\nDemo Credentials:")
    print_info(f"  Recruiter: recruiter@example.com / password123")
    print_info(f"  Candidate: candidate@example.com / password123")

    print(f"\n{Colors.GREEN}🚀 Ready for presentation!{Colors.END}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        sys.exit(1)
