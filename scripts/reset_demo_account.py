#!/usr/bin/env python3
"""
IronBeam Demo Account Reset Script

This script provides functionality to reset demo accounts using the IronBeam API.
It supports both the high-level IronBeam SDK and the low-level OpenAPI client.

Features:
- Reset demo account to initial state (clears positions, trades, and restores starting balance)
- Support for different account templates (XAP50, XAP100, XAP150)
- Comprehensive error handling and validation
- Account information display before and after reset
- Multiple authentication methods

Usage:
    python reset_demo_account.py --account-id 12345 --template XAP100
    python reset_demo_account.py --config config.ini
    python reset_demo_account.py --interactive

Requirements:
    - Valid IronBeam demo account credentials
    - Enterprise API access (for account reset functionality)
    - Python packages: requests, openapi-client (from python-client directory)
"""

import os
import sys
import argparse
import configparser
import getpass
from datetime import datetime
from typing import Optional, Dict, Any

# Add the python-client to the path so we can import the OpenAPI client
current_dir = os.path.dirname(os.path.abspath(__file__))
python_client_path = os.path.join(current_dir, 'python-client')
sys.path.insert(0, python_client_path)

try:
    # OpenAPI client imports
    import openapi_client
    from openapi_client.api.authorization_api import AuthorizationApi
    from openapi_client.api.account_api import AccountApi
    from openapi_client.api.simulated_trader_account_api import SimulatedTraderAccountApi
    from openapi_client.models.authorization_request import AuthorizationRequest
    from openapi_client.models.simulated_account_reset import SimulatedAccountReset
    from openapi_client.models.balance_type import BalanceType
    from openapi_client.exceptions import OpenApiException
    from openapi_client.api_client import ApiClient
    from openapi_client.configuration import Configuration
except ImportError as e:
    print(f"❌ Error importing OpenAPI client: {e}")
    print("Make sure the python-client directory exists and contains the generated client code.")
    sys.exit(1)

try:
    # High-level SDK import (optional)
    from ironbeam import IronBeam
    IRONBEAM_SDK_AVAILABLE = True
except ImportError:
    IRONBEAM_SDK_AVAILABLE = False
    print("⚠️  IronBeam SDK not available. Using OpenAPI client directly.")


