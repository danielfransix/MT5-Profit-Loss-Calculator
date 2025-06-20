#!/usr/bin/env python3
"""
MT5 Connection Manager - Multi-Account Support

This module handles MT5 connections for multiple accounts with the same
function names as the original system for consistency.
"""

import MetaTrader5 as mt5
import logging
import time
from typing import Optional, Dict, Any

# Import configuration
from config import (
    MT5_CONNECTION_TIMEOUT,
    MT5_CONNECTION_RETRIES,
    MT5_RETRY_DELAY,
    MAX_CONNECTION_ATTEMPTS
)

def initialize_mt5(account_number: Optional[int] = None, 
                  password: Optional[str] = None, 
                  server: Optional[str] = None, 
                  terminal_path: Optional[str] = None, 
                  log_level: int = logging.INFO) -> bool:
    """
    Initialize the MT5 connection with the specified account and configuration.
    This function maintains the same signature as the original system.
    
    Args:
        account_number (int, optional): MT5 account number
        password (str, optional): MT5 account password
        server (str, optional): MT5 server name
        terminal_path (str, optional): Path to MT5 terminal executable
        log_level (int, optional): Logging level to set for MT5 logs
        
    Returns:
        bool: True if successfully connected, False otherwise
        
    Note:
        When making MT5 API calls with parameters:
        1. Do not pass None values as parameters (e.g., symbol=None) to MT5 functions
        2. Instead, omit the parameter completely when the value is None
        3. For example, use mt5.positions_get() instead of mt5.positions_get(symbol=None)
        4. This prevents "Invalid symbol argument" and similar errors
    """
    
    if not account_number:
        logging.error("Login account number is required for initialize_mt5.")
        return False

    # Prepare connection keyword arguments (excluding path)
    connection_kwargs = {
        "login": account_number,
        "timeout": MT5_CONNECTION_TIMEOUT
    }
    
    if password:
        connection_kwargs["password"] = password
    if server:
        connection_kwargs["server"] = server

    # Connect using the specified path (if provided)
    if terminal_path:
        logging.info(f"Attempting connection via path: {terminal_path} for login {account_number}")
        # Pass path positionally, others as keyword arguments
        if mt5.initialize(terminal_path, **connection_kwargs):
            account_info = mt5.account_info()
            if account_info and account_info.login == account_number:
                logging.info(f"Successfully connected to account {account_number} via path {terminal_path}.")
                return True
            else:
                # This might happen if the terminal at 'terminal_path' is running a different account
                logging.error(f"Connected terminal at path {terminal_path}, but it's logged into account {account_info.login if account_info else 'N/A'} (Expected: {account_number}). Shutting down connection.")
                mt5.shutdown()
                return False
        else:
            logging.error(f"Connection attempt via path {terminal_path} failed. Last error: {mt5.last_error()}")
            return False
    else:
        # Connect without specifying the path (fallback only when no path configured)
        logging.info(f"No terminal path configured, attempting connection without specific path for login {account_number}...")
        # Pass only keyword arguments here
        if mt5.initialize(**connection_kwargs):
            account_info = mt5.account_info()
            if account_info and account_info.login == account_number:
                logging.info(f"Successfully connected to account {account_number} (auto-detected path or running instance).")
                return True
            else:
                logging.error(f"Connected without path, but to wrong account (Expected: {account_number}, Got: {account_info.login if account_info else 'N/A'}). Shutting down.")
                mt5.shutdown()
                return False
        else:
            logging.error(f"Connection attempt without path failed for login {account_number}. Last error: {mt5.last_error()}")
            return False

def shutdown_mt5() -> None:
    """
    Shuts down the connection to the MetaTrader 5 terminal.
    This function maintains the same signature as the original system.
    """
    logging.info("Shutting down MT5 connection...")
    mt5.shutdown()
    logging.info("MT5 connection shut down.")

def ensure_mt5_connection(max_attempts: int = MAX_CONNECTION_ATTEMPTS, 
                         delay_seconds: float = MT5_RETRY_DELAY) -> bool:
    """
    Ensures MT5 is connected, attempting reconnection if necessary.
    This function maintains the same signature as the original system.
    
    Args:
        max_attempts (int): Maximum number of connection attempts
        delay_seconds (float): Delay between attempts in seconds
        
    Returns:
        bool: True if connected, False if connection failed
    """
    if mt5.terminal_info():
        return True
        
    logging.warning("MT5 terminal not connected. Connection may have been lost.")
    logging.warning("Note: This function cannot reconnect without account credentials.")
    logging.warning("Please use connect_to_account() to establish a new connection.")
    
    return False

