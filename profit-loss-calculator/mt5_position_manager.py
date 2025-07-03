#!/usr/bin/env python3
"""
MT5 Position Manager - Profit/Loss Calculator

This module handles position and pending order profit/loss calculations
with the same function names as the original system for consistency.
"""

import MetaTrader5 as mt5
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import math

# Import configuration and connection utilities
from config import (
    DOLLAR_PER_LOT_PER_PRICE_UNIT,
    MT5_CONNECTION_RETRIES,
    MT5_RETRY_DELAY,
    MAGIC_NUMBER_FILTER,
    ENABLE_MAGIC_FILTER,
    POSITION_CACHE_DURATION,
    ORDER_CACHE_DURATION
)
from mt5_connection import ensure_mt5_connection, optimize_mt5_query, get_mt5_error_description

# Cache for positions and orders to reduce API calls
_position_cache = {}
_order_cache = {}
_last_position_fetch = 0
_last_order_fetch = 0

def is_valid_position(position) -> bool:
    """
    Validate if a position object has all required attributes.
    This function maintains the same signature as the original system.
    
    Args:
        position: MT5 position object
        
    Returns:
        bool: True if position is valid, False otherwise
    """
    if not position:
        return False
        
    required_attrs = ['ticket', 'symbol', 'type', 'volume', 'price_open', 'sl', 'tp', 'profit']
    
    for attr in required_attrs:
        if not hasattr(position, attr):
            logging.error(f"Position missing required attribute: {attr}")
            return False
            
    return True

def is_valid_order(order) -> bool:
    """
    Validate if an order object has all required attributes.
    
    Args:
        order: MT5 order object
        
    Returns:
        bool: True if order is valid, False otherwise
    """
    if not order:
        return False
        
    required_attrs = ['ticket', 'symbol', 'type', 'volume_initial', 'price_open', 'sl', 'tp']
    
    for attr in required_attrs:
        if not hasattr(order, attr):
            logging.error(f"Order missing required attribute: {attr}")
            return False
            
    return True

def get_cached_positions() -> Optional[List]:
    """
    Get cached positions if they're still valid, otherwise fetch fresh data.
    
    Returns:
        List of positions or None if fetch fails
    """
    global _position_cache, _last_position_fetch
    
    current_time = time.time()
    
    # Check if cache is still valid
    if (current_time - _last_position_fetch) < POSITION_CACHE_DURATION and _position_cache:
        logging.debug("Using cached position data")
        return _position_cache.get('positions')
    
    # Fetch fresh data
    logging.debug("Fetching fresh position data")
    positions = optimize_mt5_query(mt5.positions_get)
    
    if positions is not None:
        # Apply magic number filter if enabled
        if ENABLE_MAGIC_FILTER and MAGIC_NUMBER_FILTER:
            positions = [pos for pos in positions if pos.magic in MAGIC_NUMBER_FILTER]
            logging.debug(f"Filtered positions by magic numbers: {len(positions)} positions")
        
        _position_cache = {'positions': positions}
        _last_position_fetch = current_time
        return positions
    
    logging.error("Failed to fetch positions")
    return None

def get_cached_orders() -> Optional[List]:
    """
    Get cached pending orders if they're still valid, otherwise fetch fresh data.
    
    Returns:
        List of orders or None if fetch fails
    """
    global _order_cache, _last_order_fetch
    
    current_time = time.time()
    
    # Check if cache is still valid
    if (current_time - _last_order_fetch) < ORDER_CACHE_DURATION and _order_cache:
        logging.debug("Using cached order data")
        return _order_cache.get('orders')
    
    # Fetch fresh data
    logging.debug("Fetching fresh order data")
    orders = optimize_mt5_query(mt5.orders_get)
    
    if orders is not None:
        # Apply magic number filter if enabled
        if ENABLE_MAGIC_FILTER and MAGIC_NUMBER_FILTER:
            orders = [order for order in orders if order.magic in MAGIC_NUMBER_FILTER]
            logging.debug(f"Filtered orders by magic numbers: {len(orders)} orders")
        
        _order_cache = {'orders': orders}
        _last_order_fetch = current_time
        return orders
    
    logging.error("Failed to fetch orders")
    return None

