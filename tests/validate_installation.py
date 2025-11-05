#!/usr/bin/env python3
"""
IronBeam SDK Installation Validation Test

This script tests that the IronBeam SDK was installed correctly and all
imports work as expected.
"""

import sys
import traceback

def test_import(module_name, items=None):
    """Test importing a module or specific items from a module."""
    try:
        if items:
            print(f"  Testing: from {module_name} import {', '.join(items)}")
            exec(f"from {module_name} import {', '.join(items)}")
        else:
            print(f"  Testing: import {module_name}")
            exec(f"import {module_name}")
        print("    ✅ SUCCESS")
        return True
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        traceback.print_exc()
        return False

def main():
    """Run installation validation tests."""
    print("🔍 IronBeam SDK Installation Validation")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # Test main package import
    print("\n1. Testing main package import...")
    total_tests += 1
    if test_import("ironbeam"):
        success_count += 1
    
    # Test core client import
    print("\n2. Testing core client imports...")
    total_tests += 1
    if test_import("ironbeam", ["IronBeam"]):
        success_count += 1
    
    # Test streaming imports
    print("\n3. Testing streaming imports...")
    total_tests += 1
    if test_import("ironbeam", ["IronBeamStream", "ConnectionState"]):
        success_count += 1
    
    # Test trade management imports
    print("\n4. Testing trade management imports...")
    total_tests += 1
    if test_import("ironbeam", [
        "AutoBreakevenManager", "RunningTPManager", 
        "AutoBreakevenConfig", "RunningTPConfig",
        "PositionState", "BreakevenState"
    ]):
        success_count += 1
    
    # Test execution engine imports
    print("\n5. Testing execution engine imports...")
    total_tests += 1
    if test_import("ironbeam", ["ThreadedExecutor", "AsyncExecutor"]):
        success_count += 1
    
    # Test model imports
    print("\n6. Testing data model imports...")
    total_tests += 1
    if test_import("ironbeam", [
        "OrderSide", "OrderType", "DurationType", "OrderStatus",
        "Quote", "Order", "Position", "Fill", "Balance"
    ]):
        success_count += 1
    
    # Test exception imports
    print("\n7. Testing exception imports...")
    total_tests += 1
    if test_import("ironbeam", [
        "APIError", "AuthenticationError", "InvalidRequestError",
        "RateLimitError", "ServerError", "StreamingError"
    ]):
        success_count += 1
    
    # Test creating client instance
    print("\n8. Testing client instantiation...")
    total_tests += 1
    try:
        from ironbeam import IronBeam
        client = IronBeam(
            api_key="test_key",
            username="test_user", 
            password="test_pass"
        )
        print("  Testing: IronBeam client creation")
        print("    ✅ SUCCESS - Client created without errors")
        success_count += 1
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        traceback.print_exc()
    
    # Test model creation with field compatibility
    print("\n9. Testing model field compatibility...")
    total_tests += 1
    try:
        from ironbeam import Quote
        
        # Test API format (abbreviated field names)
        api_quote = Quote(
            s="XCME:ES.Z24",
            b=5000.0,
            a=5000.25,
            bs=10,
            as_=5
        )
        
        # Test SDK format (full field names)
        sdk_quote = Quote(
            exch_sym="XCME:ES.Z24",
            bid_price=5000.0,
            ask_price=5000.25,
            bid_size=10,
            ask_size=5
        )
        
        # Verify both formats work and produce same result
        assert api_quote.exch_sym == sdk_quote.exch_sym == "XCME:ES.Z24"
        assert api_quote.bid_price == sdk_quote.bid_price == 5000.0
        assert api_quote.ask_price == sdk_quote.ask_price == 5000.25
        
        print("  Testing: Quote model field compatibility")
        print("    ✅ SUCCESS - Both API and SDK field formats work")
        success_count += 1
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        traceback.print_exc()
    
    # Test Pydantic v2 features
    print("\n10. Testing Pydantic v2 compatibility...")
    total_tests += 1
    try:
        from pydantic import __version__ as pydantic_version
        
        print(f"  Pydantic version: {pydantic_version}")
        
        # Verify Pydantic v2 is installed
        major_version = int(pydantic_version.split('.')[0])
        if major_version >= 2:
            print("  Testing: Pydantic v2 compatibility")
            print("    ✅ SUCCESS - Pydantic v2 is installed and working")
            success_count += 1
        else:
            print(f"    ❌ FAILED: Pydantic v{major_version} found, v2+ required")
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"✅ Successful tests: {success_count}/{total_tests}")
    print(f"❌ Failed tests: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ IronBeam SDK is properly installed and functional")
        print("\n📖 Next steps:")
        print("   1. Check examples/ directory for usage patterns")
        print("   2. Read docs/ directory for detailed documentation")
        print("   3. Set up your API credentials in .env file")
        print("   4. Start with examples/01_authentication_examples.py")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("❌ There may be issues with the installation")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure Python >= 3.7")
        print("   2. Ensure Pydantic >= 2.0")
        print("   3. Try: pip install --upgrade pydantic requests websockets")
        print("   4. Check for conflicting package versions")
        return 1

if __name__ == "__main__":
    sys.exit(main())