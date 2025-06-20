#!/usr/bin/env python3
"""
Setup Script for MT5 Profit/Loss Calculator

This script helps new users set up the calculator by:
1. Copying the example configuration
2. Checking dependencies
3. Creating necessary directories
4. Providing setup guidance
"""

import os
import sys
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import MetaTrader5
        print("✅ MetaTrader5 package is installed")
        return True
    except ImportError:
        print("❌ MetaTrader5 package not found")
        print("   Install with: pip install MetaTrader5")
        return False

def setup_configuration():
    """Set up the configuration file from example."""
    config_example = Path("config_example.py")
    config_file = Path("config.py")
    
    if not config_example.exists():
        print("❌ config_example.py not found")
        return False
    
    if config_file.exists():
        response = input("⚠️  config.py already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("✅ Keeping existing config.py")
            return True
    
    try:
        shutil.copy2(config_example, config_file)
        print("✅ Created config.py from example")
        print("   📝 Edit config.py with your MT5 account details")
        return True
    except Exception as e:
        print(f"❌ Failed to create config.py: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ["output", "logs"]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}/")
            except Exception as e:
                print(f"❌ Failed to create directory {directory}: {e}")
                return False
        else:
            print(f"✅ Directory exists: {directory}/")
    
    return True

def check_mt5_terminal():
    """Check if MT5 terminal is installed in common locations."""
    common_paths = [
        r"C:\Program Files\MetaTrader 5\terminal64.exe",
        r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
        r"C:\Program Files\Tickmill MT5 Terminal\terminal64.exe",
        r"C:\Program Files (x86)\Tickmill MT5 Terminal\terminal64.exe"
    ]
    
    found_paths = []
    for path in common_paths:
        if Path(path).exists():
            found_paths.append(path)
    
    if found_paths:
        print("✅ Found MT5 terminal installations:")
        for path in found_paths:
            print(f"   📁 {path}")
        return True
    else:
        print("⚠️  No MT5 terminal found in common locations")
        print("   Make sure MetaTrader 5 is installed")
        print("   Update MT5_TERMINAL_PATH in config.py with correct path")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("SETUP COMPLETE - NEXT STEPS")
    print("="*60)
    print("\n1. 📝 EDIT CONFIG.PY (REQUIRED):")
    print("   - Open config.py in a text editor")
    print("   - Replace placeholder values with your actual MT5 account details:")
    print("     • MT5_ACCOUNT: Your login number")
    print("     • MT5_PASSWORD: Your account password")
    print("     • MT5_SERVER: Your broker's server name")
    print("     • MT5_TERMINAL_PATH: Path to your MT5 terminal")
    print("\n2. 🧪 TEST YOUR SETUP:")
    print("   python test_installation.py")
    print("\n3. ✅ VALIDATE CONFIGURATION:")
    print("   python profit_loss_calculator.py --validate-only")
    print("\n4. 🚀 RUN THE CALCULATOR:")
    print("   python profit_loss_calculator.py")
    print("\n5. 🔒 SECURITY REMINDER:")
    print("   - NEVER commit config.py to version control")
    print("   - Keep your configuration file secure")
    print("   - The .gitignore file will help protect sensitive files")
    print("\n" + "="*60)

def main():
    """Main setup function."""
    print("="*60)
    print("MT5 PROFIT/LOSS CALCULATOR SETUP")
    print("="*60)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Check dependencies
    if not check_dependencies():
        success = False
    
    # Create directories
    if not create_directories():
        success = False
    
    # Setup configuration
    if not setup_configuration():
        success = False
    
    # Check MT5 terminal
    check_mt5_terminal()  # This is informational, not critical
    
    if success:
        print_next_steps()
        return True
    else:
        print("\n❌ Setup encountered errors. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)