class DemoAccountResetManager:
    """Manager class for resetting IronBeam demo accounts."""
    
    # Available account templates
    TEMPLATES = {
        'XAP50': 'Template with $50,000 starting balance',
        'XAP100': 'Template with $100,000 starting balance', 
        'XAP150': 'Template with $150,000 starting balance'
    }
    
    def __init__(self, api_key: str, username: str, password: str, base_url: str = None):
        """
        Initialize the reset manager.
        
        Args:
            api_key: IronBeam API key
            username: Account username
            password: Account password  
            base_url: API base URL (defaults to demo environment)
        """
        self.api_key = api_key
        self.username = username
        self.password = password
        self.base_url = base_url or "https://demo.ironbeamapi.com/v2"
        self.token = None
        self.account_id = None
        
        # Configure OpenAPI client
        self.configuration = Configuration()
        self.configuration.host = self.base_url
        self.api_client = ApiClient(self.configuration)
        
        # Initialize API instances
        self.auth_api = AuthorizationApi(self.api_client)
        self.account_api = AccountApi(self.api_client)
        self.sim_account_api = SimulatedTraderAccountApi(self.api_client)
    
    def authenticate(self) -> bool:
        """
        Authenticate with the IronBeam API.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            print("🔐 Authenticating with IronBeam API...")
            
            auth_request = AuthorizationRequest(
                username=self.username,
                password=self.password,
                apikey=self.api_key
            )
            
            response = self.auth_api.authorize(auth_request)
            
            # Check if response has token attribute
            if hasattr(response, 'token') and response.token:
                self.token = response.token
            else:
                print(f"❌ Authentication response missing token: {response}")
                return False
            
            # Configure authentication for future requests
            self.configuration.access_token = self.token
            
            print(f"✅ Authentication successful!")
            print(f"   Token: {self.token[:20]}...")
            return True
            
        except OpenApiException as e:
            print(f"❌ Authentication failed: {e}")
            if hasattr(e, 'body'):
                print(f"   Details: {e.body}")
            return False
        except Exception as e:
            print(f"❌ Unexpected authentication error: {e}")
            return False
    
    def get_account_info(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Get account information including balance and positions.
        
        Args:
            account_id: The account ID to query
            
        Returns:
            Dict containing account information or None if error
        """
        try:
            print(f"📊 Getting account information for {account_id}...")
            
            # Get account balance
            balance_response = self.account_api.account_balance(
                account_id=account_id,
                balance_type=BalanceType.CURRENT_OPEN
            )
            
            # Get positions
            positions_response = self.account_api.positions(account_id=account_id)
            
            # Get fills (recent trades)
            fills_response = self.account_api.fills(account_id=account_id)
            
            return {
                'balance': balance_response,
                'positions': positions_response,
                'fills': fills_response,
                'account_id': account_id
            }
            
        except OpenApiException as e:
            print(f"❌ Error getting account info: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error getting account info: {e}")
            return None
    
    def display_account_info(self, account_info: Dict[str, Any], title: str = "Account Information"):
        """
        Display formatted account information.
        
        Args:
            account_info: Account information dictionary
            title: Title for the display section
        """
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        
        if not account_info:
            print("❌ No account information available")
            return
        
        # Display balance information
        balance = account_info['balance']
        print(f"📊 Balance Information:")
        print(f"   Account ID: {account_info['account_id']}")
        print(f"   Status: {balance.status}")
        
        if balance.balances:
            for bal in balance.balances:
                print(f"\n   Currency: {bal.currency_code}")
                print(f"   Cash Balance: ${bal.cash_balance:,.2f}")
                print(f"   Open Trade Equity: ${bal.open_trade_equity:,.2f}")
                if hasattr(bal, 'unrealized_pl') and bal.unrealized_pl is not None:
                    print(f"   Unrealized P&L: ${bal.unrealized_pl:,.2f}")
                if hasattr(bal, 'available_for_trading') and bal.available_for_trading is not None:
                    print(f"   Available for Trading: ${bal.available_for_trading:,.2f}")
        
        # Display positions
        positions = account_info['positions']
        print(f"\n📈 Positions:")
        print(f"   Total Positions: {len(positions.positions)}")
        
        if positions.positions:
            for i, pos in enumerate(positions.positions[:5], 1):  # Show up to 5 positions
                print(f"\n   Position {i}:")
                print(f"     Symbol: {pos.exch_sym}")
                print(f"     Side: {pos.side}")
                print(f"     Quantity: {pos.quantity}")
                print(f"     Price: ${pos.price:,.2f}")
                if hasattr(pos, 'unrealized_pl') and pos.unrealized_pl is not None:
                    pnl_indicator = "📈" if pos.unrealized_pl >= 0 else "📉"
                    print(f"     Unrealized P&L: {pnl_indicator} ${pos.unrealized_pl:,.2f}")
        else:
            print("   No open positions")
        
        # Display recent fills
        fills = account_info['fills']
        print(f"\n📋 Recent Fills:")
        print(f"   Total Fills: {len(fills.fills)}")
        
        if fills.fills:
            print("\n   Latest 3 fills:")
            for i, fill in enumerate(fills.fills[:3], 1):
                print(f"     {i}. {fill.exch_sym} - {fill.side} {fill.quantity} @ ${fill.price:,.2f}")
        else:
            print("   No recent fills")
    
    def reset_account(self, account_id: str, template_id: str = "XAP100") -> bool:
        """
        Reset a demo account to its initial state.
        
        Args:
            account_id: The account ID to reset
            template_id: Template to use for reset (XAP50, XAP100, XAP150)
            
        Returns:
            bool: True if reset successful, False otherwise
        """
        try:
            if template_id not in self.TEMPLATES:
                print(f"❌ Invalid template ID: {template_id}")
                print(f"   Available templates: {', '.join(self.TEMPLATES.keys())}")
                return False
            
            print(f"🔄 Resetting account {account_id} with template {template_id}...")
            print(f"   Template: {self.TEMPLATES[template_id]}")
            
            # Create reset request
            reset_request = SimulatedAccountReset(
                account_id=account_id,
                template_id=template_id
            )
            
            # Perform the reset
            response = self.sim_account_api.simulated_account_reset(reset_request)
            
            print(f"✅ Account reset successful!")
            print(f"   Response: {response.message if hasattr(response, 'message') else 'Reset completed'}")
            return True
            
        except OpenApiException as e:
            print(f"❌ Account reset failed: {e}")
            if hasattr(e, 'body'):
                print(f"   Details: {e.body}")
            if hasattr(e, 'status'):
                if e.status == 403:
                    print("   💡 Tip: Account reset requires Enterprise API access")
                elif e.status == 401:
                    print("   💡 Tip: Check your authentication credentials")
            return False
        except Exception as e:
            print(f"❌ Unexpected reset error: {e}")
            return False
    
    def reset_with_confirmation(self, account_id: str, template_id: str = "XAP100") -> bool:
        """
        Reset account with user confirmation and before/after comparison.
        
        Args:
            account_id: The account ID to reset
            template_id: Template to use for reset
            
        Returns:
            bool: True if reset successful, False otherwise
        """
        print(f"\n🎯 Starting demo account reset process...")
        
        # Get account info before reset
        print("\n1️⃣ Getting account information before reset...")
        before_info = self.get_account_info(account_id)
        if before_info:
            self.display_account_info(before_info, "Account Status - BEFORE RESET")
        
        # Confirm reset
        print(f"\n⚠️  WARNING: This will reset account {account_id} to initial state!")
        print(f"   - All positions will be closed")
        print(f"   - All trade history will be cleared") 
        print(f"   - Balance will be reset to template default ({self.TEMPLATES.get(template_id, 'Unknown')})")
        
        confirm = input(f"\n❓ Are you sure you want to reset account {account_id}? (yes/no): ").lower()
        if confirm not in ['yes', 'y']:
            print("❌ Reset cancelled by user")
            return False
        
        # Perform reset
        print(f"\n2️⃣ Performing account reset...")
        success = self.reset_account(account_id, template_id)
        
        if not success:
            return False
        
        # Get account info after reset
        print(f"\n3️⃣ Getting account information after reset...")
        # Wait a moment for reset to propagate
        import time
        time.sleep(2)
        
        after_info = self.get_account_info(account_id)
        if after_info:
            self.display_account_info(after_info, "Account Status - AFTER RESET")
        
        print(f"\n✅ Demo account reset completed successfully!")
        print(f"   Account {account_id} has been reset to initial state")
        print(f"   Template: {template_id} - {self.TEMPLATES[template_id]}")
        
        return True