def clear_cache():
    """
    Clear the position and order cache.
    """
    global _position_cache, _order_cache, _last_position_fetch, _last_order_fetch
    
    _position_cache = {}
    _order_cache = {}
    _last_position_fetch = 0
    _last_order_fetch = 0
    logging.debug("Cache cleared")

def calculate_profit_loss_percentage(potential_profit: float, potential_loss: float) -> Optional[float]:
    """
    Calculate the percentage difference between potential profit and potential loss.
    Formula: ((potential_profit - abs(potential_loss)) / abs(potential_loss)) * 100
    
    Args:
        potential_profit (float): The potential profit value
        potential_loss (float): The potential loss value (typically negative)
        
    Returns:
        Optional[float]: Percentage difference, or None if calculation not possible
    """
    try:
        # Handle edge cases
        if potential_loss == 0.0:
            return None  # Cannot calculate percentage when loss is zero
        
        if potential_profit == 0.0 and potential_loss == 0.0:
            return None  # Both values are zero
        
        # Use absolute value of potential_loss for calculation
        abs_loss = abs(potential_loss)
        
        # Calculate percentage difference
        percentage = ((potential_profit - abs_loss) / abs_loss) * 100
        
        return round(percentage, 2)
        
    except (ZeroDivisionError, TypeError, ValueError) as e:
        logging.debug(f"Error calculating profit/loss percentage: {e}")
        return None

def calculate_risk_reward_ratio(potential_profit: float, potential_loss: float) -> Optional[float]:
    """
    Calculate the risk-reward ratio (potential_profit / abs(potential_loss)).
    
    Args:
        potential_profit (float): The potential profit value
        potential_loss (float): The potential loss value (typically negative)
        
    Returns:
        Optional[float]: Risk-reward ratio, or None if calculation not possible
    """
    try:
        # Handle edge cases
        if potential_loss == 0.0:
            return None  # Cannot calculate ratio when loss is zero
        
        if potential_profit == 0.0 and potential_loss == 0.0:
            return None  # Both values are zero
        
        # Use absolute value of potential_loss for calculation
        abs_loss = abs(potential_loss)
        
        # Calculate risk-reward ratio
        ratio = potential_profit / abs_loss
        
        return round(ratio, 2)
        
    except (ZeroDivisionError, TypeError, ValueError) as e:
        logging.debug(f"Error calculating risk-reward ratio: {e}")
        return None

