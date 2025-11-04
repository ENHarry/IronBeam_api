#!/usr/bin/env python3
"""
Example: Using the Demo Account Reset Tool

This script demonstrates different ways to use the demo account reset functionality.
"""

import os
import sys
from datetime import datetime

# Add the current directory to path to import our reset tool
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the reset tool classes
from reset_demo_account import DemoAccountResetManager


def example_basic_reset():
    """Example 1: Basic account reset."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Account Reset")
    print("="*60)
    
    # Demo credentials (replace with your actual credentials)
    API_KEY = "your_api_key_here"
    USERNAME = "your_username_here"
    PASSWORD = "your_password_here"
    ACCOUNT_ID = "your_account_id_here"
    
    try:
        # Initialize the reset manager
        manager = DemoAccountResetManager(
            api_key=API_KEY,
            username=USERNAME,
            password=PASSWORD
        )
        
        # Authenticate
        print("🔐 Authenticating...")
        if not manager.authenticate():
            print("❌ Authentication failed")
            return
        
        # Get account info before reset
        print("\n📊 Getting account information...")
        account_info = manager.get_account_info(ACCOUNT_ID)
        if account_info:
            manager.display_account_info(account_info, "Account Status - BEFORE")
        
        # Reset account
        print(f"\n🔄 Resetting account {ACCOUNT_ID}...")
        success = manager.reset_account(ACCOUNT_ID, "XAP100")
        
        if success:
            print("✅ Reset successful!")
            
            # Get account info after reset
            print("\n📊 Getting updated account information...")
            account_info = manager.get_account_info(ACCOUNT_ID)
            if account_info:
                manager.display_account_info(account_info, "Account Status - AFTER")
        else:
            print("❌ Reset failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_multiple_accounts():
    """Example 2: Reset multiple accounts."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multiple Account Reset")
    print("="*60)
    
    # Demo credentials
    API_KEY = "your_api_key_here"
    USERNAME = "your_username_here"
    PASSWORD = "your_password_here"
    
    # Multiple accounts to reset
    accounts = [
        {"id": "account1", "template": "XAP50"},
        {"id": "account2", "template": "XAP100"},
        {"id": "account3", "template": "XAP150"}
    ]
    
    try:
        # Initialize manager
        manager = DemoAccountResetManager(API_KEY, USERNAME, PASSWORD)
        
        # Authenticate once
        if not manager.authenticate():
            print("❌ Authentication failed")
            return
        
        # Reset each account
        for i, account in enumerate(accounts, 1):
            print(f"\n{i}. Resetting account {account['id']} with template {account['template']}...")
            
            success = manager.reset_account(account['id'], account['template'])
            if success:
                print(f"   ✅ Account {account['id']} reset successfully")
            else:
                print(f"   ❌ Account {account['id']} reset failed")
                
    except Exception as e:
        print(f"❌ Error: {e}")


