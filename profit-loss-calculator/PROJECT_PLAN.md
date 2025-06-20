# MT5 Profit/Loss Calculator - Standalone Tool Project Plan

## Project Understanding

I understand that you want to replicate the existing profit/loss summary feature from the original directory into a standalone tool in this new folder.

**Key Requirements:**
- **DO NOT** remove or modify the original feature in the existing system
- Learn from the current implementation and its dependencies
- Create a completely standalone codebase that can be shared independently
- Replicate all functionality of the existing profit/loss summary feature
- **Pure Reporting Tool**: This is exclusively a reporting/analysis tool that connects to MT5 terminals to read position and order data
- **Multi-Account Support**: Support multiple MT5 accounts/terminals with configurable delays between runs
- **Variable Name Consistency**: Use the same variable names as the original system where possible for consistency

## Current Feature Analysis

After analyzing the existing codebase, I've identified the core profit/loss summary feature consists of:

### Main Entry Point
- **File**: `profit_loss_summary.py`
- **Purpose**: Main script that connects to MT5, fetches data, calculates P&L, and displays results
- **Key Functions**: Calls `log_comprehensive_summary()` from `mt5_position_manager`

### Core Dependencies
1. **mt5_config_loader.py** - Configuration management
2. **mt5_connection.py** - MT5 terminal connection handling
3. **mt5_position_manager.py** - Core P&L calculation logic

### Key Functionality
The profit/loss summary feature provides:

1. **Multi-Account Processing**:
   - Sequential processing of multiple MT5 accounts/terminals
   - Configurable delay between account runs
   - Clear account identification in each summary report

2. **Open Positions Analysis** (per account):
   - Current unrealized P&L for all open positions
   - Potential loss if Stop Loss is hit
   - Potential profit if Take Profit is hit
   - Position details (ticket, symbol, type, volume, prices)

3. **Pending Orders Analysis** (per account):
   - Potential loss/profit for pending orders when triggered
   - Distance to trigger price
   - Order details (ticket, symbol, type, volume, prices)

4. **Comprehensive Summary** (per account):
   - Combined totals across positions and orders
   - Detailed breakdown by category
   - Professional logging format with account identification

### Critical Components Identified

#### Configuration Requirements
- **DOLLAR_PER_LOT_PER_PRICE_UNIT**: Symbol-specific conversion rates for accurate P&L calculation
- **Multiple MT5 Account Settings**: Support for multiple MT5 accounts/terminals with login credentials and server information
- **Execution Settings**: Configurable delay between account runs (in seconds)

#### Core Functions
- `calculate_position_profit_loss()`: Calculates P&L for open positions
- `calculate_pending_order_profit_loss()`: Calculates P&L for pending orders
- `log_comprehensive_summary()`: Generates formatted summary output
- `fetch_open_positions()`: Retrieves and validates open positions
- `fetch_pending_orders()`: Retrieves and validates pending orders
- `validate_symbol_configuration()`: Ensures symbols have proper configuration

#### Utility Functions
- `ensure_mt5_connection()`: Connection management with retry logic
- `get_mt5_error_description()`: Error code translation
- `is_valid_position()` / `is_valid_order()`: Data validation

## Implementation Plan

### Phase 1: Project Setup and Core Infrastructure
**Objective**: Create the basic project structure and core dependencies

**Tasks**:
1. Create project directory structure
2. Set up requirements.txt with necessary dependencies
3. Create standalone configuration system with multi-account support
4. Implement MT5 connection management for multiple accounts
5. Create basic logging setup with account identification
6. Write project README with setup instructions

**Deliverables**:
- Project folder structure
- `requirements.txt`
- `config.py` (standalone configuration with multi-account support)
- `mt5_connection.py` (multi-account connection management)
- `README.md` (setup and usage guide)

### Phase 2: Core Calculation Engine
**Objective**: Implement the profit/loss calculation logic with multi-account support

**Tasks**:
1. Create position and order data fetching functions (using original variable names)
2. Implement position profit/loss calculation (`calculate_position_profit_loss`)
3. Implement pending order profit/loss calculation (`calculate_pending_order_profit_loss`)
4. Add symbol validation and configuration checking (`validate_symbol_configuration`)
5. Create data validation functions (`is_valid_position`, `is_valid_order`)
6. Implement error handling and retry logic
7. Add account-specific processing logic

**Deliverables**:
- `position_manager.py` (core calculation engine with original function names)
- `data_validator.py` (validation utilities)
- `symbol_config.py` (symbol-specific settings)

### Phase 3: Summary Generation and Output
**Objective**: Create the summary generation and display system

**Tasks**:
1. Implement comprehensive summary logging
2. Create formatted output functions
3. Add console and file output options
4. Implement summary statistics
5. Create export functionality (optional)

**Deliverables**:
- `summary_generator.py` (summary creation)
- `output_formatter.py` (display formatting)
- Enhanced logging with multiple output options

### Phase 4: Main Application and Multi-Account Processing
**Objective**: Create the main application entry point with multi-account support

**Tasks**:
1. Create main application script with multi-account processing loop
2. Implement command-line interface
3. Add configuration options via CLI
4. Create sequential account processing with configurable delays
5. Add account identification in output reports
6. Implement error handling for individual account failures

**Deliverables**:
- `main.py` (primary entry point with multi-account support)
- `cli.py` (command-line interface)
- `account_processor.py` (multi-account processing logic)
- Executable script for easy running

