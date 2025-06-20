#!/usr/bin/env python3
"""
Example Configuration File for MT5 Profit/Loss Calculator

Copy this file to 'config.py' and update with your actual MT5 account details.
NEVER commit your actual config.py file with real credentials to version control.
"""

# =============================================================================
# ACCOUNT CONFIGURATION (CRITICAL SETUP STEP)
# =============================================================================

# Configure your MT5 account(s) here
# You can add multiple accounts for batch processing
ACCOUNTS = [
    {
        "MT5_ACCOUNT": 12345678,                           # Your MT5 login number (integer)
        "MT5_PASSWORD": "your_mt5_password",               # Your MT5 account password (string)
        "MT5_SERVER": "YourBroker-Demo",                  # Your broker's server name (string)
        "MT5_TERMINAL_PATH": r"C:\Program Files\MetaTrader 5\terminal64.exe"  # Path to MT5 terminal
    },
    # Add more accounts as needed:
    # {
    #     "MT5_ACCOUNT": 87654321,
    #     "MT5_PASSWORD": "your_password2",
    #     "MT5_SERVER": "YourBroker-Live",
    #     "MT5_TERMINAL_PATH": r"C:\Program Files\MetaTrader 5\terminal64.exe"
    # }
]

# =============================================================================
# PROCESSING CONFIGURATION
# =============================================================================

# Processing delays
ENABLE_ACCOUNT_PROCESSING_DELAY = True
ACCOUNT_PROCESSING_DELAY = 2.0  # seconds between accounts

# Error handling
CONTINUE_ON_ACCOUNT_FAILURE = True
MAX_ACCOUNT_FAILURES = 3

# Output settings
OUTPUT_DIRECTORY = "output"  # Directory for output files
ENABLE_CONSOLE_OUTPUT = True  # Show results in console
ENABLE_JSON_OUTPUT = True     # Save results to JSON file

# Magic number filtering (optional)
ENABLE_MAGIC_FILTER = False   # Enable filtering by magic numbers
MAGIC_NUMBER_FILTER = []      # List of magic numbers to include (empty = all)

# =============================================================================
# SYMBOL CONFIGURATION (DOLLAR PER LOT VALUES)
# =============================================================================

# This dictionary tells the system how much profit/loss occurs when the market
# moves 1.0 price unit in your favor/against you on a 1 lot position.
# Use the Tickmill Forex Calculator to calculate values for new symbols:
# https://www.tickmill.com/tools/forex-calculators

DOLLAR_PER_LOT_PER_PRICE_UNIT = {
    # Major Forex Pairs
    "EURUSD": 100000.0,
    "GBPUSD": 100000.0,
    "AUDUSD": 100000.0,
    "NZDUSD": 100000.0,
    "USDCAD": 74000.0,
    "USDCHF": 122000.0,
    "USDJPY": 700.0,
    
    # Cross Pairs
    "EURJPY": 700.0,
    "GBPJPY": 700.0,
    "EURGBP": 134000.0,
    "AUDCAD": 74000.0,
    
    # Precious Metals
    "XAUUSD": 100.0,  # Gold
    "XAGUSD": 5000.0, # Silver
    
    # Cryptocurrencies
    "BTCUSD": 1.0,
    "ETHUSD": 1.0,
    
    # Add more symbols as needed
    # "SYMBOL": value,
}

# =============================================================================
# VALIDATION SETTINGS
# =============================================================================

VALIDATE_SYMBOL_CONFIG = True        # Validate all symbols have configuration
SKIP_MISSING_SYMBOL_CONFIG = True    # Skip positions with missing symbol config
LOG_MISSING_SYMBOL_WARNINGS = True  # Log warnings for missing symbols

# =============================================================================
# ERROR HANDLING
# =============================================================================

CONTINUE_ON_ACCOUNT_ERROR = True     # Continue processing if account fails
MAX_CONNECTION_ATTEMPTS = 3          # Maximum connection attempts per account
LOG_DETAILED_ERRORS = True           # Log detailed error information

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

LOG_LEVEL = "INFO"                   # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True                   # Enable file logging
LOG_DIRECTORY = "logs"               # Directory for log files

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

# JSON file name format
JSON_FILE_FORMAT = 'profit_loss_summary_{timestamp}.json'

# =============================================================================
# CACHE SETTINGS
# =============================================================================

ENABLE_POSITION_CACHE = True
POSITION_CACHE_DURATION = 30  # seconds

ENABLE_ORDER_CACHE = True
ORDER_CACHE_DURATION = 30  # seconds

# =============================================================================
# CONNECTION SETTINGS
# =============================================================================

CONNECTION_TIMEOUT = 60000  # milliseconds
CONNECTION_RETRIES = 3
RETRY_DELAY = 1.0  # seconds

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
    
    for i, account in enumerate(ACCOUNTS, 1):
        account_id = account.get('MT5_ACCOUNT', f'Account_{i}')
        
        # Check required fields
        required_fields = ['MT5_ACCOUNT', 'MT5_PASSWORD', 'MT5_SERVER', 'MT5_TERMINAL_PATH']
        for field in required_fields:
            if not account.get(field):
                errors.append(f"Account '{account_id}' missing required field: {field}")
        
        # Validate account number is integer
        if 'MT5_ACCOUNT' in account and not isinstance(account['MT5_ACCOUNT'], int):
            errors.append(f"Account '{account_id}' MT5_ACCOUNT must be an integer")
    
    # Validate symbol configuration
    if not DOLLAR_PER_LOT_PER_PRICE_UNIT:
        errors.append("DOLLAR_PER_LOT_PER_PRICE_UNIT is empty")
    
    # Validate processing delay
    if ENABLE_ACCOUNT_PROCESSING_DELAY and ACCOUNT_PROCESSING_DELAY <= 0:
        errors.append("ACCOUNT_PROCESSING_DELAY must be positive when enabled")
    
    return len(errors) == 0, errors

if __name__ == "__main__":
    # Test configuration when run directly
    is_valid, errors = validate_configuration()
    if is_valid:
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration errors found:")
        for error in errors:
            print(f"  - {error}")