def load_config_file(config_path: str) -> Dict[str, str]:
    """
    Load configuration from INI file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict containing configuration values
    """
    config = configparser.ConfigParser()
    
    try:
        config.read(config_path)
        
        if 'ironbeam' not in config:
            raise ValueError("Missing [ironbeam] section in config file")
        
        section = config['ironbeam']
        return {
            'api_key': section.get('api_key'),
            'username': section.get('username'), 
            'password': section.get('password'),
            'base_url': section.get('base_url', 'https://demo.ironbeamapi.com/v2'),
            'account_id': section.get('account_id'),
            'template': section.get('template', 'XAP100')
        }
        
    except Exception as e:
        print(f"❌ Error loading config file: {e}")
        return {}


def interactive_mode() -> Dict[str, str]:
    """
    Interactive mode for entering credentials and account details.
    
    Returns:
        Dict containing user input
    """
    print("\n🔧 Interactive Configuration Mode")
    print("=" * 50)
    
    config = {}
    
    # Get API credentials
    config['api_key'] = input("Enter API Key: ").strip()
    config['username'] = input("Enter Username: ").strip()
    config['password'] = getpass.getpass("Enter Password: ").strip()
    
    # Get account details
    account_id_input = input("Enter Account ID to reset (or press Enter to use username): ").strip()
    config['account_id'] = account_id_input if account_id_input else config['username']
    
    # Choose template
    print("\nAvailable templates:")
    for template_id, description in DemoAccountResetManager.TEMPLATES.items():
        print(f"  {template_id}: {description}")
    
    template = input("Enter template ID (default: XAP100): ").strip() or "XAP100"
    config['template'] = template
    
    # Base URL (optional)
    base_url = input("Enter base URL (default: demo): ").strip()
    # Remove quotes if user added them
    base_url = base_url.strip('\'"')
    if not base_url:
        config['base_url'] = 'https://demo.ironbeamapi.com/v2'
    elif base_url.lower() == 'demo':
        config['base_url'] = 'https://demo.ironbeamapi.com/v2'
    elif base_url.lower() == 'live':
        config['base_url'] = 'https://api.ironbeamapi.com/v2'
    else:
        config['base_url'] = base_url
    
    return config


