"""
Authentication Examples

Functions covered:
1. authenticate() - Get authentication token
2. logout() - Invalidate token

Learn how to:
- Basic authentication
- Handle authentication errors
- Token refresh patterns
- Secure credential storage
"""

from ironbeam import IronBeam, AuthenticationError
import os
from datetime import datetime, timedelta


# ============================================================================
# EXAMPLE 1: Basic Authentication
# ============================================================================

def basic_authentication():
    """Simple authentication example."""
    print("\n=== Example 1: Basic Authentication ===")

    # Initialize client
    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )

    # Authenticate
    try:
        token = client.authenticate()
        print(f"✅ Authentication successful!")
        print(f"Token: {token[:20]}...")  # Show first 20 chars
        print(f"Client ready to use")
        return client
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return None


# ============================================================================
# EXAMPLE 2: Authentication with Environment Variables
# ============================================================================

def auth_with_env_vars():
    """Secure authentication using environment variables."""
    print("\n=== Example 2: Authentication with Environment Variables ===")

    # Set up environment variables first (in your .env file or system):
    # export IRONBEAM_API_KEY="your_api_key"
    # export IRONBEAM_USERNAME="your_username"
    # export IRONBEAM_PASSWORD="your_password"

    api_key = os.getenv("IRONBEAM_API_KEY")
    username = os.getenv("IRONBEAM_USERNAME")
    password = os.getenv("IRONBEAM_PASSWORD")

    if not all([api_key, username, password]):
        print("❌ Missing environment variables!")
        print("Please set: IRONBEAM_API_KEY, IRONBEAM_USERNAME, IRONBEAM_PASSWORD")
        return None

    client = IronBeam(
        api_key=api_key,
        username=username,
        password=password
    )

    try:
        client.authenticate()
        print("✅ Authenticated using environment variables")
        return client
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ============================================================================
# EXAMPLE 3: Error Handling
# ============================================================================

def authentication_with_error_handling():
    """Comprehensive error handling for authentication."""
    print("\n=== Example 3: Authentication with Error Handling ===")

    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )

    try:
        print("Authenticating...")
        token = client.authenticate()
        print(f"✅ Success! Token received")
        print(f"   Length: {len(token)} characters")

        return client

    except AuthenticationError as e:
        print(f"❌ Authentication failed!")
        print(f"   Reason: {e}")
        print(f"   Solution: Check your API key, username, and password")
        return None

    except ConnectionError as e:
        print(f"❌ Connection failed!")
        print(f"   Reason: {e}")
        print(f"   Solution: Check your internet connection")
        return None

    except Exception as e:
        print(f"❌ Unexpected error!")
        print(f"   Error: {e}")
        print(f"   Type: {type(e).__name__}")
        return None


# ============================================================================
# EXAMPLE 4: Check if Authenticated
# ============================================================================

def check_authentication_status():
    """Check if client is authenticated."""
    print("\n=== Example 4: Check Authentication Status ===")

    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )

    # Before authentication
    print(f"Token before auth: {client.token}")

    # Authenticate
    client.authenticate()
    print(f"Token after auth: {client.token[:20] if client.token else 'None'}...")

    # Check if authenticated
    if client.token:
        print("✅ Client is authenticated")
    else:
        print("❌ Client is NOT authenticated")


# ============================================================================
# EXAMPLE 5: Logout
# ============================================================================

def logout_example():
    """Properly logout and invalidate token."""
    print("\n=== Example 5: Logout ===")

    # Authenticate
    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )
    client.authenticate()
    print(f"✅ Authenticated: {client.token[:20]}...")

    # Logout
    try:
        response = client.logout()
        print(f"✅ Logged out successfully")
        print(f"   Response: {response}")
        print(f"   Token after logout: {client.token}")
    except Exception as e:
        print(f"❌ Logout failed: {e}")


# ============================================================================
# EXAMPLE 6: Token Lifespan Tracking
# ============================================================================