### Phase 5: Testing and Documentation
**Objective**: Ensure reliability and provide comprehensive documentation

**Tasks**:
1. Create unit tests for core functions
2. Implement integration tests
3. Add error scenario testing
4. Create comprehensive documentation
5. Write usage examples
6. Create troubleshooting guide

**Deliverables**:
- Test suite (`tests/` directory)
- Complete documentation
- Usage examples
- Troubleshooting guide

### Phase 6: Packaging and Distribution
**Objective**: Make the tool easily distributable

**Tasks**:
1. Create installation script
2. Package as standalone executable (optional)
3. Create distribution package
4. Add version management
5. Create release documentation

**Deliverables**:
- Installation script
- Distribution package
- Release notes
- Version management system

## Technical Architecture

### Module Structure
```
profit-loss-calculator/
├── main.py                 # Main entry point with multi-account processing
├── config.py              # Configuration management (multi-account support)
├── mt5_connection.py      # MT5 connection handling (multi-account)
├── position_manager.py    # Core P&L calculation logic (original function names)
├── summary_generator.py   # Summary creation and formatting
├── data_validator.py      # Data validation utilities
├── symbol_config.py       # Symbol-specific configurations
├── account_processor.py   # Multi-account processing logic
├── cli.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── README.md             # Setup and usage guide
├── PROJECT_PLAN.md       # This document
└── tests/                # Test suite
    ├── test_calculations.py
    ├── test_connection.py
    ├── test_multi_account.py
    └── test_validation.py
```

### Key Dependencies
- **MetaTrader5**: MT5 Python API
- **logging**: For comprehensive logging
- **configparser**: Configuration management
- **argparse**: Command-line interface
- **datetime**: Time handling
- **json**: Data serialization (optional)
- **time**: For delays between account processing

### Multi-Account Configuration Structure
```python
# Example configuration structure
ACCOUNTS = [
    {
        'name': 'Account 1',
        'login': 12345678,
        'password': 'password1',
        'server': 'MetaQuotes-Demo',
        'path': 'C:\\Program Files\\MetaTrader 5\\terminal64.exe'
    },
    {
        'name': 'Account 2', 
        'login': 87654321,
        'password': 'password2',
        'server': 'ICMarkets-Live02',
        'path': 'C:\\Program Files\\MetaTrader 5\\terminal64.exe'
    }
]

# Processing settings
ACCOUNT_PROCESSING_DELAY = 5  # seconds between account runs
DOLLAR_PER_LOT_PER_PRICE_UNIT = {
    # Same structure as original system
    'EURUSD': 10.0,
    'GBPUSD': 10.0,
    # ... etc
}
```

### Data Flow
1. **Configuration Loading**: Load multiple MT5 account credentials and symbol configurations
2. **Account Processing Loop**: For each configured account:
   a. **MT5 Connection**: Establish connection to specific MT5 terminal
   b. **Account Identification**: Display current account being processed
   c. **Data Fetching**: Retrieve open positions and pending orders
   d. **Data Validation**: Validate and filter retrieved data
   e. **P&L Calculation**: Calculate profit/loss for positions and orders
   f. **Summary Generation**: Create comprehensive summary with account details
   g. **Output Display**: Format and display results
   h. **Connection Cleanup**: Close MT5 connection
   i. **Delay**: Wait configured delay before next account (if applicable)
3. **Process Completion**: All accounts processed

## Success Criteria

1. **Functional Completeness**: All features from the original system are replicated with identical calculations
2. **Multi-Account Support**: Successfully processes multiple MT5 accounts sequentially with configurable delays
3. **Standalone Operation**: Tool runs independently without original codebase dependencies
4. **Variable Name Consistency**: Uses same function and variable names as original system where applicable
5. **Easy Distribution**: Can be easily shared and set up by others
6. **Robust Error Handling**: Graceful handling of connection and data issues, including individual account failures
7. **Clear Account Identification**: Each summary clearly identifies which account the data belongs to
8. **Clear Documentation**: Comprehensive setup and usage instructions for multi-account configuration
9. **Maintainable Code**: Clean, well-documented, and modular code structure

## Risk Mitigation

1. **MT5 Connection Issues**: Implement robust retry logic and connection validation for each account
2. **Multi-Account Failures**: Handle individual account connection failures without stopping entire process
3. **Symbol Configuration**: Provide clear documentation for adding new symbols to DOLLAR_PER_LOT_PER_PRICE_UNIT
4. **Data Validation**: Comprehensive validation to handle unexpected data formats from different brokers
5. **Account Configuration**: Clear validation and error messages for account setup issues
6. **Error Handling**: Detailed error messages and logging for troubleshooting with account identification
7. **Version Compatibility**: Test with different MT5 versions and Python environments across multiple brokers

## Next Steps

Once you approve this updated plan, I will begin with Phase 1: Project Setup and Core Infrastructure. Each phase will be completed sequentially, with testing and validation at each step to ensure the tool works correctly before moving to the next phase.

**Key Implementation Focus:**
- Pure reporting tool (no trading functionality)
- Multi-account sequential processing with configurable delays
- Identical variable names and function signatures as original system
- Robust error handling for individual account failures
- Clear account identification in all output

The estimated timeline for complete implementation is approximately 6 phases of development, with each phase building upon the previous one to create a robust, standalone, multi-account profit/loss calculator tool that maintains consistency with the original system while adding multi-account capabilities.