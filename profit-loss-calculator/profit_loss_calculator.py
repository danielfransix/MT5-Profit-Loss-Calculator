#!/usr/bin/env python3
"""
Standalone MT5 Profit/Loss Calculator

A pure reporting tool that calculates profit/loss for multiple MT5 accounts
without any trading functionality. Processes accounts sequentially with
configurable delays and provides comprehensive reporting.

This script maintains the same function names and structure as the original
system for consistency and compatibility.
"""

import sys
import os
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# Import our modules
from config import (
    ACCOUNTS,
    LOG_LEVEL,
    LOG_FILE,
    ENABLE_CONSOLE_OUTPUT,
    ENABLE_JSON_OUTPUT,
    validate_configuration
)
from account_processor import process_accounts, print_summary_to_console

def setup_logging(log_level: int = None, log_file: str = None) -> None:
    """
    Set up logging configuration.
    This function maintains the same signature as the original system.
    
    Args:
        log_level (int, optional): Logging level (defaults to config value)
        log_file (str, optional): Log file path (defaults to config value)
    """
    # Use config defaults if not provided
    if log_level is None:
        log_level = LOG_LEVEL
    if log_file is None:
        log_file = LOG_FILE
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8') if log_file else logging.NullHandler(),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized - Level: {logging.getLevelName(log_level)}")
    if log_file:
        logging.info(f"Log file: {log_file}")

def validate_environment() -> bool:
    """
    Validate the environment and configuration.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    try:
        # Validate configuration
        config_valid, config_errors = validate_configuration()
        if not config_valid:
            logging.error("Configuration validation failed:")
            for error in config_errors:
                logging.error(f"  - {error}")
            return False
        
        # Check if MetaTrader5 is available
        try:
            import MetaTrader5 as mt5
            logging.info(f"MetaTrader5 module version: {mt5.__version__ if hasattr(mt5, '__version__') else 'Unknown'}")
        except ImportError as e:
            logging.error(f"MetaTrader5 module not available: {e}")
            return False
        
        # Check if accounts are configured
        if not ACCOUNTS:
            logging.error("No accounts configured in config.py")
            return False
        
        logging.info(f"Environment validation passed - {len(ACCOUNTS)} accounts configured")
        return True
        
    except Exception as e:
        logging.error(f"Environment validation error: {e}")
        return False

def print_startup_info() -> None:
    """
    Print startup information and configuration summary.
    """
    logging.info("=" * 80)
    logging.info("MT5 STANDALONE PROFIT/LOSS CALCULATOR")
    logging.info("=" * 80)
    logging.info(f"Version: 1.0.0")
    logging.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Python version: {sys.version.split()[0]}")
    logging.info(f"Platform: {sys.platform}")
    
    # Configuration summary
    logging.info("\nConfiguration Summary:")
    logging.info(f"  Accounts configured: {len(ACCOUNTS)}")
    logging.info(f"  Console output: {ENABLE_CONSOLE_OUTPUT}")
    logging.info(f"  JSON output: {ENABLE_JSON_OUTPUT}")
    
    # Account list
    logging.info("\nConfigured Accounts:")
    for i, account in enumerate(ACCOUNTS, 1):
        account_login = account.get('MT5_ACCOUNT', 'N/A')
        account_server = account.get('MT5_SERVER', 'Unknown')
        logging.info(f"  {i}. Account {account_login} ({account_server})")
    
    logging.info("=" * 80)

def main(args: Optional[argparse.Namespace] = None) -> int:
    """
    Main function for the profit/loss calculator.
    This function maintains the same signature as the original system.
    
    Args:
        args (argparse.Namespace, optional): Command line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        # Parse command line arguments if not provided
        if args is None:
            parser = create_argument_parser()
            args = parser.parse_args()
        
        # Setup logging
        log_level = getattr(logging, args.log_level.upper()) if hasattr(args, 'log_level') else LOG_LEVEL
        log_file = getattr(args, 'log_file', None) or LOG_FILE
        setup_logging(log_level, log_file)
        
        # Print startup information
        print_startup_info()
        
        # Validate environment
        if not validate_environment():
            logging.error("Environment validation failed. Exiting.")
            return 1
        
        # Process accounts (filtered if --account specified)
        account_filter = getattr(args, 'account', None)
        if account_filter:
            logging.info(f"Starting profit/loss processing for account: {account_filter}")
        else:
            logging.info("Starting multi-account profit/loss processing...")
        summary = process_accounts(account_filter)
        
        # Print summary to console if enabled
        if ENABLE_CONSOLE_OUTPUT:
            print_summary_to_console(summary)
        
        # Check if any accounts were processed successfully
        successful_accounts = summary['processing_info']['accounts_processed_successfully']
        failed_accounts = summary['processing_info']['accounts_failed']
        
        if successful_accounts == 0:
            logging.error("No accounts were processed successfully")
            return 1
        elif failed_accounts > 0:
            logging.warning(f"Processing completed with {failed_accounts} failed accounts")
            return 2  # Partial success
        else:
            logging.info("All accounts processed successfully")
            return 0
        
    except KeyboardInterrupt:
        logging.info("Processing interrupted by user")
        return 130  # Standard exit code for Ctrl+C
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}", exc_info=True)
        return 1

def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Standalone MT5 Profit/Loss Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with default settings
  %(prog)s --log-level DEBUG        # Run with debug logging
  %(prog)s --log-file custom.log    # Use custom log file
  %(prog)s --no-console             # Disable console output
  %(prog)s --json-only              # Output only JSON, no console

This tool is a pure reporting utility and does not perform any trading operations.
It processes multiple MT5 accounts sequentially with configurable delays.
        """
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file (default: from config.py)'
    )
    
    # Output options
    parser.add_argument(
        '--no-console',
        action='store_true',
        help='Disable console output (only log to file)'
    )
    
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='Output only JSON file, disable console summary'
    )
    
    # Account selection
    parser.add_argument(
        '--account',
        type=str,
        help='Process only the specified account login number (default: all accounts)'
    )
    
    # Validation mode
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate configuration and environment, do not process accounts'
    )
    
    # Version
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser

def run_validation_only() -> int:
    """
    Run only configuration and environment validation.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    print("Running validation mode...")
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Validate environment
    if validate_environment():
        print("✓ All validations passed")
        return 0
    else:
        print("✗ Validation failed")
        return 1

if __name__ == "__main__":
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Handle special modes
    if args.validate_only:
        sys.exit(run_validation_only())
    
    # Override config settings with command line arguments
    if args.no_console:
        import config
        config.ENABLE_CONSOLE_OUTPUT = False
    
    if args.json_only:
        import config
        config.ENABLE_CONSOLE_OUTPUT = False
        config.ENABLE_JSON_OUTPUT = True
    
    # Run main function
    exit_code = main(args)
    sys.exit(exit_code)