def connect_to_account(account_config: Dict[str, Any]) -> bool:
    """
    Connect to a specific MT5 account using the provided configuration.
    
    Args:
        account_config (dict): Account configuration containing:
            - MT5_ACCOUNT: MT5 account number
            - MT5_PASSWORD: MT5 account password
            - MT5_SERVER: MT5 server name
            - MT5_TERMINAL_PATH: Path to MT5 terminal executable
            
    Returns:
        bool: True if successfully connected, False otherwise
    """
    try:
        login = account_config.get('MT5_ACCOUNT')
        password = account_config.get('MT5_PASSWORD')
        server = account_config.get('MT5_SERVER')
        path = account_config.get('MT5_TERMINAL_PATH')
        account_name = f"Account {login}"
        
        logging.info(f"Connecting to account: {account_name} (Login: {login})")
        
        # Attempt connection with retry logic
        for attempt in range(MAX_CONNECTION_ATTEMPTS):
            if attempt > 0:
                logging.info(f"Connection attempt {attempt + 1}/{MAX_CONNECTION_ATTEMPTS}")
                time.sleep(MT5_RETRY_DELAY)
            
            if initialize_mt5(
                account_number=login,
                password=password,
                server=server,
                terminal_path=path
            ):
                # Verify connection and get account info
                account_info = mt5.account_info()
                terminal_info = mt5.terminal_info()
                
                if account_info:
                    logging.info(f"Successfully connected to {account_name}")
                    logging.info(f"Account: {account_info.login} | Server: {account_info.server}")
                    logging.info(f"Balance: ${account_info.balance:.2f} | Equity: ${account_info.equity:.2f}")
                    
                    if terminal_info:
                        if not terminal_info.trade_allowed:
                            logging.warning("Trading is disabled in this terminal instance")
                        logging.info(f"Terminal connected: {terminal_info.connected}")
                    
                    return True
                else:
                    logging.error(f"Connected but could not retrieve account info for {account_name}")
                    shutdown_mt5()
            else:
                logging.error(f"Failed to connect to {account_name} (attempt {attempt + 1})")
        
        logging.error(f"Failed to connect to {account_name} after {MAX_CONNECTION_ATTEMPTS} attempts")
        return False
        
    except Exception as e:
        logging.error(f"Error connecting to account {account_config.get('MT5_ACCOUNT', 'Unknown')}: {e}")
        return False

def disconnect_from_account(account_name: str = "current account") -> None:
    """
    Disconnect from the current MT5 account.
    
    Args:
        account_name (str): Name of the account for logging purposes
    """
    try:
        logging.info(f"Disconnecting from {account_name}")
        shutdown_mt5()
        logging.info(f"Successfully disconnected from {account_name}")
    except Exception as e:
        logging.error(f"Error disconnecting from {account_name}: {e}")

def get_mt5_error_description(error_code: int) -> str:
    """
    Get a human-readable description for an MT5 error code.
    This function maintains the same signature as the original system.
    
    Args:
        error_code (int): MT5 error code
        
    Returns:
        str: Error description
    """
    error_descriptions = {
        0: "No error",
        1: "Generic error",
        2: "Common error",
        3: "Invalid trade parameters",
        4: "Trade server is busy",
        5: "Old version of the client terminal",
        6: "No connection with trade server",
        7: "Not enough rights",
        8: "Too frequent requests",
        9: "Malfunctional trade operation",
        64: "Account disabled",
        65: "Invalid account",
        128: "Trade timeout",
        129: "Invalid price",
        130: "Invalid stops",
        131: "Invalid trade volume",
        132: "Market is closed",
        133: "Trade is disabled",
        134: "Not enough money",
        135: "Price changed",
        136: "Off quotes",
        137: "Broker is busy",
        138: "Requote",
        139: "Order is locked",
        140: "Long positions only allowed",
        141: "Too many requests",
        145: "Modification denied",
        146: "Trade context is busy",
        147: "Expirations are denied",
        148: "Too many open/pending orders",
        4301: "No connection to trading server",
        4302: "Internal network error",
        5001: "Too many pending and open orders",
        5202: "Order already exists",
        5207: "Invalid price",
        10021: "Invalid parameter"
    }
    
    return error_descriptions.get(error_code, f"Unknown error ({error_code})")

def optimize_mt5_query(func, *args, retries: int = MT5_CONNECTION_RETRIES, 
                      retry_delay: float = MT5_RETRY_DELAY, **kwargs):
    """
    Execute an MT5 query with optimized error handling and retry logic.
    This function maintains the same signature as the original system.
    
    Args:
        func: MT5 API function to call (e.g., mt5.positions_get)
        *args: Positional arguments for the function
        retries (int): Number of retry attempts
        retry_delay (float): Delay between retries in seconds
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result from the MT5 API call or None if all attempts fail
    """
    for attempt in range(retries):
        # Ensure MT5 connection before each attempt
        if not ensure_mt5_connection():
            logging.error("MT5 is not connected and reconnection failed")
            return None
            
        try:
            # Call the MT5 function
            result = func(*args, **kwargs)
            
            # Check if the call was successful
            if result is not None:
                return result
                
            # If failed, get the error code and decide what to do
            error_code = mt5.last_error()
            
            # Handle specific error codes
            if error_code == 4301:  # No connection
                logging.error("No connection to trading server")
            else:
                error_description = get_mt5_error_description(error_code)
                logging.error(f"MT5 API error: {error_code} - {error_description}")
                
            # If this was the last attempt, return None
            if attempt == retries - 1:
                logging.error(f"All {retries} attempts to call {func.__name__} failed with error code {error_code}")
                return None
                
            # Wait before retrying
            logging.info(f"Retrying ({attempt+1}/{retries}) in {retry_delay} seconds...")
            time.sleep(retry_delay)
            
        except Exception as e:
            logging.error(f"Exception calling {func.__name__}: {e}", exc_info=True)
            
            # If this was the last attempt, return None
            if attempt == retries - 1:
                logging.error(f"All {retries} attempts to call {func.__name__} failed with exception")
                return None
                
            # Wait before retrying
            logging.info(f"Retrying ({attempt+1}/{retries}) in {retry_delay} seconds...")
            time.sleep(retry_delay)
            
    return None  # Should never reach here, but just in case

if __name__ == "__main__":
    # Test the connection module
    import sys
    from config import ACCOUNTS
    
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    if not ACCOUNTS:
        print("No accounts configured in config.py")
        sys.exit(1)
    
    # Test connection to first account
    test_account = ACCOUNTS[0]
    print(f"Testing connection to: Account {test_account['MT5_ACCOUNT']}")

    if connect_to_account(test_account):
        print("Connection test successful!")
        disconnect_from_account(f"Account {test_account['MT5_ACCOUNT']}")
    else:
        print("Connection test failed!")
        sys.exit(1)