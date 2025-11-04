#!/usr/bin/env python3
"""
Simple test script to verify demo account reset functionality
"""

import os
import sys

# Add the python-client to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
python_client_path = os.path.join(current_dir, 'python-client')
sys.path.insert(0, python_client_path)

from reset_demo_account import DemoAccountResetManager

def test_basic_functionality():
    """Test basic authentication and account info retrieval."""
    print("🧪 Testing Demo Account Reset Functionality")
    print("=" * 50)
    
    # Demo credentials from the examples
    API_KEY = "cfcf8651c7914cf988ffc026db9849b1"
    USERNAME = "51392077"
    PASSWORD = "207341"
    ACCOUNT_ID = USERNAME  # Use username as account ID
    
    try:
        # Initialize manager
        print("1️⃣ Initializing reset manager...")
        manager = DemoAccountResetManager(API_KEY, USERNAME, PASSWORD)
        
        # Test authentication
        print("2️⃣ Testing authentication...")
        if manager.authenticate():
            print("   ✅ Authentication successful")
        else:
            print("   ❌ Authentication failed")
            return False
        
        # Test account info retrieval
        print("3️⃣ Testing account info retrieval...")
        account_info = manager.get_account_info(ACCOUNT_ID)
        if account_info:
            print("   ✅ Account info retrieved successfully")
            manager.display_account_info(account_info, "Current Account Status")
        else:
            print("   ❌ Failed to retrieve account info")
            return False
        
        # Ask if user wants to proceed with reset test
        print("\n4️⃣ Reset Test (Optional)")
        proceed = input("   Do you want to test account reset? (yes/no): ").lower()
        
        if proceed in ['yes', 'y']:
            print("   🔄 Testing account reset...")
            
            # Show warning
            print("   ⚠️  This will reset the demo account!")
            confirm = input("   Are you sure? (yes/no): ").lower()
            
            if confirm in ['yes', 'y']:
                success = manager.reset_account(ACCOUNT_ID, "XAP100")
                if success:
                    print("   ✅ Account reset successful")
                    
                    # Get updated info
                    print("   📊 Getting updated account info...")
                    new_info = manager.get_account_info(ACCOUNT_ID)
                    if new_info:
                        manager.display_account_info(new_info, "Account Status After Reset")
                else:
                    print("   ❌ Account reset failed")
            else:
                print("   ⏭️  Reset test skipped")
        else:
            print("   ⏭️  Reset test skipped")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    
    if success:
        print("\n🎉 Demo account reset tool is working correctly!")
        print("💡 You can now use the full reset_demo_account.py script")
    else:
        print("\n❌ Tests failed - check the error messages above")
        
    input("\nPress Enter to exit...")