#!/usr/bin/env python3
"""
Installation and Configuration Test Script

This script tests the installation and configuration of the MT5 Profit/Loss Calculator
without connecting to actual MT5 accounts. Use this to verify your setup.
"""

import sys
import os
import logging
from typing import List, Tuple

def test_imports() -> Tuple[bool, List[str]]:
    """
    Test if all required modules can be imported.
    
    Returns:
        tuple: (success, error_messages)
    """
    errors = []
    
    # Test standard library imports
    try:
        import time
        import datetime
        import json
        import argparse
        import configparser
        import math
        import typing
        print("✓ Standard library modules imported successfully")
    except ImportError as e:
        errors.append(f"Standard library import error: {e}")
    
    # Test MetaTrader5 import
    try:
        import MetaTrader5 as mt5
        print(f"✓ MetaTrader5 module imported successfully")
        if hasattr(mt5, '__version__'):
            print(f"  Version: {mt5.__version__}")
    except ImportError as e:
        errors.append(f"MetaTrader5 import error: {e}")
        print("✗ MetaTrader5 module not found")
        print("  Install with: pip install MetaTrader5")
    
    # Test our custom modules
    custom_modules = [
        'config',
        'mt5_connection',
        'mt5_position_manager',
        'account_processor'
    ]
    
    for module_name in custom_modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name} module imported successfully")
        except ImportError as e:
            errors.append(f"{module_name} import error: {e}")
            print(f"✗ {module_name} module import failed: {e}")
    
    return len(errors) == 0, errors

def test_configuration() -> Tuple[bool, List[str]]:
    """
    Test the configuration file.
    
    Returns:
        tuple: (success, error_messages)
    """
    errors = []
    
    try:
        from config import (
            ACCOUNTS,
            DOLLAR_PER_LOT_PER_PRICE_UNIT,
            ACCOUNT_PROCESSING_DELAY,
            ENABLE_ACCOUNT_PROCESSING_DELAY,
            LOG_LEVEL,
            validate_configuration
        )
        
        print("✓ Configuration file loaded successfully")
        
        # Test account configuration
        if not ACCOUNTS:
            errors.append("No accounts configured in ACCOUNTS list")
            print("✗ No accounts configured")
        else:
            print(f"✓ {len(ACCOUNTS)} accounts configured")
            
            # Validate each account
            for i, account in enumerate(ACCOUNTS, 1):
                account_login = account.get('MT5_ACCOUNT', f'Account_{i}')
                required_fields = ['MT5_ACCOUNT', 'MT5_PASSWORD', 'MT5_SERVER', 'MT5_TERMINAL_PATH']
                missing_fields = [field for field in required_fields if not account.get(field)]
                
                if missing_fields:
                    errors.append(f"Account '{account_login}' missing fields: {missing_fields}")
                    print(f"✗ Account '{account_login}' missing: {', '.join(missing_fields)}")
                else:
                    print(f"✓ Account '{account_login}' configuration valid")
        
        # Test symbol configuration
        if not DOLLAR_PER_LOT_PER_PRICE_UNIT:
            errors.append("DOLLAR_PER_LOT_PER_PRICE_UNIT is empty")
            print("✗ No symbol configurations found")
        else:
            print(f"✓ {len(DOLLAR_PER_LOT_PER_PRICE_UNIT)} symbols configured")
        
        # Test processing configuration
        if ENABLE_ACCOUNT_PROCESSING_DELAY:
            if ACCOUNT_PROCESSING_DELAY <= 0:
                errors.append("ACCOUNT_PROCESSING_DELAY must be positive when enabled")
                print(f"✗ Invalid processing delay: {ACCOUNT_PROCESSING_DELAY}")
            else:
                print(f"✓ Processing delay: {ACCOUNT_PROCESSING_DELAY} seconds")
        else:
            print("✓ Processing delay disabled")
        
        # Run built-in validation
        config_valid, config_errors = validate_configuration()
        if not config_valid:
            errors.extend(config_errors)
            print("✗ Configuration validation failed:")
            for error in config_errors:
                print(f"  - {error}")
        else:
            print("✓ Configuration validation passed")
        
    except Exception as e:
        errors.append(f"Configuration test error: {e}")
        print(f"✗ Configuration test failed: {e}")
    
    return len(errors) == 0, errors

def test_file_structure() -> Tuple[bool, List[str]]:
    """
    Test if all required files exist.
    
    Returns:
        tuple: (success, error_messages)
    """
    errors = []
    
    required_files = [
        'config.py',
        'mt5_connection.py',
        'mt5_position_manager.py',
        'account_processor.py',
        'profit_loss_calculator.py',
        'requirements.txt',
        'README.md'
    ]
    
    print("Checking file structure...")
    
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename} exists")
        else:
            errors.append(f"Missing file: {filename}")
            print(f"✗ {filename} missing")
    
    return len(errors) == 0, errors

def test_logging_setup() -> Tuple[bool, List[str]]:
    """
    Test logging configuration.
    
    Returns:
        tuple: (success, error_messages)
    """
    errors = []
    
    try:
        from profit_loss_calculator import setup_logging
        
        # Test logging setup
        setup_logging(logging.INFO, None)
        print("✓ Logging setup successful")
        
        # Test log message
        logging.info("Test log message")
        print("✓ Log message test successful")
        
    except Exception as e:
        errors.append(f"Logging test error: {e}")
        print(f"✗ Logging test failed: {e}")
    
    return len(errors) == 0, errors

def test_main_script() -> Tuple[bool, List[str]]:
    """
    Test the main script can be imported and basic functions work.
    
    Returns:
        tuple: (success, error_messages)
    """
    errors = []
    
    try:
        from profit_loss_calculator import (
            create_argument_parser,
            validate_environment,
            print_startup_info
        )
        
        # Test argument parser
        parser = create_argument_parser()
        print("✓ Argument parser created successfully")
        
        # Test environment validation (without MT5 connection)
        print("✓ Main script functions accessible")
        
    except Exception as e:
        errors.append(f"Main script test error: {e}")
        print(f"✗ Main script test failed: {e}")
    
    return len(errors) == 0, errors

def run_all_tests() -> bool:
    """
    Run all tests and return overall success status.
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print("=" * 80)
    print("MT5 PROFIT/LOSS CALCULATOR - INSTALLATION TEST")
    print("=" * 80)
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 80)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Logging Setup", test_logging_setup),
        ("Main Script", test_main_script)
    ]
    
    all_passed = True
    all_errors = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 40)
        
        try:
            success, errors = test_func()
            if success:
                print(f"✓ {test_name} test PASSED")
            else:
                print(f"✗ {test_name} test FAILED")
                all_passed = False
                all_errors.extend(errors)
        except Exception as e:
            print(f"✗ {test_name} test ERROR: {e}")
            all_passed = False
            all_errors.append(f"{test_name} test exception: {e}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("\nYour installation appears to be working correctly!")
        print("You can now run the profit/loss calculator with:")
        print("  python profit_loss_calculator.py --validate-only")
        print("  python profit_loss_calculator.py")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nErrors found:")
        for error in all_errors:
            print(f"  - {error}")
        print("\nPlease fix these issues before running the calculator.")
    
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)