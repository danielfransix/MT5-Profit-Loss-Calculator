#!/usr/bin/env python3
"""
Account Processor Module

Handles multi-account processing for the MT5 Profit/Loss Calculator.
This module processes multiple MT5 accounts sequentially with configurable
delays and provides comprehensive reporting.

This module maintains the same function names and structure as the original
system for consistency and compatibility.
"""

import logging
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Import configuration and utilities
from config import (
    ACCOUNTS,
    ACCOUNT_PROCESSING_DELAY as PROCESSING_DELAY_BETWEEN_ACCOUNTS,
    MT5_CONNECTION_RETRIES as PROCESSING_MAX_RETRIES,
    MT5_RETRY_DELAY as PROCESSING_RETRY_DELAY,
    ENABLE_JSON_OUTPUT,
    OUTPUT_DIRECTORY as JSON_OUTPUT_DIR,
    ENABLE_CONSOLE_OUTPUT
)
from mt5_connection import connect_to_account, disconnect_from_account
from mt5_position_manager import (
    get_cached_positions,
    get_cached_orders,
    calculate_position_profit_loss,
    calculate_pending_order_profit_loss
)

def process_single_account(account_config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Process a single MT5 account and calculate profit/loss.
    
    Args:
        account_config (Dict[str, Any]): Account configuration
        
    Returns:
        Tuple[bool, Dict[str, Any]]: (success, account_data)
    """
    account_login = account_config.get('MT5_ACCOUNT', 'Unknown')
    account_server = account_config.get('MT5_SERVER', 'Unknown')
    
    logger = logging.getLogger(__name__)
    logger.info(f"Processing account {account_login} ({account_server})")
    
    account_data = {
        'account_info': {
            'login': account_login,
            'server': account_server,
            'processed_at': datetime.now().isoformat()
        },
        'positions': [],
        'pending_orders': [],
        'summary': {
            'total_profit_loss': 0.0,
            'total_profit_loss_percentage': 0.0,
            'positions_count': 0,
            'pending_orders_count': 0,
            'profitable_positions': 0,
            'losing_positions': 0
        },
        'processing_status': 'failed',
        'error_message': None
    }
    
    try:
        # Connect to account
        if not connect_to_account(account_config):
            account_data['error_message'] = f"Failed to connect to account {account_login}"
            logger.error(account_data['error_message'])
            return False, account_data
        
        # Calculate position profit/loss for all positions
        position_results = calculate_position_profit_loss()
        
        # Calculate pending order profit/loss for all orders
        order_results = calculate_pending_order_profit_loss()
        
        # Store complete calculation results for detailed analysis
        account_data['position_data'] = position_results
        account_data['order_data'] = order_results
        
        # Extract data from results
        if 'error' not in position_results:
            account_data['positions'] = position_results.get('positions', [])
            total_profit_loss = position_results.get('total_current_pl', 0.0)
            
            # Count profitable and losing positions
            profitable_count = sum(1 for pos in account_data['positions'] if pos.get('current_pl', 0.0) > 0)
            losing_count = sum(1 for pos in account_data['positions'] if pos.get('current_pl', 0.0) < 0)
        else:
            logger.warning(f"Error calculating position P/L: {position_results.get('error')}")
            total_profit_loss = 0.0
            profitable_count = 0
            losing_count = 0
        
        if 'error' not in order_results:
            account_data['pending_orders'] = order_results.get('orders', [])
        else:
            logger.warning(f"Error calculating order P/L: {order_results.get('error')}")
        
        # Calculate summary
        account_data['summary'].update({
            'total_profit_loss': total_profit_loss,
            'positions_count': len(account_data['positions']),
            'pending_orders_count': len(account_data['pending_orders']),
            'profitable_positions': profitable_count,
            'losing_positions': losing_count
        })
        
        # Calculate percentage if we have position data
        if account_data['positions']:
            # This is a simplified percentage calculation
            # In a real implementation, you'd want to calculate based on account balance
            account_data['summary']['total_profit_loss_percentage'] = 0.0  # Placeholder
        
        account_data['processing_status'] = 'success'
        logger.info(f"Successfully processed account {account_login}: {len(account_data['positions'])} positions, {len(account_data['pending_orders'])} orders")
        
        return True, account_data
        
    except Exception as e:
        error_msg = f"Error processing account {account_login}: {str(e)}"
        account_data['error_message'] = error_msg
        logger.error(error_msg, exc_info=True)
        return False, account_data
        
    finally:
        # Always disconnect
        try:
            disconnect_from_account()
        except Exception as e:
            logger.warning(f"Error disconnecting from account {account_login}: {e}")

def process_accounts(account_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Process all configured accounts or a specific account.
    
    Args:
        account_filter (str, optional): Specific account login to process
        
    Returns:
        Dict[str, Any]: Processing summary with all account data
    """
    logger = logging.getLogger(__name__)
    
    # Filter accounts if specified
    accounts_to_process = ACCOUNTS
    if account_filter:
        accounts_to_process = [
            acc for acc in ACCOUNTS 
            if str(acc.get('MT5_ACCOUNT', '')) == str(account_filter)
        ]
        
        if not accounts_to_process:
            logger.error(f"Account {account_filter} not found in configuration")
            return {
                'processing_info': {
                    'total_accounts': 0,
                    'accounts_processed_successfully': 0,
                    'accounts_failed': 0,
                    'processing_start_time': datetime.now().isoformat(),
                    'processing_end_time': datetime.now().isoformat()
                },
                'accounts': [],
                'error_message': f"Account {account_filter} not found in configuration"
            }
    
    start_time = datetime.now()
    logger.info(f"Starting processing of {len(accounts_to_process)} accounts")
    
    summary = {
        'processing_info': {
            'total_accounts': len(accounts_to_process),
            'accounts_processed_successfully': 0,
            'accounts_failed': 0,
            'processing_start_time': start_time.isoformat(),
            'processing_end_time': None
        },
        'accounts': []
    }
    
    # Process each account
    for i, account_config in enumerate(accounts_to_process):
        account_login = account_config.get('MT5_ACCOUNT', f'Account_{i+1}')
        
        # Add delay between accounts (except for the first one)
        if i > 0 and PROCESSING_DELAY_BETWEEN_ACCOUNTS > 0:
            logger.info(f"Waiting {PROCESSING_DELAY_BETWEEN_ACCOUNTS} seconds before processing next account...")
            time.sleep(PROCESSING_DELAY_BETWEEN_ACCOUNTS)
        
        # Process account with retries
        success = False
        account_data = None
        
        for attempt in range(PROCESSING_MAX_RETRIES):
            try:
                success, account_data = process_single_account(account_config)
                if success:
                    break
                    
                if attempt < PROCESSING_MAX_RETRIES - 1:
                    logger.warning(f"Retry {attempt + 1}/{PROCESSING_MAX_RETRIES} for account {account_login} in {PROCESSING_RETRY_DELAY} seconds")
                    time.sleep(PROCESSING_RETRY_DELAY)
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for account {account_login}: {e}")
                if attempt < PROCESSING_MAX_RETRIES - 1:
                    time.sleep(PROCESSING_RETRY_DELAY)
        
        # Add account data to summary
        if account_data:
            summary['accounts'].append(account_data)
            
        # Update counters
        if success:
            summary['processing_info']['accounts_processed_successfully'] += 1
        else:
            summary['processing_info']['accounts_failed'] += 1
    
    # Finalize summary
    end_time = datetime.now()
    summary['processing_info']['processing_end_time'] = end_time.isoformat()
    
    # Save JSON output if enabled
    if ENABLE_JSON_OUTPUT:
        save_json_output(summary)
    
    logger.info(f"Processing completed: {summary['processing_info']['accounts_processed_successfully']} successful, {summary['processing_info']['accounts_failed']} failed")
    
    return summary

def save_json_output(summary: Dict[str, Any]) -> None:
    """
    Save processing summary to JSON file.
    
    Args:
        summary (Dict[str, Any]): Processing summary data
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(JSON_OUTPUT_DIR):
            os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"profit_loss_summary_{timestamp}.json"
        filepath = os.path.join(JSON_OUTPUT_DIR, filename)
        
        # Save JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logging.info(f"JSON output saved to: {filepath}")
        
    except Exception as e:
        logging.error(f"Failed to save JSON output: {e}")

def print_summary_to_console(summary: Dict[str, Any]) -> None:
    """
    Print comprehensive formatted summary to console with detailed profit/loss analysis.
    
    Args:
        summary (Dict[str, Any]): Processing summary data
    """
    if not ENABLE_CONSOLE_OUTPUT:
        return
    
    print("\n" + "=" * 100)
    print("MT5 COMPREHENSIVE PROFIT/LOSS ANALYSIS")
    print("=" * 100)
    
    # Processing info
    processing_info = summary.get('processing_info', {})
    print(f"\nProcessing Summary:")
    print(f"  Total Accounts: {processing_info.get('total_accounts', 0)}")
    print(f"  Successful: {processing_info.get('accounts_processed_successfully', 0)}")
    print(f"  Failed: {processing_info.get('accounts_failed', 0)}")
    print(f"  Start Time: {processing_info.get('processing_start_time', 'N/A')}")
    print(f"  End Time: {processing_info.get('processing_end_time', 'N/A')}")
    
    # Account details
    accounts = summary.get('accounts', [])
    if not accounts:
        print("\nNo account data available.")
        return
    
    for account in accounts:
        account_info = account.get('account_info', {})
        account_login = account_info.get('login', 'Unknown')
        account_server = account_info.get('server', 'Unknown')
        
        print(f"\n{'-' * 100}")
        print(f"ACCOUNT: {account_login} ({account_server})")
        print(f"Status: {account.get('processing_status', 'Unknown')}")
        print(f"{'-' * 100}")
        
        if account.get('processing_status') != 'success':
            error_msg = account.get('error_message', 'Unknown error')
            print(f"Error: {error_msg}")
            continue
            
        # Get position and order data
        position_data = account.get('position_data', {})
        order_data = account.get('order_data', {})
        
        # Print detailed analysis
        print_detailed_profit_loss_analysis(position_data, order_data, account_login)
    
    print("\n" + "=" * 100)

def print_detailed_profit_loss_analysis(position_data: Dict[str, Any], order_data: Dict[str, Any], account_name: str) -> None:
    """
    Print comprehensive profit/loss analysis with detailed breakdowns.
    
    Args:
        position_data (Dict[str, Any]): Position profit/loss data
        order_data (Dict[str, Any]): Order profit/loss data
        account_name (str): Account identifier
    """
    # Calculate combined totals
    pos_potential_loss = position_data.get('total_potential_loss', 0.0)
    pos_potential_profit = position_data.get('total_potential_profit', 0.0)
    pos_current_pl = position_data.get('total_current_pl', 0.0)
    pos_count = position_data.get('total_positions', 0)
    
    order_potential_loss = order_data.get('total_potential_loss', 0.0)
    order_potential_profit = order_data.get('total_potential_profit', 0.0)
    order_count = order_data.get('total_orders', 0)
    
    combined_potential_loss = pos_potential_loss + order_potential_loss
    combined_potential_profit = pos_potential_profit + order_potential_profit
    
    # Calculate percentage differences and USD differences
    def calculate_percentage_diff(profit, loss):
        if loss == 0.0:
            return None
        return ((profit - abs(loss)) / abs(loss)) * 100
    
    def calculate_usd_diff(profit, loss):
        return profit - abs(loss)
    
    # SECTION 1: ALL OPEN POSITIONS SUMMARY
    print("\n[1] ALL OPEN POSITIONS SUMMARY")
    print("-" * 50)
    if pos_count > 0:
        pos_percentage_diff = calculate_percentage_diff(pos_potential_profit, pos_potential_loss)
        pos_usd_diff = calculate_usd_diff(pos_potential_profit, pos_potential_loss)
        
        print(f"  Total Positions: {pos_count}")
        print(f"  Current Unrealized P/L: ${pos_current_pl:.2f}")
        print(f"  Potential Loss (if all SL hit): ${pos_potential_loss:.2f}")
        print(f"  Potential Profit (if all TP hit): ${pos_potential_profit:.2f}")
        if pos_percentage_diff is not None:
            print(f"  Percentage Difference: {pos_percentage_diff:.2f}%")
        print(f"  USD Amount Difference: ${pos_usd_diff:.2f}")
        
        # Risk metrics
        if pos_potential_loss != 0:
            risk_reward = pos_potential_profit / abs(pos_potential_loss)
            print(f"  Risk/Reward Ratio: {risk_reward:.2f}")
    else:
        print("  No open positions")
    
    # SECTION 2: INDIVIDUAL OPEN POSITIONS
    print("\n[2] INDIVIDUAL OPEN POSITIONS")
    print("-" * 50)
    positions = position_data.get('positions', [])
    if positions:
        for i, pos in enumerate(positions, 1):
            print(f"  Position {i}: {pos['symbol']} | {pos['type']} {pos['volume']} lots")
            print(f"    Ticket: {pos['ticket']} | Open: {pos['price_open']:.5f} | Current: {pos['current_price']:.5f}")
            print(f"    Current P/L: ${pos['current_pl']:.2f}")
            
            if pos.get('sl'):
                print(f"    Stop Loss: {pos['sl']:.5f}")
            if pos.get('tp'):
                print(f"    Take Profit: {pos['tp']:.5f}")
            
            if pos.get('potential_loss') is not None:
                print(f"    Potential Loss: ${pos['potential_loss']:.2f}")
            if pos.get('potential_profit') is not None:
                print(f"    Potential Profit: ${pos['potential_profit']:.2f}")
            
            if pos.get('profit_loss_percentage') is not None:
                print(f"    Percentage Difference: {pos['profit_loss_percentage']:.2f}%")
            if pos.get('profit_loss_difference') is not None:
                print(f"    USD Amount Difference: ${pos['profit_loss_difference']:.2f}")
            if pos.get('risk_reward_ratio') is not None:
                print(f"    Risk/Reward Ratio: {pos['risk_reward_ratio']:.2f}")
            print()
    else:
        print("  No individual positions to display")
    
    # SECTION 3: ALL PENDING ORDERS SUMMARY
    print("\n[3] ALL PENDING ORDERS SUMMARY")
    print("-" * 50)
    if order_count > 0:
        order_percentage_diff = calculate_percentage_diff(order_potential_profit, order_potential_loss)
        order_usd_diff = calculate_usd_diff(order_potential_profit, order_potential_loss)
        
        print(f"  Total Pending Orders: {order_count}")
        print(f"  Potential Loss (if all SL hit): ${order_potential_loss:.2f}")
        print(f"  Potential Profit (if all TP hit): ${order_potential_profit:.2f}")
        if order_percentage_diff is not None:
            print(f"  Percentage Difference: {order_percentage_diff:.2f}%")
        print(f"  USD Amount Difference: ${order_usd_diff:.2f}")
        
        # Risk metrics
        if order_potential_loss != 0:
            risk_reward = order_potential_profit / abs(order_potential_loss)
            print(f"  Risk/Reward Ratio: {risk_reward:.2f}")
    else:
        print("  No pending orders")
    
    # SECTION 4: INDIVIDUAL PENDING ORDERS
    print("\n[4] INDIVIDUAL PENDING ORDERS")
    print("-" * 50)
    orders = order_data.get('orders', [])
    if orders:
        for i, order in enumerate(orders, 1):
            print(f"  Order {i}: {order['symbol']} | {order['type']} {order['volume']} lots")
            print(f"    Ticket: {order['ticket']} | Entry: {order['price_open']:.5f} | Current: {order['current_price']:.5f}")
            
            if order.get('sl'):
                print(f"    Stop Loss: {order['sl']:.5f}")
            if order.get('tp'):
                print(f"    Take Profit: {order['tp']:.5f}")
            
            if order.get('potential_loss') is not None:
                print(f"    Potential Loss: ${order['potential_loss']:.2f}")
            if order.get('potential_profit') is not None:
                print(f"    Potential Profit: ${order['potential_profit']:.2f}")
            
            if order.get('profit_loss_percentage') is not None:
                print(f"    Percentage Difference: {order['profit_loss_percentage']:.2f}%")
            if order.get('profit_loss_difference') is not None:
                print(f"    USD Amount Difference: ${order['profit_loss_difference']:.2f}")
            if order.get('risk_reward_ratio') is not None:
                print(f"    Risk/Reward Ratio: {order['risk_reward_ratio']:.2f}")
            print()
    else:
        print("  No individual pending orders to display")
    
    # SECTION 5: COMBINED POSITIONS + ORDERS SUMMARY
    print("\n[5] COMBINED POSITIONS + ORDERS SUMMARY")
    print("-" * 50)
    combined_percentage_diff = calculate_percentage_diff(combined_potential_profit, combined_potential_loss)
    combined_usd_diff = calculate_usd_diff(combined_potential_profit, combined_potential_loss)
    
    print(f"  Total Items: {pos_count + order_count} ({pos_count} positions + {order_count} orders)")
    print(f"  Current Unrealized P/L: ${pos_current_pl:.2f} (positions only)")
    print(f"  Combined Potential Loss: ${combined_potential_loss:.2f}")
    print(f"  Combined Potential Profit: ${combined_potential_profit:.2f}")
    if combined_percentage_diff is not None:
        print(f"  Combined Percentage Difference: {combined_percentage_diff:.2f}%")
    print(f"  Combined USD Amount Difference: ${combined_usd_diff:.2f}")
    
    # Combined risk metrics
    if combined_potential_loss != 0:
        combined_risk_reward = combined_potential_profit / abs(combined_potential_loss)
        print(f"  Combined Risk/Reward Ratio: {combined_risk_reward:.2f}")
    
    # SECTION 6: ADDITIONAL USEFUL STATISTICS
    print("\n[6] ADDITIONAL USEFUL STATISTICS")
    print("-" * 50)
    
    # Portfolio exposure analysis
    total_volume_positions = sum(pos.get('volume', 0) for pos in positions)
    total_volume_orders = sum(order.get('volume', 0) for order in orders)
    print(f"  Total Volume Exposure: {total_volume_positions + total_volume_orders:.2f} lots")
    print(f"    Open Positions: {total_volume_positions:.2f} lots")
    print(f"    Pending Orders: {total_volume_orders:.2f} lots")
    
    # Symbol diversification
    position_symbols = set(pos.get('symbol', '') for pos in positions)
    order_symbols = set(order.get('symbol', '') for order in orders)
    all_symbols = position_symbols.union(order_symbols)
    print(f"  Symbol Diversification: {len(all_symbols)} unique symbols")
    
    # Profit/Loss distribution
    profitable_positions = len([pos for pos in positions if pos.get('current_pl', 0) > 0])
    losing_positions = len([pos for pos in positions if pos.get('current_pl', 0) < 0])
    breakeven_positions = len([pos for pos in positions if pos.get('current_pl', 0) == 0])
    
    if pos_count > 0:
        print(f"  Position P/L Distribution:")
        print(f"    Profitable: {profitable_positions} ({(profitable_positions/pos_count)*100:.1f}%)")
        print(f"    Losing: {losing_positions} ({(losing_positions/pos_count)*100:.1f}%)")
        print(f"    Breakeven: {breakeven_positions} ({(breakeven_positions/pos_count)*100:.1f}%)")
    
    # Average position/order sizes
    if pos_count > 0:
        avg_position_size = total_volume_positions / pos_count
        print(f"  Average Position Size: {avg_position_size:.2f} lots")
    
    if order_count > 0:
        avg_order_size = total_volume_orders / order_count
        print(f"  Average Order Size: {avg_order_size:.2f} lots")
    
    # Risk assessment
    if pos_current_pl != 0 and combined_potential_loss != 0:
        current_risk_ratio = abs(combined_potential_loss) / abs(pos_current_pl) if pos_current_pl != 0 else float('inf')
        print(f"  Current Risk Exposure: {current_risk_ratio:.2f}x current P/L")
    
    # Maximum drawdown potential
    max_potential_loss = abs(combined_potential_loss) + abs(pos_current_pl) if pos_current_pl < 0 else abs(combined_potential_loss)
    print(f"  Maximum Potential Drawdown: ${max_potential_loss:.2f}")
    
    # Profit potential vs current unrealized
    if pos_current_pl != 0:
        profit_multiplier = combined_potential_profit / abs(pos_current_pl) if pos_current_pl != 0 else float('inf')
        print(f"  Profit Potential Multiplier: {profit_multiplier:.2f}x current P/L")