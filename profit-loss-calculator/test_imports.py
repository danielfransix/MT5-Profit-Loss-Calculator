#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""

print("Testing imports...")

try:
    print("1. Testing config import...")
    from config import ACCOUNTS, ENABLE_CONSOLE_OUTPUT
    print("   ✓ Config imported successfully")
    
    print("2. Testing account_processor import...")
    from account_processor import process_accounts, print_summary_to_console
    print("   ✓ Account processor imported successfully")
    
    print("3. Testing profit_loss_calculator import...")
    import profit_loss_calculator
    print("   ✓ Main calculator module imported successfully")
    
    print("\n✅ All imports successful! The ModuleNotFoundError has been resolved.")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")

print("\nTest completed.")