def environment_config() -> Dict[str, str]:
    """
    Load configuration from environment variables.
    
    Returns:
        Dict containing environment configuration
    """
    return {
        'api_key': os.getenv('IRONBEAM_API_KEY'),
        'username': os.getenv('IRONBEAM_USERNAME'),
        'password': os.getenv('IRONBEAM_PASSWORD'),
        'base_url': os.getenv('IRONBEAM_BASE_URL', 'https://demo.ironbeamapi.com/v2'),
        'account_id': os.getenv('IRONBEAM_ACCOUNT_ID'),
        'template': os.getenv('IRONBEAM_TEMPLATE', 'XAP100')
    }


def validate_config(config: Dict[str, str]) -> bool:
    """
    Validate configuration parameters.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        bool: True if configuration is valid
    """
    required_fields = ['api_key', 'username', 'password']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        print(f"❌ Missing required configuration: {', '.join(missing_fields)}")
        return False
    
    # If no account_id specified, use username (common for demo accounts)
    if not config.get('account_id'):
        config['account_id'] = config['username']
        print(f"💡 Using username as account ID: {config['account_id']}")
    
    if config.get('template') not in DemoAccountResetManager.TEMPLATES:
        print(f"❌ Invalid template: {config.get('template')}")
        print(f"   Available: {', '.join(DemoAccountResetManager.TEMPLATES.keys())}")
        return False
    
    return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Reset IronBeam demo account to initial state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Reset specific account with template
    %(prog)s --account-id 12345 --template XAP100
    
    # Use configuration file
    %(prog)s --config config.ini
    
    # Interactive mode
    %(prog)s --interactive
    
    # Use environment variables
    export IRONBEAM_API_KEY="your_key"
    export IRONBEAM_USERNAME="your_username" 
    export IRONBEAM_PASSWORD="your_password"
    export IRONBEAM_ACCOUNT_ID="12345"
    %(prog)s --env

Configuration file format (config.ini):
    [ironbeam]
    api_key = your_api_key
    username = your_username
    password = your_password
    account_id = 12345
    template = XAP100
    base_url = https://demo.ironbeamapi.com/v2
        """
    )
    
    # Configuration options
    config_group = parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument('--config', help='Configuration file path')
    config_group.add_argument('--interactive', action='store_true', help='Interactive configuration mode')
    config_group.add_argument('--env', action='store_true', help='Use environment variables')
    
    # Direct parameter options
    parser.add_argument('--account-id', help='Account ID to reset')
    parser.add_argument('--template', choices=list(DemoAccountResetManager.TEMPLATES.keys()),
                       default='XAP100', help='Account template to use')
    parser.add_argument('--api-key', help='IronBeam API key')
    parser.add_argument('--username', help='Account username')
    parser.add_argument('--password', help='Account password')
    parser.add_argument('--base-url', help='API base URL')
    
    # Options
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--info-only', action='store_true', help='Only show account info, do not reset')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("IRONBEAM DEMO ACCOUNT RESET TOOL")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load configuration
    config = {}
    
    if args.config:
        print(f"\n📁 Loading configuration from: {args.config}")
        config = load_config_file(args.config)
    elif args.interactive:
        config = interactive_mode()
    elif args.env:
        print(f"\n🌍 Loading configuration from environment variables")
        config = environment_config()
    
    # Override with command line arguments
    if args.account_id:
        config['account_id'] = args.account_id
    if args.template:
        config['template'] = args.template
    if args.api_key:
        config['api_key'] = args.api_key
    if args.username:
        config['username'] = args.username
    if args.password:
        config['password'] = args.password
    if args.base_url:
        config['base_url'] = args.base_url
    
    # Validate configuration
    if not validate_config(config):
        print("\n💡 Try running with --interactive for guided setup")
        sys.exit(1)
    
    # Initialize manager
    try:
        manager = DemoAccountResetManager(
            api_key=config['api_key'],
            username=config['username'], 
            password=config['password'],
            base_url=config['base_url']
        )
        
        # Authenticate
        if not manager.authenticate():
            sys.exit(1)
        
        # Info-only mode
        if args.info_only:
            print(f"\n📊 Account Information Only Mode")
            account_info = manager.get_account_info(config['account_id'])
            if account_info:
                manager.display_account_info(account_info)
            sys.exit(0)
        
        # Reset account
        if args.no_confirm:
            print(f"\n🔄 Performing account reset without confirmation...")
            success = manager.reset_account(config['account_id'], config['template'])
        else:
            success = manager.reset_with_confirmation(config['account_id'], config['template'])
        
        if success:
            print(f"\n🎉 Account reset completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Account reset failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()