def calculate_position_profit_loss() -> Dict[str, Any]:
    """
    Calculate profit and loss for all open positions.
    This function maintains the same signature as the original system.
    
    Returns:
        dict: Summary of position profit/loss calculations
    """
    try:
        # Ensure MT5 connection
        if not ensure_mt5_connection():
            logging.error("MT5 connection failed in calculate_position_profit_loss")
            return {
                'total_positions': 0,
                'total_current_pl': 0.0,
                'total_potential_loss': 0.0,
                'total_potential_profit': 0.0,
                'positions': [],
                'error': 'MT5 connection failed'
            }
        
        # Get all open positions
        positions = get_cached_positions()
        
        if positions is None:
            logging.error("Failed to retrieve positions")
            return {
                'total_positions': 0,
                'total_current_pl': 0.0,
                'total_potential_loss': 0.0,
                'total_potential_profit': 0.0,
                'positions': [],
                'error': 'Failed to retrieve positions'
            }
        
        total_current_pl = 0.0
        total_potential_loss = 0.0
        total_potential_profit = 0.0
        position_details = []
        
        for position in positions:
            if not is_valid_position(position):
                logging.warning(f"Skipping invalid position: {position}")
                continue
            
            try:
                # Get current symbol info for price calculations
                symbol_info = optimize_mt5_query(mt5.symbol_info, position.symbol)
                if not symbol_info:
                    logging.warning(f"Could not get symbol info for {position.symbol}")
                    continue
                
                # Get current price (bid for sell positions, ask for buy positions)
                current_price = symbol_info.bid if position.type == mt5.ORDER_TYPE_SELL else symbol_info.ask
                
                # Calculate current P/L (this is already provided by MT5)
                current_pl = position.profit
                total_current_pl += current_pl
                
                # Calculate potential loss and profit based on SL/TP
                potential_loss = 0.0
                potential_profit = 0.0
                
                # Get dollar per lot per price unit for this symbol
                dollar_per_lot_per_unit = DOLLAR_PER_LOT_PER_PRICE_UNIT.get(position.symbol, 10.0)
                
                if position.type == mt5.ORDER_TYPE_BUY:
                    # Buy position
                    if position.sl > 0:  # Stop Loss set
                        price_diff = position.price_open - position.sl
                        potential_loss = -(price_diff * position.volume * dollar_per_lot_per_unit)
                    
                    if position.tp > 0:  # Take Profit set
                        price_diff = position.tp - position.price_open
                        potential_profit = price_diff * position.volume * dollar_per_lot_per_unit
                        
                elif position.type == mt5.ORDER_TYPE_SELL:
                    # Sell position
                    if position.sl > 0:  # Stop Loss set
                        price_diff = position.sl - position.price_open
                        potential_loss = -(price_diff * position.volume * dollar_per_lot_per_unit)
                    
                    if position.tp > 0:  # Take Profit set
                        price_diff = position.price_open - position.tp
                        potential_profit = price_diff * position.volume * dollar_per_lot_per_unit
                
                total_potential_loss += potential_loss
                total_potential_profit += potential_profit
                
                # Calculate percentage difference and risk-reward ratio for this position
                profit_loss_percentage = calculate_profit_loss_percentage(potential_profit, potential_loss)
                risk_reward_ratio = calculate_risk_reward_ratio(potential_profit, potential_loss)
                profit_loss_difference = potential_profit - abs(potential_loss) if potential_loss != 0 else None
                
                # Store position details
                position_detail = {
                    'ticket': position.ticket,
                    'symbol': position.symbol,
                    'type': 'BUY' if position.type == mt5.ORDER_TYPE_BUY else 'SELL',
                    'volume': position.volume,
                    'price_open': position.price_open,
                    'current_price': current_price,
                    'sl': position.sl if position.sl > 0 else None,
                    'tp': position.tp if position.tp > 0 else None,
                    'current_pl': current_pl,
                    'potential_loss': potential_loss if potential_loss != 0 else None,
                    'potential_profit': potential_profit if potential_profit != 0 else None,
                    'profit_loss_percentage': profit_loss_percentage,
                    'risk_reward_ratio': risk_reward_ratio,
                    'profit_loss_difference': profit_loss_difference,
                    'magic': getattr(position, 'magic', 0),
                    'comment': getattr(position, 'comment', ''),
                    'time': datetime.fromtimestamp(position.time).strftime('%Y-%m-%d %H:%M:%S') if hasattr(position, 'time') else None
                }
                
                position_details.append(position_detail)
                
            except Exception as e:
                logging.error(f"Error processing position {position.ticket}: {e}")
                continue
        
        # Calculate combined percentage difference and risk-reward ratio
        combined_profit_loss_percentage = calculate_profit_loss_percentage(total_potential_profit, total_potential_loss)
        combined_risk_reward_ratio = calculate_risk_reward_ratio(total_potential_profit, total_potential_loss)
        combined_profit_loss_difference = total_potential_profit - abs(total_potential_loss) if total_potential_loss != 0 else None
        
        result = {
            'total_positions': len(position_details),
            'total_current_pl': total_current_pl,
            'total_potential_loss': total_potential_loss,
        'total_potential_profit': total_potential_profit,
         'combined_profit_loss_percentage': calculate_profit_loss_percentage(total_potential_profit, total_potential_loss),
         'combined_risk_reward_ratio': calculate_risk_reward_ratio(total_potential_profit, total_potential_loss),
         'combined_profit_loss_difference': total_potential_profit - abs(total_potential_loss) if total_potential_loss != 0 else None,
            'positions': position_details
        }
        
        logging.info(f"Calculated P/L for {len(position_details)} positions")
        logging.info(f"Total current P/L: ${total_current_pl:.2f}")
        logging.info(f"Total potential loss: ${total_potential_loss:.2f}")
        logging.info(f"Total potential profit: ${total_potential_profit:.2f}")
        
        return result
        
    except Exception as e:
        logging.error(f"Error in calculate_position_profit_loss: {e}", exc_info=True)
        return {
            'total_positions': 0,
            'total_current_pl': 0.0,
            'total_potential_loss': 0.0,
            'total_potential_profit': 0.0,
            'positions': [],
            'error': str(e)
        }