class AuthenticatedClient:
    """Client wrapper with token expiration tracking."""

    def __init__(self, api_key, username, password):
        self.client = IronBeam(api_key, username, password)
        self.auth_time = None
        self.token_lifespan_hours = 24  # Adjust based on API

    def authenticate(self):
        """Authenticate and track auth time."""
        self.client.authenticate()
        self.auth_time = datetime.now()
        print(f"✅ Authenticated at {self.auth_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def is_token_valid(self):
        """Check if token is still valid."""
        if not self.auth_time:
            return False

        age = datetime.now() - self.auth_time
        max_age = timedelta(hours=self.token_lifespan_hours)

        is_valid = age < max_age
        remaining = max_age - age if is_valid else timedelta(0)

        print(f"Token age: {age}")
        print(f"Remaining: {remaining}")
        print(f"Valid: {is_valid}")

        return is_valid

    def ensure_authenticated(self):
        """Re-authenticate if token is expired."""
        if not self.is_token_valid():
            print("🔄 Token expired, re-authenticating...")
            self.authenticate()
        else:
            print("✅ Token still valid")


def token_lifespan_example():
    """Track token lifespan."""
    print("\n=== Example 6: Token Lifespan Tracking ===")

    wrapped_client = AuthenticatedClient(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )

    # Initial authentication
    wrapped_client.authenticate()

    # Check if valid
    wrapped_client.is_token_valid()

    # Ensure authenticated (will re-auth if needed)
    wrapped_client.ensure_authenticated()


# ============================================================================
# EXAMPLE 7: Multiple Account Management
# ============================================================================

def multiple_accounts():
    """Manage multiple accounts."""
    print("\n=== Example 7: Multiple Account Management ===")

    # Account 1: Live trading
    live_client = IronBeam(
        api_key="live_api_key",
        username="live_username",
        password="live_password"
    )
    live_client.base_url = "https://api.ironbeamapi.com/v2"  # Live URL

    # Account 2: Demo trading
    demo_client = IronBeam(
        api_key="demo_api_key",
        username="demo_username",
        password="demo_password"
    )
    demo_client.base_url = "https://demo.ironbeamapi.com/v2"  # Demo URL

    # Authenticate both
    try:
        live_client.authenticate()
        print("✅ Live account authenticated")
    except Exception as e:
        print(f"❌ Live account failed: {e}")

    try:
        demo_client.authenticate()
        print("✅ Demo account authenticated")
    except Exception as e:
        print(f"❌ Demo account failed: {e}")

    return live_client, demo_client


# ============================================================================
# EXAMPLE 8: Re-authentication Pattern
# ============================================================================

def safe_api_call(client, func, *args, **kwargs):
    """Safely call API function with auto re-authentication."""
    try:
        return func(*args, **kwargs)
    except AuthenticationError:
        print("🔄 Token expired, re-authenticating...")
        client.authenticate()
        return func(*args, **kwargs)


def reauth_pattern_example():
    """Automatic re-authentication on token expiry."""
    print("\n=== Example 8: Re-authentication Pattern ===")

    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )
    client.authenticate()

    # Use the safe API call wrapper
    try:
        # This will auto re-auth if token expired
        trader_info = safe_api_call(client, client.get_trader_info)
        print(f"✅ Got trader info: {trader_info}")
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# EXAMPLE 9: Credential Storage (Secure)
# ============================================================================

def secure_credential_storage():
    """
    Example of securely storing credentials.

    NEVER store credentials in code!
    Use one of these methods:

    1. Environment Variables (.env file)
    2. Configuration file (outside git)
    3. Secret management service (AWS Secrets Manager, etc.)
    4. OS keyring
    """
    print("\n=== Example 9: Secure Credential Storage ===")

    # Method 1: .env file (recommended for development)
    print("\n1. Using .env file:")
    print("   Create a .env file with:")
    print("   IRONBEAM_API_KEY=your_key")
    print("   IRONBEAM_USERNAME=your_username")
    print("   IRONBEAM_PASSWORD=your_password")
    print("")
    print("   Then load with: python-dotenv")
    print("   pip install python-dotenv")
    print("")
    print("   from dotenv import load_dotenv")
    print("   load_dotenv()")
    print("   api_key = os.getenv('IRONBEAM_API_KEY')")

    # Method 2: config.ini (not in git)
    print("\n2. Using config.ini:")
    print("   Create config.ini (add to .gitignore!):")
    print("   [ironbeam]")
    print("   api_key = your_key")
    print("   username = your_username")
    print("   password = your_password")
    print("")
    print("   import configparser")
    print("   config = configparser.ConfigParser()")
    print("   config.read('config.ini')")
    print("   api_key = config['ironbeam']['api_key']")

    # Method 3: OS keyring
    print("\n3. Using OS keyring:")
    print("   pip install keyring")
    print("   import keyring")
    print("   keyring.set_password('ironbeam', 'api_key', 'your_key')")
    print("   api_key = keyring.get_password('ironbeam', 'api_key')")


# ============================================================================
# EXAMPLE 10: Testing Authentication
# ============================================================================

def test_authentication():
    """Test authentication with different scenarios."""
    print("\n=== Example 10: Testing Authentication ===")

    test_cases = [
        {
            "name": "Valid credentials",
            "api_key": "valid_key",
            "username": "valid_user",
            "password": "valid_pass",
            "should_succeed": True
        },
        {
            "name": "Invalid API key",
            "api_key": "invalid_key",
            "username": "valid_user",
            "password": "valid_pass",
            "should_succeed": False
        },
        {
            "name": "Invalid password",
            "api_key": "valid_key",
            "username": "valid_user",
            "password": "wrong_pass",
            "should_succeed": False
        }
    ]

    for test in test_cases:
        print(f"\nTest: {test['name']}")
        client = IronBeam(
            api_key=test['api_key'],
            username=test['username'],
            password=test['password']
        )

        try:
            client.authenticate()
            result = "✅ SUCCESS"
        except Exception as e:
            result = f"❌ FAILED: {type(e).__name__}"

        expected = "✅ SUCCESS" if test['should_succeed'] else "❌ FAILED"
        status = "PASS" if (result.startswith("✅") == test['should_succeed']) else "FAIL"

        print(f"   Result: {result}")
        print(f"   Expected: {expected}")
        print(f"   Test: {status}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("IRONBEAM SDK - AUTHENTICATION EXAMPLES")
    print("=" * 70)

    # Run examples (comment out as needed)

    # Example 1: Basic authentication
    # client = basic_authentication()

    # Example 2: Environment variables
    # client = auth_with_env_vars()

    # Example 3: Error handling
    # client = authentication_with_error_handling()

    # Example 4: Check status
    # check_authentication_status()

    # Example 5: Logout
    # logout_example()

    # Example 6: Token lifespan
    # token_lifespan_example()

    # Example 7: Multiple accounts
    # live, demo = multiple_accounts()

    # Example 8: Re-auth pattern
    # reauth_pattern_example()

    # Example 9: Secure storage
    secure_credential_storage()

    # Example 10: Testing
    # test_authentication()

    print("\n" + "=" * 70)
    print("Done! See code for more examples.")
    print("=" * 70)
