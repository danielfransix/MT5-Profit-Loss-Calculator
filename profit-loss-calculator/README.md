# MT5 Standalone Profit/Loss Calculator

A pure reporting tool that calculates profit/loss for multiple MT5 accounts without any trading functionality. This standalone calculator processes accounts sequentially with configurable delays and provides comprehensive reporting.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
  - [Step 1: Install Python Dependencies](#step-1-install-python-dependencies)
  - [Step 2: Download and Setup Files](#step-2-download-and-setup-files)
  - [Step 3: Configure Your MT5 Accounts](#step-3-configure-your-mt5-accounts)
- [Configuration](#configuration)
  - [Account Configuration (Critical Setup Step)](#account-configuration-critical-setup-step)
  - [Processing Configuration](#processing-configuration)
  - [Symbol Configuration (Dollar Per Lot Values)](#symbol-configuration-dollar-per-lot-values)
- [First-Time Setup Validation](#first-time-setup-validation)
  - [Step 1: Test Configuration](#step-1-test-configuration)
  - [Step 2: Test MT5 Connection](#step-2-test-mt5-connection)
  - [Step 3: Verify Output](#step-3-verify-output)
  - [Common First-Time Issues](#common-first-time-issues)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Validation Mode](#validation-mode)
  - [Command Line Options](#command-line-options)
- [Output Examples](#output-examples)
  - [Console Output](#console-output)
  - [JSON Output](#json-output)
- [Module Structure](#module-structure)
  - [Core Modules](#core-modules)
  - [Key Functions](#key-functions)
- [Error Handling](#error-handling)
  - [Connection Failures](#connection-failures)
  - [Account Processing Failures](#account-processing-failures)
  - [Data Validation](#data-validation)
- [Logging](#logging)
  - [Log Levels](#log-levels)
  - [Log Files](#log-files)
- [Performance Optimization](#performance-optimization)
  - [Caching](#caching)
  - [Connection Management](#connection-management)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debug Mode](#debug-mode)
  - [Validation Mode](#validation-mode-1)
- [Requirements](#requirements)
- [License](#license)
- [Support](#support)
- [Version History](#version-history)

## Features

- **Pure Reporting Tool**: No trading functionality - only calculates and reports P/L
- **Multi-Account Support**: Process multiple MT5 accounts sequentially
- **Configurable Delays**: Add delays between account processing to avoid overloading
- **Comprehensive Error Handling**: Graceful handling of connection failures and errors
- **Flexible Output**: Console output, JSON file output, or both
- **Detailed Logging**: Comprehensive logging with configurable levels
- **Cache Optimization**: Efficient data retrieval with caching mechanisms
- **Magic Number Filtering**: Optional filtering by magic numbers
- **Original Function Names**: Maintains compatibility with existing systems

## Prerequisites

Before setting up this calculator, ensure you have:

1. **Windows Operating System**: Required for MetaTrader 5 compatibility
2. **Python 3.7 or higher**: Download from [python.org](https://www.python.org/downloads/)
3. **MetaTrader 5 Terminal**: Download and install from your broker or [MetaQuotes](https://www.metatrader5.com/)
4. **Active MT5 Trading Account(s)**: With valid login credentials from your broker
5. **Internet Connection**: For connecting to MT5 servers

## Installation & Setup

### Step 1: Install Python Dependencies

1. **Install MetaTrader5 Python Package**:
   ```bash
   pip install MetaTrader5
   ```

2. **Install Additional Requirements** (if requirements.txt exists):
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Download and Setup Files

1. **Clone or Download**: Place all files in your desired directory
2. **Create Required Directories**: The system will auto-create `logs/` and `output/` directories

### Step 3: Configure Your MT5 Accounts

**IMPORTANT**: This is the most critical step for new users.

1. **Copy the example configuration**:
   ```bash
   copy config_example.py config.py
   ```
   
2. **Edit your new `config.py` file** with your actual MT5 account details
3. **Never commit your `config.py` file** to version control (it's already in `.gitignore`)
4. **Keep your `config.py` file secure** and never share it with others

## Configuration

### Account Configuration (Critical Setup Step)

**For New Users**: You must configure your MT5 account details before the calculator will work.

#### Finding Your MT5 Account Information

1. **Login Number**: Found in your broker's account details email or MT5 terminal
2. **Password**: Your MT5 account password (not your broker website password)
3. **Server**: Found in MT5 terminal under Tools → Options → Server tab
4. **Terminal Path**: Location where MT5 is installed (usually `C:\Program Files\MetaTrader 5\terminal64.exe`)

#### Configuring the ACCOUNTS List

Edit the `ACCOUNTS` list in `config.py` with your actual account details:

```python
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
```

**Important Notes:**
- Replace ALL placeholder values with your actual account information
- `MT5_ACCOUNT`: Your MT5 login number (integer, not a custom name)
- `MT5_PASSWORD`: Your MT5 account password (string)
- `MT5_SERVER`: Your broker's server name (found in MT5 terminal)
- `MT5_TERMINAL_PATH`: Full path to your MT5 terminal executable
- Keep passwords secure and never share your config file
- You can configure multiple accounts for batch processing

### Processing Configuration

```python
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

# Validation settings
VALIDATE_SYMBOL_CONFIG = True        # Validate all symbols have configuration
SKIP_MISSING_SYMBOL_CONFIG = True    # Skip positions with missing symbol config
LOG_MISSING_SYMBOL_WARNINGS = True  # Log warnings for missing symbols

# Error handling
CONTINUE_ON_ACCOUNT_ERROR = True     # Continue processing if account fails
MAX_CONNECTION_ATTEMPTS = 3          # Maximum connection attempts per account
LOG_DETAILED_ERRORS = True           # Log detailed error information

# Logging settings
LOG_LEVEL = "INFO"                   # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True                   # Enable file logging
LOG_DIRECTORY = "logs"               # Directory for log files

# JSON file name format
JSON_FILE_FORMAT = 'profit_loss_summary_{timestamp}.json'
```

### Symbol Configuration (Dollar Per Lot Values)

This is the most important configuration for accurate P/L calculations. The `DOLLAR_PER_LOT_PER_PRICE_UNIT` dictionary tells the system how much profit/loss occurs when the market moves 1.0 price unit in your favor/against you on a 1 lot position.

#### How to Calculate Dollar Per Lot Values

**For New Users**: You need to calculate the correct values for each trading pair you use. Here's how:

1. **Go to the Tickmill Forex Calculator**: [https://www.tickmill.com/tools/forex-calculators](https://www.tickmill.com/tools/forex-calculators)

2. **Set up the calculation**:
   - **Platform**: Select "MT5"
   - **Account Currency**: Select "USD" (or your account currency)
   - **Instrument**: Select the currency pair you want to calculate (e.g., "AUD/CAD")
   - **Account Leverage**: Leave as "1:1" (leverage doesn't affect this calculation)
   - **Direction**: Select "BUY" (direction doesn't matter for this calculation)
   - **Open Price**: Enter any current market price (e.g., "1")
   - **Close Price**: Enter the open price + 1.0 (e.g., if open price is "1", enter "2")
   - **Lot Size**: Enter "1"

3. **Click "Calculate"** and look at the **"Profit USD"** value

4. **Add the result to your config**: Take the profit value and add it to the `DOLLAR_PER_LOT_PER_PRICE_UNIT` dictionary

**Example**: If the calculator shows that a 1.0 price movement on 1 lot of AUD/CAD results in $72,832.4 USD profit, then you would add:
```python
"AUDCAD": 72832.4,
```

#### Current Configuration

The system comes pre-configured with values for major pairs:

```python
DOLLAR_PER_LOT_PER_PRICE_UNIT = {
    # Major Forex Pairs (pre-calculated)
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
    
    # Cryptocurrencies
    "BTCUSD": 1.0,
    "ETHUSD": 1.0,
    # Add more symbols as needed
}
```

**Important**: If you trade symbols not listed above, you MUST calculate and add their values using the method described above, or the system will not be able to calculate accurate P/L for those positions.

## First-Time Setup Validation

**For New Users**: Before running the calculator for the first time, validate your configuration:

### Step 1: Test Configuration

```bash
# Validate your configuration without processing any accounts
python profit_loss_calculator.py --validate-only
```

This will check:
- All required account fields are present
- MT5 terminal paths are valid
- Symbol configurations are properly formatted
- No configuration errors exist

### Step 2: Test MT5 Connection

```bash
# Run the calculator with debug logging to see detailed connection info
python profit_loss_calculator.py --log-level DEBUG
```

Watch for:
- Successful MT5 terminal connections
- Account login confirmations
- Position and order retrieval
- Any connection errors or warnings

### Step 3: Verify Output

After a successful run, check:
- **Console Output**: Should show account summaries and totals
- **Log Files**: Created in `logs/` directory with detailed processing info
- **JSON Output**: Created in `output/` directory with complete results

### Common First-Time Issues

1. **"No connection to trading server"**
   - Ensure MT5 terminal is running and logged in
   - Check your internet connection
   - Verify account credentials are correct

2. **"Invalid account"**
   - Double-check your login number (MT5_ACCOUNT)
   - Verify your password (MT5_PASSWORD)
   - Confirm the server name (MT5_SERVER) matches your broker

3. **"Failed to retrieve positions"**
   - Make sure you have open positions or pending orders
   - Check that your account has trading permissions
   - Verify the MT5 terminal is not restricted

## Usage

### Windows Batch File (Recommended)

For Windows users, use the provided batch file for an interactive menu:

```cmd
run_calculator.bat
```

This provides options for:
1. **Run Installation Test** - Validates MT5 installation and dependencies
2. **Validate Configuration Only** - Checks configuration without processing
3. **Run Calculator (Default Settings)** - Standard execution for all accounts
4. **Run Calculator (Debug Mode)** - Enhanced logging for troubleshooting
5. **Run Calculator (JSON Output Only)** - Saves results without console output
6. **Run Calculator (Specific Account)** - Process only a specific account by login number

### Basic Command Line Usage

```bash
# Run with default settings (all accounts)
python profit_loss_calculator.py

# Run for specific account only
python profit_loss_calculator.py --account 12345678

# Run with debug logging
python profit_loss_calculator.py --log-level DEBUG

# Use custom log file
python profit_loss_calculator.py --log-file custom.log

# Disable console output (log only)
python profit_loss_calculator.py --no-console

# Output only JSON file
python profit_loss_calculator.py --json-only
```

### Validation Mode

```bash
# Validate configuration without processing
python profit_loss_calculator.py --validate-only
```

### Command Line Options

- `--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: Set logging level
- `--log-file PATH`: Specify custom log file path
- `--no-console`: Disable console output
- `--json-only`: Output only JSON file, disable console
- `--account LOGIN`: Process only specified account by login number
- `--validate-only`: Only validate configuration
- `--version`: Show version information
- `--help`: Show help message

## Output Examples

### Console Output

```
================================================================================
MULTI-ACCOUNT PROFIT/LOSS PROCESSING SUMMARY
================================================================================
Processing Duration: 12.45 seconds
Accounts Configured: 2
Successfully Processed: 2
Failed: 0
Processing Delay: 2 seconds

COMBINED TOTALS (All Accounts):
  Total Positions: 5
  Total Orders: 3
  Current Unrealized P/L: $1,234.56
  Total Potential Loss: $-2,500.00
  Total Potential Profit: $3,750.00

ACCOUNT BREAKDOWN:

  Main Trading Account:
    Positions: 3 | Orders: 2
    Current P/L: $856.23
    Potential Loss: $-1,500.00
    Potential Profit: $2,250.00

  Secondary Account:
    Positions: 2 | Orders: 1
    Current P/L: $378.33
    Potential Loss: $-1,000.00
    Potential Profit: $1,500.00
================================================================================
```

### JSON Output

The tool generates a comprehensive JSON file with detailed information:

```json
{
  "processing_info": {
    "start_time": "2024-01-15T10:30:00",
    "end_time": "2024-01-15T10:30:12",
    "processing_duration_seconds": 12.45,
    "total_accounts_configured": 2,
    "accounts_processed_successfully": 2,
    "accounts_failed": 0
  },
  "combined_totals": {
    "total_positions": 5,
    "total_orders": 3,
    "total_current_unrealized_pl": 1234.56,
    "total_potential_loss": -2500.00,
    "total_potential_profit": 3750.00
  },
  "account_summaries": [...],
  "detailed_results": {...}
}
```

## Module Structure

### Core Modules

- `profit_loss_calculator.py` - Main entry point and command-line interface
- `account_processor.py` - Multi-account processing logic
- `mt5_connection.py` - MT5 connection management
- `mt5_position_manager.py` - Position and order data retrieval
- `config.py` - Configuration settings and validation
- `test_installation.py` - Installation and setup validation
- `requirements.txt` - Python dependencies
- `run_calculator.bat` - Windows batch file for easy execution

### Output Directory

- `output/` - Directory containing JSON output files with timestamps

### Key Functions

The tool maintains the same function names as the original system:

- `connect_to_account()`: Connect to MT5 account
- `disconnect_from_account()`: Disconnect from MT5
- `calculate_position_profit_loss()`: Calculate position P/L
- `calculate_pending_order_profit_loss()`: Calculate order P/L
- `log_comprehensive_summary()`: Log detailed summary
- `print_summary_to_console()`: Print formatted summary
- `setup_logging()`: Configure logging
- `main()`: Main execution function
- `process_accounts()`: Process all configured accounts
- `validate_configuration()`: Validate configuration settings

## Error Handling

### Connection Failures
- Automatic retry with configurable attempts
- Graceful handling of connection timeouts
- Detailed error logging with MT5 error codes

### Account Processing Failures
- Continue processing other accounts on individual failures
- Configurable maximum failure threshold
- Detailed error reporting in output

### Data Validation
- Validation of position and order objects
- Symbol information verification
- Configuration validation on startup

## Logging

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information and progress
- **WARNING**: Warning messages for non-critical issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that stop processing

### Log Files
- Configurable log file location
- Automatic log directory creation
- UTF-8 encoding support
- Timestamped log entries

## Performance Optimization

### Caching
- Position data caching with configurable duration
- Order data caching to reduce API calls
- Automatic cache clearing between accounts

### Connection Management
- Optimized MT5 query execution
- Retry logic for failed API calls
- Connection validation before operations

## Security Considerations

### Data Protection
- **No Trading Operations**: Tool is read-only and cannot place trades
- **Configuration Security**: Never commit your `config.py` file with real credentials to version control
- **Use Example Config**: Copy `config_example.py` to `config.py` and update with your credentials
- **Password Protection**: Store passwords securely and never share your configuration file
- **Log Security**: Logs may contain account numbers - keep log files secure
- **Output Security**: JSON output files contain trading data - treat as confidential

### File Security
- **Sensitive Files**: The following files contain sensitive information:
  - `config.py` (your actual configuration with credentials)
  - `output/*.json` (trading data and account information)
  - `logs/*.log` (may contain account numbers and trading details)
- **Git Ignore**: A `.gitignore` file is provided to prevent committing sensitive files
- **Backup Security**: If backing up, ensure sensitive files are encrypted

### Network Security
- **Connection Security**: Use secure MT5 server connections provided by your broker
- **Firewall**: Ensure your firewall allows MT5 terminal connections
- **VPN**: Consider using a VPN if required by your broker

### Best Practices
- **Regular Updates**: Keep your MT5 terminal and Python packages updated
- **Access Control**: Limit access to the directory containing this tool
- **Credential Rotation**: Regularly update your MT5 passwords
- **Monitoring**: Monitor your accounts for any unauthorized access

## Troubleshooting

### Common Issues

1. **"No connection to trading server"**
   - Check MT5 terminal is running
   - Verify account credentials
   - Check internet connection

2. **"Invalid account"**
   - Verify login number and server
   - Check account is active
   - Ensure correct terminal path

3. **"Failed to retrieve positions"**
   - Check MT5 terminal permissions
   - Verify account has positions
   - Check symbol availability

### Debug Mode

Run with debug logging for detailed troubleshooting:

```bash
python profit_loss_calculator.py --log-level DEBUG
```

### Validation Mode

Test configuration without processing:

```bash
python profit_loss_calculator.py --validate-only
```

## Requirements

- Python 3.7+
- MetaTrader5 Python package
- Windows OS (for MT5 compatibility)
- Active MT5 terminal installation
- Valid MT5 account credentials

## License

This tool is provided as-is for educational and reporting purposes. Use at your own risk.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run in debug mode for detailed logs
3. Validate configuration with `--validate-only`
4. Review log files for error details

## Version History

### v1.0.0
- Initial release
- Multi-account support
- Configurable processing delays
- Comprehensive error handling
- JSON and console output
- Original function name compatibility