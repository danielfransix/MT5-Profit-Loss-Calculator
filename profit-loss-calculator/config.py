#!/usr/bin/env python3
"""
MT5 Profit/Loss Calculator - Configuration

This configuration file supports multiple MT5 accounts and uses the same
variable names as the original system for consistency.
"""

# =============================================================================
# MULTI-ACCOUNT CONFIGURATION
# =============================================================================

# List of MT5 accounts to process sequentially
# Each account should have the required connection details
ACCOUNTS = [
    {
        "MT5_ACCOUNT": 12345678,                           # Your MT5 login number (integer)
        "MT5_PASSWORD": "your_mt5_password",               # Your MT5 account password (string)
        "MT5_SERVER": "YourBroker-Demo",                  # Your broker's server name (string)
        "MT5_TERMINAL_PATH": r"C:\Program Files\MetaTrader 5\terminal64.exe"  # Path to MT5 terminal
    }
    # Add more accounts as needed:
    # {
    #     "MT5_ACCOUNT": 87654321,
    #     "MT5_PASSWORD": "your_password2",
    #     "MT5_SERVER": "YourBroker-Live",
    #     "MT5_TERMINAL_PATH": r"C:\Program Files\MetaTrader 5\terminal64.exe"
    # }
]

# =============================================================================
# PROCESSING SETTINGS
# =============================================================================

# Enable delay between processing accounts
ENABLE_ACCOUNT_PROCESSING_DELAY = True

# Delay between processing accounts (in seconds)
# This prevents overwhelming MT5 terminals and allows proper connection cleanup
ACCOUNT_PROCESSING_DELAY = 5.0

# Error handling settings
CONTINUE_ON_ACCOUNT_FAILURE = True
MAX_ACCOUNT_FAILURES = 3

# Connection settings
MT5_CONNECTION_TIMEOUT = 60000  # Connection timeout in milliseconds
MT5_CONNECTION_RETRIES = 3      # Number of connection retry attempts
MT5_RETRY_DELAY = 1.0          # Delay between retries in seconds
MAX_CONNECTION_ATTEMPTS = 3     # Maximum connection attempts per account

# Cache settings
POSITION_CACHE_DURATION = 30   # Position cache duration in seconds
ORDER_CACHE_DURATION = 30      # Order cache duration in seconds

# =============================================================================
# SYMBOL CONFIGURATION (DOLLAR_PER_LOT_PER_PRICE_UNIT)
# =============================================================================
# This is the same variable name as the original system
# These values determine how price movements translate to dollar P&L
# Format: 'SYMBOL': dollar_value_per_lot_per_price_unit