def calculate_pending_order_profit_loss() -> Dict[str, Any]:
    """
    Calculate potential profit and loss for all pending orders.
    This function maintains the same signature as the original system.
    
    Returns:
        dict: Summary of pending order profit/loss calculations
    """
    try:
        # Ensure MT5 connection
        if not ensure_mt5_connection():
            logging.error("MT5 connection failed in calculate_pending_order_profit_loss")
            return {
                'total_orders': 0,
                'total_potential_loss': 0.0,
                'total_potential_profit': 0.0,
                'orders': [],
                'error': 'MT5 connection failed'
            }
        
        # Get all pending orders
        orders = get_cached_orders()
        
        if orders is None:
            logging.error("Failed to retrieve pending orders")
            return {
                'total_orders': 0,
                'total_potential_loss': 0.0,
                'total_potential_profit': 0.0,
                'orders': [],
                'error': 'Failed to retrieve pending orders'
            }
        
        total_potential_loss = 0.0
        total_potential_profit = 0.0
        order_details = []
        
        for order in orders:
            if not is_valid_order(order):
                logging.warning(f"Skipping invalid order: {order}")
                continue
            
            try:
                # Get current symbol info for price calculations
                symbol_info = optimize_mt5_query(mt5.symbol_info, order.symbol)
                if not symbol_info:
                    logging.warning(f"Could not get symbol info for {order.symbol}")
                    continue
                
                # Get current price (bid for sell orders, ask for buy orders)
                current_price = symbol_info.bid if order.type in [mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_TYPE_SELL_STOP] else symbol_info.ask
                
                # Calculate potential loss and profit based on SL/TP
                potential_loss = 0.0
                potential_profit = 0.0
                
                # Get dollar per lot per price unit for this symbol
                dollar_per_lot_per_unit = DOLLAR_PER_LOT_PER_PRICE_UNIT.get(order.symbol, 10.0)
                
                if order.type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP]:
                    # Buy order
                    if order.sl > 0:  # Stop Loss set
                        price_diff = order.price_open - order.sl
                        potential_loss = -(price_diff * order.volume_initial * dollar_per_lot_per_unit)
                    
                    if order.tp > 0:  # Take Profit set
                        price_diff = order.tp - order.price_open
                        potential_profit = price_diff * order.volume_initial * dollar_per_lot_per_unit
                        
                elif order.type in [mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_TYPE_SELL_STOP]:
                    # Sell order
                    if order.sl > 0:  # Stop Loss set
                        price_diff = order.sl - order.price_open
                        potential_loss = -(price_diff * order.volume_initial * dollar_per_lot_per_unit)
                    
                    if order.tp > 0:  # Take Profit set
                        price_diff = order.price_open - order.tp
                        potential_profit = price_diff * order.volume_initial * dollar_per_lot_per_unit
                
                total_potential_loss += potential_loss
                total_potential_profit += potential_profit
                
                # Calculate percentage difference and risk-reward ratio for this order
                profit_loss_percentage = calculate_profit_loss_percentage(potential_profit, potential_loss)
                risk_reward_ratio = calculate_risk_reward_ratio(potential_profit, potential_loss)
                profit_loss_difference = potential_profit - abs(potential_loss) if potential_loss != 0 else None
                
                # Determine order type string
                order_type_map = {
                    mt5.ORDER_TYPE_BUY_LIMIT: 'BUY_LIMIT',
                    mt5.ORDER_TYPE_SELL_LIMIT: 'SELL_LIMIT',
                    mt5.ORDER_TYPE_BUY_STOP: 'BUY_STOP',
                    mt5.ORDER_TYPE_SELL_STOP: 'SELL_STOP',
                    mt5.ORDER_TYPE_BUY_STOP_LIMIT: 'BUY_STOP_LIMIT',
                    mt5.ORDER_TYPE_SELL_STOP_LIMIT: 'SELL_STOP_LIMIT'
                }
                
                order_type_str = order_type_map.get(order.type, f'UNKNOWN({order.type})')
                
                # Store order details
                order_detail = {
                    'ticket': order.ticket,
                    'symbol': order.symbol,
                    'type': order_type_str,
                    'volume': order.volume_initial,
                    'price_open': order.price_open,
                    'current_price': current_price,
                    'sl': order.sl if order.sl > 0 else None,
                    'tp': order.tp if order.tp > 0 else None,
                    'potential_loss': potential_loss if potential_loss != 0 else None,
                    'potential_profit': potential_profit if potential_profit != 0 else None,
                    'profit_loss_percentage': profit_loss_percentage,
                    'risk_reward_ratio': risk_reward_ratio,
                    'profit_loss_difference': profit_loss_difference,
                    'magic': getattr(order, 'magic', 0),
                    'comment': getattr(order, 'comment', ''),
                    'time_setup': datetime.fromtimestamp(order.time_setup).strftime('%Y-%m-%d %H:%M:%S') if hasattr(order, 'time_setup') else None,
                    'time_expiration': datetime.fromtimestamp(order.time_expiration).strftime('%Y-%m-%d %H:%M:%S') if hasattr(order, 'time_expiration') and order.time_expiration > 0 else None
                }
                
                order_details.append(order_detail)
                
            except Exception as e:
                logging.error(f"Error processing order {order.ticket}: {e}")
                continue
        
        result = {
            'total_orders': len(order_details),
            'total_potential_loss': total_potential_loss,
            'total_potential_profit': total_potential_profit,
            'combined_profit_loss_percentage': calculate_profit_loss_percentage(total_potential_profit, total_potential_loss),
            'combined_risk_reward_ratio': calculate_risk_reward_ratio(total_potential_profit, total_potential_loss),
            'combined_profit_loss_difference': total_potential_profit - abs(total_potential_loss) if total_potential_loss != 0 else None,
            'orders': order_details
        }
        
        logging.info(f"Calculated P/L for {len(order_details)} pending orders")
        logging.info(f"Total potential loss: ${total_potential_loss:.2f}")
        logging.info(f"Total potential profit: ${total_potential_profit:.2f}")
        
        return result
        
    except Exception as e:
        logging.error(f"Error in calculate_pending_order_profit_loss: {e}", exc_info=True)
        return {
            'total_orders': 0,
            'total_potential_loss': 0.0,
            'total_potential_profit': 0.0,
            'orders': [],
            'error': str(e)
        }

