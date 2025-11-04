# IronBeam Demo Account Reset Tool

A comprehensive Python script to reset IronBeam demo accounts to their initial state using the IronBeam API.

## Overview

This tool provides a safe and reliable way to reset demo trading accounts, clearing all positions, trades, and restoring the account balance to the template default. This is particularly useful for:

- Resetting demo accounts after testing strategies
- Cleaning up accounts for new simulations
- Restoring accounts to known starting states
- Educational and training purposes

## Features

- **Multiple Authentication Methods**: Support for config files, environment variables, and interactive input
- **Account Templates**: Support for different starting balance templates (XAP50, XAP100, XAP150)
- **Safety Features**: Confirmation prompts and before/after account state comparison
- **Comprehensive Error Handling**: Clear error messages and troubleshooting tips
- **Info-Only Mode**: View account information without performing reset
- **Enterprise API Support**: Works with Enterprise API accounts that have reset permissions

## Prerequisites

1. **IronBeam Demo Account**: Valid demo account credentials
2. **Enterprise API Access**: Account reset functionality requires Enterprise API permissions
3. **Python Environment**: Python 3.7+ with required packages
4. **Generated Client**: The `python-client` directory with OpenAPI generated code

## Installation

1. Ensure the `python-client` directory exists with the generated OpenAPI client code
2. Install any required dependencies (if using the high-level IronBeam SDK)

## Usage

### Method 1: Interactive Mode (Recommended for first-time users)

```bash
python reset_demo_account.py --interactive
```

This will prompt you for all required information step by step.

### Method 2: Configuration File

1. Copy the template configuration file:
```bash
cp config.ini.template config.ini
```

2. Edit `config.ini` with your credentials:
```ini
[ironbeam]
api_key = your_api_key_here
username = your_username
password = your_password
account_id = 12345
template = XAP100
base_url = https://demo.ironbeamapi.com/v2
```

3. Run the script:
```bash
python reset_demo_account.py --config config.ini
```

### Method 3: Environment Variables

Set environment variables:
```bash
export IRONBEAM_API_KEY="your_api_key"
export IRONBEAM_USERNAME="your_username"
export IRONBEAM_PASSWORD="your_password"
export IRONBEAM_ACCOUNT_ID="12345"
export IRONBEAM_TEMPLATE="XAP100"
```

Run the script:
```bash
python reset_demo_account.py --env
```

### Method 4: Command Line Arguments

```bash
python reset_demo_account.py --account-id 12345 --template XAP100 --api-key your_key --username your_user --password your_pass
```

## Account Templates

The script supports three account templates:

| Template | Starting Balance | Description |
|----------|------------------|-------------|
| XAP50    | $50,000         | Standard demo account |
| XAP100   | $100,000        | Enhanced demo account |
| XAP150   | $150,000        | Premium demo account |

## Command Line Options

```
usage: reset_demo_account.py [-h] (--config CONFIG | --interactive | --env)
                            [--account-id ACCOUNT_ID]
                            [--template {XAP50,XAP100,XAP150}]
                            [--api-key API_KEY] [--username USERNAME]
                            [--password PASSWORD] [--base-url BASE_URL]
                            [--no-confirm] [--info-only]

Reset IronBeam demo account to initial state

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Configuration file path
  --interactive         Interactive configuration mode
  --env                 Use environment variables
  --account-id ACCOUNT_ID
                        Account ID to reset
  --template {XAP50,XAP100,XAP150}
                        Account template to use
  --api-key API_KEY     IronBeam API key
  --username USERNAME   Account username
  --password PASSWORD   Account password
  --base-url BASE_URL   API base URL
  --no-confirm          Skip confirmation prompt
  --info-only           Only show account info, do not reset
```

## Examples

### View Account Information Only
```bash
python reset_demo_account.py --config config.ini --info-only
```

### Reset Without Confirmation (Dangerous!)
```bash
python reset_demo_account.py --config config.ini --no-confirm
```

### Reset with Specific Template
```bash
python reset_demo_account.py --interactive --template XAP150
```

## Safety Features

### Confirmation Prompt
The script will show account information before reset and ask for confirmation:

```
⚠️  WARNING: This will reset account 12345 to initial state!
   - All positions will be closed
   - All trade history will be cleared
   - Balance will be reset to template default (Template with $100,000 starting balance)

❓ Are you sure you want to reset account 12345? (yes/no):
```

### Before/After Comparison
The script displays account state before and after reset:

```
==============================================================
Account Status - BEFORE RESET
==============================================================
📊 Balance Information:
   Account ID: 12345
   Status: OK
   
   Currency: USD
   Cash Balance: $95,432.10
   Open Trade Equity: $95,432.10
   Unrealized P&L: -$4,567.90

📈 Positions:
   Total Positions: 3
   
   Position 1:
     Symbol: ES
     Side: LONG
     Quantity: 2
     Price: $4,234.50

==============================================================
Account Status - AFTER RESET
==============================================================
📊 Balance Information:
   Account ID: 12345
   Status: OK
   
   Currency: USD
   Cash Balance: $100,000.00
   Open Trade Equity: $100,000.00

📈 Positions:
   Total Positions: 0
   No open positions
```

## Error Handling

The script provides comprehensive error handling with clear messages:

### Authentication Errors
```
❌ Authentication failed: Unauthorized
   💡 Tip: Check your authentication credentials
```

### Permission Errors
```
❌ Account reset failed: 403 Forbidden
   💡 Tip: Account reset requires Enterprise API access
```

### Invalid Configuration
```
❌ Missing required configuration: api_key, account_id
```

## Security Best Practices

1. **Never commit credentials to version control**
2. **Use configuration files that are gitignored**
3. **Use environment variables in production**
4. **Regularly rotate API keys**
5. **Use demo environment for testing**

### Securing Configuration Files

Add to your `.gitignore`:
```
config.ini
*.env
.env
```

## API Endpoints Used

The script uses the following IronBeam API endpoints:

- `POST /auth` - Authentication
- `GET /account/{accountId}/balance` - Account balance
- `GET /account/{accountId}/positions` - Account positions  
- `GET /account/{accountId}/fills` - Account fills
- `PUT /simulatedAccountReset` - Reset demo account

## Troubleshooting

### Import Errors
```
❌ Error importing OpenAPI client: No module named 'openapi_client'
```
**Solution**: Ensure the `python-client` directory exists and contains the generated OpenAPI client code.

### Authentication Failures
```
❌ Authentication failed: Invalid credentials
```
**Solutions**:
- Verify your API key, username, and password
- Ensure you're using the correct environment (demo vs live)
- Check that your account has API access enabled

### Permission Denied
```
❌ Account reset failed: 403 Forbidden
```
**Solutions**:
- Ensure your account has Enterprise API access
- Verify you're using demo environment credentials
- Contact IronBeam support to enable account reset permissions

### Account Not Found
```
❌ Error getting account info: Account not found
```
**Solutions**:
- Verify the account ID is correct
- Ensure the account exists in the specified environment
- Check that the account belongs to your authenticated user

## Advanced Usage

### Batch Reset Multiple Accounts

Create a script to reset multiple accounts:

```python
from reset_demo_account import DemoAccountResetManager

# Initialize manager
manager = DemoAccountResetManager(api_key, username, password)
manager.authenticate()

# Reset multiple accounts
accounts = ['12345', '12346', '12347']
for account_id in accounts:
    print(f"Resetting account {account_id}...")
    manager.reset_account(account_id, 'XAP100')
```

### Automated Testing Integration

Use in automated testing workflows:

```python
def setup_test_account():
    """Reset demo account before each test."""
    manager = DemoAccountResetManager(api_key, username, password)
    manager.authenticate()
    manager.reset_account(test_account_id, 'XAP100')
```

## Contributing

To contribute to this tool:

1. Follow the existing code style and patterns
2. Add comprehensive error handling
3. Include docstrings for all functions
4. Test with multiple account types and scenarios
5. Update this README with any new features

## License

This tool is part of the IronBeam API SDK. See the main project LICENSE for details.

## Support

For issues with this tool:

1. Check the troubleshooting section above
2. Verify your API credentials and permissions
3. Review the IronBeam API documentation
4. Contact IronBeam support for account-specific issues

For Enterprise API access and account reset permissions, contact IronBeam support directly.