#!/usr/bin/env python3
"""
Super Simple Demo Account Reset using High-Level Client

Uses the IronBeam high-level client from .env credentials.
"""

import os
import sys
from datetime import datetime

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("📁 Loaded .env file")
except ImportError:
    print("💡 python-dotenv not installed, using system environment variables")

# Import the high-level IronBeam client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ironbeam import IronBeam

def main():
    """Main function."""
    print("=" * 60)
    print("IRONBEAM DEMO ACCOUNT RESET (High-Level Client)")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get credentials from environment
    api_key = (os.getenv('IRONBEAM_API_KEY') or 
               os.getenv('Demo_Key', '').strip('\'"'))
    
    username = (os.getenv('IRONBEAM_USERNAME') or 
                os.getenv('Demo_Username'))
    
    password = (os.getenv('IRONBEAM_PASSWORD') or 
                os.getenv('Demo_Password', '').strip('\'"'))
    
    account_id = (os.getenv('IRONBEAM_ACCOUNT_ID') or username)
    template = os.getenv('IRONBEAM_TEMPLATE', 'XAP100')
    
    if not all([api_key, username, password]):
        print("❌ Missing credentials in environment variables!")
        return
    
    print(f"\n📋 Configuration:")
    print(f"   Account ID: {account_id}")
    print(f"   Template: {template}")
    print(f"   Username: {username}")
    print(f"   API Key: {api_key[:10]}...")
    
    try:
        # Initialize IronBeam client
        print(f"\n🔧 Initializing IronBeam client...")
        client = IronBeam(
            api_key=api_key,
            username=username,
            password=password,
            mode="demo"
        )
        
        # Authenticate
        print(f"🔐 Authenticating...")
        token = client.authenticate()
        print(f"✅ Authentication successful!")
        print(f"   Token: {client.token[:20]}...")
        
        # Get account balance before reset
        print(f"\n📊 Getting account information...")
        try:
            balance = client.get_account_balance(account_id)
            print(f"💰 Current Balance:")
            if balance.balances:
                bal = balance.balances[0]
                print(f"   Cash: ${bal.cash_balance:,.2f}")
                print(f"   Equity: ${bal.open_trade_equity:,.2f}")
        except Exception as e:
            print(f"⚠️  Could not get balance: {e}")
        
        # Get positions
        try:
            positions = client.get_positions(account_id)
            print(f"📋 Current Positions: {len(positions.positions)}")
            if positions.positions:
                for i, pos in enumerate(positions.positions[:3], 1):
                    print(f"   {i}. {pos.exch_sym} - {pos.side} {pos.quantity}")
        except Exception as e:
            print(f"⚠️  Could not get positions: {e}")
        
        # Confirm reset
        print(f"\n⚠️  This will reset account {account_id} with template {template}!")
        confirm = input("Continue with reset? (yes/no): ").lower()
        
        if confirm not in ['yes', 'y']:
            print("❌ Reset cancelled")
            return
        
        # Perform reset using the high-level client method
        print(f"\n🔄 Resetting account...")
        try:
            response = client.simulated_account_reset(account_id, template)
            print(f"✅ Account reset successful!")
            print(f"   Response: {response}")
            
            # Wait a moment and check updated status
            import time
            time.sleep(2)
            
            print(f"\n📊 Getting updated account information...")
            try:
                new_balance = client.get_account_balance(account_id)
                if new_balance.balances:
                    bal = new_balance.balances[0]
                    print(f"💰 New Balance:")
                    print(f"   Cash: ${bal.cash_balance:,.2f}")
                    print(f"   Equity: ${bal.open_trade_equity:,.2f}")
                
                new_positions = client.get_positions(account_id)
                print(f"📋 New Positions: {len(new_positions.positions)}")
                
            except Exception as e:
                print(f"⚠️  Could not get updated info: {e}")
            
            print(f"\n🎉 Demo account reset completed successfully!")
            
        except Exception as e:
            print(f"❌ Reset failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()