def log_comprehensive_summary(position_data: Dict[str, Any], order_data: Dict[str, Any], account_name: str = "Current Account") -> None:
    """
    Log a comprehensive summary of positions and orders.
    This function maintains the same signature as the original system.
    
    Args:
        position_data (dict): Position profit/loss data
        order_data (dict): Order profit/loss data
        account_name (str): Name of the account for identification
    """
    try:
        # Calculate combined totals
        combined_potential_loss = position_data.get('total_potential_loss', 0.0) + order_data.get('total_potential_loss', 0.0)
        combined_potential_profit = position_data.get('total_potential_profit', 0.0) + order_data.get('total_potential_profit', 0.0)
        total_current_pl = position_data.get('total_current_pl', 0.0)
        
        # Log header
        logging.info("=" * 80)
        logging.info(f"COMPREHENSIVE PROFIT/LOSS SUMMARY - {account_name}")
        logging.info("=" * 80)
        
        # Log overall summary
        logging.info("OVERALL SUMMARY:")
        logging.info(f"  Total Open Positions: {position_data.get('total_positions', 0)}")
        logging.info(f"  Total Pending Orders: {order_data.get('total_orders', 0)}")
        logging.info(f"  Current Unrealized P/L: ${total_current_pl:.2f}")
        logging.info(f"  Combined Potential Loss: ${combined_potential_loss:.2f}")
        logging.info(f"  Combined Potential Profit: ${combined_potential_profit:.2f}")
        
        # Calculate and display combined percentage metrics
        combined_profit_loss_percentage = calculate_profit_loss_percentage(combined_potential_profit, combined_potential_loss)
        combined_risk_reward_ratio = calculate_risk_reward_ratio(combined_potential_profit, combined_potential_loss)
        combined_profit_loss_difference = combined_potential_profit - abs(combined_potential_loss) if combined_potential_loss != 0 else None
        
        if combined_profit_loss_percentage is not None:
            logging.info(f"  Profit/Loss Percentage: {combined_profit_loss_percentage:.2f}%")
        if combined_risk_reward_ratio is not None:
            logging.info(f"  Risk/Reward Ratio: {combined_risk_reward_ratio:.2f}")
        if combined_profit_loss_difference is not None:
            logging.info(f"  Profit/Loss Difference: ${combined_profit_loss_difference:.2f}")
        
        # Log breakdown by category
        logging.info("\nBREAKDOWN BY CATEGORY:")
        logging.info(f"  Open Positions:")
        logging.info(f"    Count: {position_data.get('total_positions', 0)}")
        logging.info(f"    Current P/L: ${position_data.get('total_current_pl', 0.0):.2f}")
        logging.info(f"    Potential Loss: ${position_data.get('total_potential_loss', 0.0):.2f}")
        logging.info(f"    Potential Profit: ${position_data.get('total_potential_profit', 0.0):.2f}")
        
        logging.info(f"  Pending Orders:")
        logging.info(f"    Count: {order_data.get('total_orders', 0)}")
        logging.info(f"    Potential Loss: ${order_data.get('total_potential_loss', 0.0):.2f}")
        logging.info(f"    Potential Profit: ${order_data.get('total_potential_profit', 0.0):.2f}")
        
        # Log detailed position information
        if position_data.get('positions'):
            logging.info("\nOPEN POSITIONS DETAIL:")
            # Sort positions alphabetically by symbol name
            sorted_positions = sorted(position_data['positions'], key=lambda x: x.get('symbol', ''))
            for pos in sorted_positions:
                logging.info(f"  Ticket {pos['ticket']} | {pos['symbol']} | {pos['type']} {pos['volume']} lots")
                logging.info(f"    Open: {pos['price_open']:.5f} | Current: {pos['current_price']:.5f}")
                if pos.get('sl'):
                    logging.info(f"    SL: {pos['sl']:.5f}")
                if pos.get('tp'):
                    logging.info(f"    TP: {pos['tp']:.5f}")
                logging.info(f"    Current P/L: ${pos['current_pl']:.2f}")
                if pos.get('potential_loss'):
                    logging.info(f"    Potential Loss: ${pos['potential_loss']:.2f}")
                if pos.get('potential_profit'):
                    logging.info(f"    Potential Profit: ${pos['potential_profit']:.2f}")
                
                # Display percentage metrics for this position
                if pos.get('profit_loss_percentage') is not None:
                    logging.info(f"    Profit/Loss Percentage: {pos['profit_loss_percentage']:.2f}%")
                if pos.get('risk_reward_ratio') is not None:
                    logging.info(f"    Risk/Reward Ratio: {pos['risk_reward_ratio']:.2f}")
                if pos.get('profit_loss_difference') is not None:
                    logging.info(f"    Profit/Loss Difference: ${pos['profit_loss_difference']:.2f}")
                logging.info("")
        
        # Log detailed order information
        if order_data.get('orders'):
            logging.info("PENDING ORDERS DETAIL:")
            # Sort orders alphabetically by symbol name
            sorted_orders = sorted(order_data['orders'], key=lambda x: x.get('symbol', ''))
            for order in sorted_orders:
                logging.info(f"  Ticket {order['ticket']} | {order['symbol']} | {order['type']} {order['volume']} lots")
                logging.info(f"    Entry Price: {order['price_open']:.5f} | Current: {order['current_price']:.5f}")
                if order.get('sl'):
                    logging.info(f"    SL: {order['sl']:.5f}")
                if order.get('tp'):
                    logging.info(f"    TP: {order['tp']:.5f}")
                if order.get('potential_loss'):
                    logging.info(f"    Potential Loss: ${order['potential_loss']:.2f}")
                if order.get('potential_profit'):
                    logging.info(f"    Potential Profit: ${order['potential_profit']:.2f}")
                
                # Display percentage metrics for this order
                if order.get('profit_loss_percentage') is not None:
                    logging.info(f"    Profit/Loss Percentage: {order['profit_loss_percentage']:.2f}%")
                if order.get('risk_reward_ratio') is not None:
                    logging.info(f"    Risk/Reward Ratio: {order['risk_reward_ratio']:.2f}")
                if order.get('profit_loss_difference') is not None:
                    logging.info(f"    Profit/Loss Difference: ${order['profit_loss_difference']:.2f}")
                logging.info("")
        
        # Log footer
        logging.info("=" * 80)
        
    except Exception as e:
        logging.error(f"Error in log_comprehensive_summary: {e}", exc_info=True)