DOLLAR_PER_LOT_PER_PRICE_UNIT = {
    # AUD pairs
    "AUDCAD": 74000.0,   # Australian Dollar / Canadian Dollar
    "AUDCHF": 122000.0,   # Australian Dollar / Swiss Franc
    "AUDJPY": 700.0,    # Australian Dollar / Japanese Yen
    "AUDNZD": 65000.0,   # Australian Dollar / New Zealand Dollar
    "AUDUSD": 100000.0,   # Australian Dollar / US Dollar
    
    # CAD pairs
    "CADCHF": 122000.0,   # Canadian Dollar / Swiss Franc
    "CADJPY": 700.0,    # Canadian Dollar / Japanese Yen
    
    # CHF pairs
    "CHFJPY": 700.0,      # Swiss Franc / Japanese Yen
    
    # EUR pairs
    "EURAUD": 66000.0,   # Euro / Australian Dollar
    "EURCAD": 74000.0,   # Euro / Canadian Dollar
    "EURCHF": 122000.0,   # Euro / Swiss Franc
    "EURGBP": 134000.0,   # Euro / British Pound
    "EURJPY": 700.0,    # Euro / Japanese Yen
    "EURNZD": 60000.0,   # Euro / New Zealand Dollar
    "EURUSD": 100000.0,   # Euro / US Dollar
    
    # GBP pairs
    "GBPAUD": 66000.0,   # British Pound / Australian Dollar
    "GBPCHF": 122000.0,   # British Pound / Swiss Franc
    "GBPJPY": 700.0,    # British Pound / Japanese Yen
    "GBPUSD": 100000.0,   # British Pound / US Dollar
    "GBPCAD": 74000.0,   # British Pound / Canadian Dollar
    "GBPNZD": 61000.0,   # British Pound / New Zealand Dollar

    # NZD pairs
    "NZDCAD": 74000.0,    # New Zealand Dollar / Canadian Dollar
    "NZDCHF": 122000.0,   # New Zealand Dollar / Swiss Franc
    "NZDJPY": 700.0,    # New Zealand Dollar / Japanese Yen
    "NZDUSD": 100000.0,   # New Zealand Dollar / US Dollar
    
    # USD pairs
    "USDCAD": 74000.0,    # US Dollar / Canadian Dollar
    "USDCHF": 122000.0,   # US Dollar / Swiss Franc
    "USDJPY": 700.0,      # US Dollar / Japanese Yen
    
    # Precious Metals
    "XAUUSD": 100.0,      # Gold / US Dollar
    # Cryptocurrencies
    "ADAUSD": 10000.0,       # $1 per full 1.00 move with 1 lot
    "AVAXUSD": 100.0,      # $1 per full 1.00 move with 1 lot
    "BCHUSD": 10.0,       # $1 per full 1.00 move with 1 lot
    "BTCUSD": 1.0,       # $1 per full 1.00 move with 1 lot
    "DOGEUSD": 100000.0,      # $1 per full 1.00 move with 1 lot
    "ETHUSD": 1.0,       # $1 per full 1.00 move with 1 lot
    "LINKUSD": 250.0,      # $1 per full 1.00 move with 1 lot
    "LTCUSD": 100.0,       # $1 per full 1.00 move with 1 lot
    "SOLUSD": 100.0,       # $1 per full 1.00 move with 1 lot
    "XRPUSD": 50000.0,       # $1 per full 1.00 move with 1 lot
    # Add other symbols as needed
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

import logging
from datetime import datetime
import os

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_TO_FILE = True
LOG_DIRECTORY = "logs"  # Directory for log files

# Log file name format (will include timestamp)
LOG_FILE_FORMAT = 'profit_loss_summary_{timestamp}.log'

# Generate log file path
def get_log_file_path():
    """Generate log file path with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"profit_loss_calculator_{timestamp}.log"
    return os.path.join(LOG_DIRECTORY, filename)

# Log file path
LOG_FILE = get_log_file_path() if LOG_TO_FILE else None

# =============================================================================
# OUTPUT CONFIGURATION
# =============================================================================

# Output settings
OUTPUT_DIRECTORY = "output"  # Directory for output files
ENABLE_CONSOLE_OUTPUT = True  # Show results in console
ENABLE_JSON_OUTPUT = True     # Save results to JSON file

# JSON file name format
JSON_FILE_FORMAT = 'profit_loss_summary_{timestamp}.json'

# Generate JSON output file path
def get_json_output_path():
    """Generate JSON output file path with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"profit_loss_summary_{timestamp}.json"
    return os.path.join(OUTPUT_DIRECTORY, filename)

# Default JSON output file
OUTPUT_JSON_FILE = get_json_output_path()

# =============================================================================
# VALIDATION SETTINGS
# =============================================================================

# Whether to validate all symbols have configuration
VALIDATE_SYMBOL_CONFIG = True

# Whether to skip positions/orders with missing symbol configuration
SKIP_MISSING_SYMBOL_CONFIG = True

# Whether to log warnings for missing symbol configurations
LOG_MISSING_SYMBOL_WARNINGS = True

# =============================================================================
# ERROR HANDLING
# =============================================================================

# Whether to continue processing other accounts if one fails
CONTINUE_ON_ACCOUNT_ERROR = True

# Maximum number of connection attempts per account
MAX_CONNECTION_ATTEMPTS = 3

# Whether to log detailed error information
LOG_DETAILED_ERRORS = True

# =============================================================================
# MAGIC NUMBER FILTERING
# =============================================================================

# Enable magic number filtering
ENABLE_MAGIC_FILTER = False

# Magic numbers to filter positions and orders (empty list = all positions/orders)
# This matches the original system's behavior
MAGIC_NUMBER_FILTER = []  # Example: [12345, 67890] to filter specific magic numbers

# Legacy compatibility
MAGIC_NUMBER = 0  # For compatibility with original system

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_configuration():
    """
    Validate the configuration settings.
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # Validate accounts
    if not ACCOUNTS:
        errors.append("No accounts configured in ACCOUNTS list")
    
    for i, account in enumerate(ACCOUNTS):
        if not isinstance(account, dict):
            errors.append(f"Account {i} is not a dictionary")
            continue
            
        required_fields = ['MT5_ACCOUNT', 'MT5_PASSWORD', 'MT5_SERVER', 'MT5_TERMINAL_PATH']
        for field in required_fields:
            if field not in account:
                errors.append(f"Account {i} missing required field: {field}")
            elif not account[field]:
                errors.append(f"Account {i} has empty value for field: {field}")
    
    # Validate processing delay
    if not isinstance(ACCOUNT_PROCESSING_DELAY, (int, float)) or ACCOUNT_PROCESSING_DELAY < 0:
        errors.append("ACCOUNT_PROCESSING_DELAY must be a non-negative number")
    
    # Validate DOLLAR_PER_LOT_PER_PRICE_UNIT
    if not DOLLAR_PER_LOT_PER_PRICE_UNIT:
        errors.append("DOLLAR_PER_LOT_PER_PRICE_UNIT cannot be empty")
    
    for symbol, value in DOLLAR_PER_LOT_PER_PRICE_UNIT.items():
        if not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"Invalid DOLLAR_PER_LOT_PER_PRICE_UNIT value for {symbol}: {value}")
    
    return len(errors) == 0, errors

if __name__ == "__main__":
    # Validate configuration when run directly
    is_valid, errors = validate_configuration()
    if is_valid:
        print("Configuration is valid!")
        print(f"Configured accounts: {len(ACCOUNTS)}")
        print(f"Configured symbols: {len(DOLLAR_PER_LOT_PER_PRICE_UNIT)}")
    else:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")