def example_account_info_only():
    """Example 3: Get account information without resetting."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Account Information Only")
    print("="*60)
    
    # Demo credentials
    API_KEY = "your_api_key_here"
    USERNAME = "your_username_here"
    PASSWORD = "your_password_here"
    ACCOUNT_ID = "your_account_id_here"
    
    try:
        # Initialize manager
        manager = DemoAccountResetManager(API_KEY, USERNAME, PASSWORD)
        
        # Authenticate
        if not manager.authenticate():
            print("❌ Authentication failed")
            return
        
        # Get account information
        account_info = manager.get_account_info(ACCOUNT_ID)
        if account_info:
            manager.display_account_info(account_info)
            
            # Show additional analysis
            balance = account_info['balance']
            positions = account_info['positions']
            
            print(f"\n📈 Account Analysis:")
            print(f"   Number of positions: {len(positions.positions)}")
            
            if balance.balances:
                cash_balance = balance.balances[0].cash_balance
                if hasattr(balance.balances[0], 'unrealized_pl') and balance.balances[0].unrealized_pl:
                    total_pl = balance.balances[0].unrealized_pl
                    print(f"   Total P&L: ${total_pl:,.2f}")
                    print(f"   Return %: {(total_pl / cash_balance) * 100:.2f}%")
        else:
            print("❌ Could not retrieve account information")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_with_error_handling():
    """Example 4: Comprehensive error handling."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Error Handling")
    print("="*60)
    
    # Intentionally wrong credentials for demonstration
    WRONG_API_KEY = "wrong_key"
    WRONG_USERNAME = "wrong_user"
    WRONG_PASSWORD = "wrong_pass"
    
    try:
        # Try with wrong credentials
        print("🔐 Testing with wrong credentials...")
        manager = DemoAccountResetManager(WRONG_API_KEY, WRONG_USERNAME, WRONG_PASSWORD)
        
        success = manager.authenticate()
        if not success:
            print("❌ Authentication failed as expected with wrong credentials")
            
            # Now try with correct credentials (replace with your actual credentials)
            print("\n🔐 Now trying with correct credentials...")
            manager = DemoAccountResetManager(
                api_key="your_correct_api_key",
                username="your_correct_username", 
                password="your_correct_password"
            )
            
            if manager.authenticate():
                print("✅ Authentication successful with correct credentials")
            else:
                print("❌ Authentication still failed - check your credentials")
                
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_production_usage():
    """Example 5: Production-ready usage pattern."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Production Usage Pattern")
    print("="*60)
    
    def reset_demo_account_safe(api_key: str, username: str, password: str, 
                               account_id: str, template: str = "XAP100") -> bool:
        """
        Production-ready function to reset demo account.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Initialize manager with error handling
            manager = DemoAccountResetManager(api_key, username, password)
            
            # Authenticate with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if manager.authenticate():
                        break
                    else:
                        print(f"   Authentication attempt {attempt + 1} failed")
                        if attempt == max_retries - 1:
                            return False
                except Exception as e:
                    print(f"   Authentication error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        return False
            
            # Validate account exists before reset
            print(f"   Validating account {account_id}...")
            account_info = manager.get_account_info(account_id)
            if not account_info:
                print(f"   ❌ Account {account_id} not found or inaccessible")
                return False
            
            # Log current state
            print(f"   Current account state logged")
            
            # Perform reset
            print(f"   Resetting account with template {template}...")
            success = manager.reset_account(account_id, template)
            
            if success:
                print(f"   ✅ Account {account_id} reset successful")
                
                # Verify reset
                new_info = manager.get_account_info(account_id)
                if new_info and len(new_info['positions'].positions) == 0:
                    print(f"   ✅ Reset verification passed - no positions remaining")
                    return True
                else:
                    print(f"   ⚠️  Reset verification inconclusive")
                    return True
            else:
                print(f"   ❌ Account {account_id} reset failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Unexpected error during reset: {e}")
            return False
    
    # Example usage
    print("🔧 Production reset function example:")
    
    # Replace with your actual credentials
    API_KEY = "your_api_key"
    USERNAME = "your_username"
    PASSWORD = "your_password"
    ACCOUNT_ID = "your_account_id"
    
    print(f"   Resetting account {ACCOUNT_ID}...")
    success = reset_demo_account_safe(API_KEY, USERNAME, PASSWORD, ACCOUNT_ID, "XAP100")
    
    if success:
        print("   🎉 Production reset completed successfully")
    else:
        print("   ❌ Production reset failed")


def main():
    """Run all examples."""
    print("=" * 70)
    print("IRONBEAM DEMO ACCOUNT RESET - EXAMPLES")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n⚠️  IMPORTANT: Replace placeholder credentials with your actual credentials")
    print("   before running these examples!")
    
    # Uncomment the examples you want to run:
    
    # Example 1: Basic reset
    # example_basic_reset()
    
    # Example 2: Multiple accounts
    # example_multiple_accounts()
    
    # Example 3: Info only
    # example_account_info_only()
    
    # Example 4: Error handling
    example_with_error_handling()
    
    # Example 5: Production usage
    # example_production_usage()
    
    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETED")
    print("=" * 70)
    print("💡 Uncomment the examples in main() to run them with your credentials")


if __name__ == "__main__":
    main()