def log_position_summary(position_data: Dict[str, Any], account_name: str = "Current Account") -> None:
    """
    Log a summary specifically for open positions.
    This function maintains the same signature as the original system.
    
    Args:
        position_data (dict): Position profit/loss data
        account_name (str): Name of the account for identification
    """
    try:
        logging.info("=" * 60)
        logging.info(f"POSITION SUMMARY - {account_name}")
        logging.info("=" * 60)
        
        logging.info(f"Total Positions: {position_data.get('total_positions', 0)}")
        logging.info(f"Current P/L: ${position_data.get('total_current_pl', 0.0):.2f}")
        logging.info(f"Potential Loss: ${position_data.get('total_potential_loss', 0.0):.2f}")
        logging.info(f"Potential Profit: ${position_data.get('total_potential_profit', 0.0):.2f}")
        
        if position_data.get('positions'):
            logging.info("\nPosition Details:")
            # Sort positions alphabetically by symbol name
            sorted_positions = sorted(position_data['positions'], key=lambda x: x.get('symbol', ''))
            for pos in sorted_positions:
                sl_str = f" SL:{pos['sl']:.5f}" if pos.get('sl') else ""
                tp_str = f" TP:{pos['tp']:.5f}" if pos.get('tp') else ""
                logging.info(f"  {pos['ticket']} | {pos['symbol']} {pos['type']} {pos['volume']} | P/L: ${pos['current_pl']:.2f}{sl_str}{tp_str}")
        
        logging.info("=" * 60)
        
    except Exception as e:
        logging.error(f"Error in log_position_summary: {e}", exc_info=True)

if __name__ == "__main__":
    # Test the position manager module
    import sys
    from config import ACCOUNTS
    from mt5_connection import connect_to_account, disconnect_from_account
    
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    if not ACCOUNTS:
        print("No accounts configured in config.py")
        sys.exit(1)
    
    # Test with first account
    test_account = ACCOUNTS[0]
    print(f"Testing position manager with: {test_account['name']}")
    
    if connect_to_account(test_account):
        print("\nCalculating position P/L...")
        position_data = calculate_position_profit_loss()
        
        print("\nCalculating pending order P/L...")
        order_data = calculate_pending_order_profit_loss()
        
        print("\nLogging comprehensive summary...")
        log_comprehensive_summary(position_data, order_data, test_account['name'])
        
        disconnect_from_account(test_account['name'])
        print("\nTest completed successfully!")
    else:
        print("Connection test failed!")
        sys.exit(1)