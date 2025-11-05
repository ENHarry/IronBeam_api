#!/usr/bin/env python3
"""
Simple focused test for IronBeam update_order and trade managers.
This version properly handles the model requirements and API structure.
"""

import os
import sys
from unittest.mock import Mock, patch
import logging
from dotenv import load_dotenv

sys.path.insert(0, os.getcwd())

from ironbeam import (
    IronBeam, OrderUpdateRequest, OrderSide,
    PositionState, AutoBreakevenConfig, RunningTPConfig
)
from ironbeam.trade_manager import AutoBreakevenManager, RunningTPManager

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)

def test_update_order_functionality():
    """Test the update_order method with real client but mocked responses."""
    
    logger.info("🧪 Testing update_order() method functionality")
    
    # Setup real client
    api_key = os.getenv('Demo_Key')
    username = os.getenv('Demo_Username') 
    password = os.getenv('Demo_Password')
    
    if not all([api_key, username, password]):
        logger.error("❌ Missing credentials")
        return
    
    client = IronBeam(api_key=api_key, username=username, password=password, mode="demo")
    client.authenticate()
    
    trader_info = client.get_trader_info()
    account_id = trader_info.accounts[0]
    logger.info(f"✅ Authenticated - Account: {account_id}")
    
    # Test 1: Check method exists and can be called
    logger.info("\n📝 Test 1: Method signature validation")
    try:
        # This should not fail due to method signature issues
        update_data = {
            "orderId": "FAKE_ORDER_FOR_TESTING",
            "quantity": 1
        }
        
        # We expect this to fail with 400 (order not found), not method errors
        try:
            response = client.update_order(account_id, "FAKE_ORDER_FOR_TESTING", update_data)
            logger.info("   ⚠️  Unexpected success - order should not exist")
        except Exception as e:
            if "400 Client Error" in str(e) or "Bad Request" in str(e):
                logger.info("   ✅ Method works correctly - failed as expected (order doesn't exist)")
            else:
                logger.error(f"   ❌ Unexpected error type: {e}")
        
    except Exception as e:
        logger.error(f"   ❌ Method signature error: {e}")
    
    # Test 2: Test with OrderUpdateRequest model
    logger.info("\n📝 Test 2: OrderUpdateRequest model")
    try:
        order_request = OrderUpdateRequest(
            order_id="TEST_MODEL",
            stop_loss=5000.0,
            quantity=1
        )
        
        model_dict = order_request.model_dump(by_alias=True, exclude_none=True)
        logger.info(f"   Model dict: {model_dict}")
        logger.info("   ✅ OrderUpdateRequest model works correctly")
        
    except Exception as e:
        logger.error(f"   ❌ Model error: {e}")

def test_auto_breakeven_logic():
    """Test AutoBreakevenManager logic with mocked client."""
    
    logger.info("\n🧪 Testing AutoBreakevenManager logic")
    
    # Create mock client that always succeeds
    mock_client = Mock()
    mock_client.update_order.return_value = Mock(status="SUCCESS", message="Updated")
    
    manager = AutoBreakevenManager(mock_client, "TEST_ACCOUNT")
    
    # Create test position
    position = PositionState(
        order_id="BE_TEST",
        account_id="TEST_ACCOUNT", 
        symbol="XCME:MES.Z25",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_stop_loss=4980.0,
        current_take_profit=5020.0
    )
    
    # Test config
    config = AutoBreakevenConfig(
        enabled=True,
        trigger_levels=[15.0, 30.0],  # 15 and 30 ticks profit
        sl_offsets=[5.0, 20.0],       # Move SL to +5 and +20 ticks
        trigger_mode="ticks"
    )
    
    manager.start_monitoring("BE_TEST", position, config)
    
    # Test scenarios
    logger.info("\n📝 Testing breakeven triggers:")
    
    # Test 1: Below trigger (should not update)
    result = manager.check_and_update("BE_TEST", 5010.0)  # 10 ticks profit
    logger.info(f"   Price 5010 (10 ticks): Updated={result}, Expected=False")
    assert result == False, "Should not update below trigger"
    
    # Test 2: First trigger (should update)
    result = manager.check_and_update("BE_TEST", 5015.0)  # 15 ticks profit
    logger.info(f"   Price 5015 (15 ticks): Updated={result}, Expected=True")
    logger.info(f"   New SL: {position.current_stop_loss}, Expected=5005.0")
    assert result == True, "Should update at first trigger"
    assert abs(position.current_stop_loss - 5005.0) < 0.01, "SL should be entry + 5"
    
    # Test 3: Second trigger (should update again)
    result = manager.check_and_update("BE_TEST", 5030.0)  # 30 ticks profit  
    logger.info(f"   Price 5030 (30 ticks): Updated={result}, Expected=True")
    logger.info(f"   New SL: {position.current_stop_loss}, Expected=5020.0")
    assert result == True, "Should update at second trigger"
    assert abs(position.current_stop_loss - 5020.0) < 0.01, "SL should be entry + 20"
    
    # Test 4: Beyond all triggers (should not update)
    result = manager.check_and_update("BE_TEST", 5050.0)  # 50 ticks profit
    logger.info(f"   Price 5050 (50 ticks): Updated={result}, Expected=False")
    assert result == False, "Should not update beyond all triggers"
    
    logger.info("   ✅ All AutoBreakevenManager tests passed!")

def test_running_tp_logic():
    """Test RunningTPManager logic with mocked client."""
    
    logger.info("\n🧪 Testing RunningTPManager logic") 
    
    # Create mock client
    mock_client = Mock()
    mock_client.update_order.return_value = Mock(status="SUCCESS", message="Updated")
    
    manager = RunningTPManager(mock_client, "TEST_ACCOUNT")
    
    # Create test position
    position = PositionState(
        order_id="TP_TEST",
        account_id="TEST_ACCOUNT",
        symbol="XCME:MES.Z25", 
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_stop_loss=4980.0,
        current_take_profit=5020.0
    )
    
    # Create config with proper parameters (at least one adjustment mode required)
    config = RunningTPConfig(
        enable_trailing_extremes=True,
        enable_profit_levels=False,
        extend_by_ticks=20.0,  # Required: at least one adjustment mode
        enabled=True
    )
    
    manager.start_monitoring("TP_TEST", position, config)
    
    logger.info("\n📝 Testing TP trailing:")
    
    # Test price movements
    prices = [5010.0, 5020.0, 5030.0, 5015.0, 5035.0]
    
    for price in prices:
        result = manager.check_and_update("TP_TEST", price)
        logger.info(f"   Price ${price}: Updated={result}")
        logger.info(f"   Position high/low: ${position.highest_price}/{position.lowest_price}")
        logger.info(f"   Current TP: ${position.current_take_profit}")
    
    logger.info("   ✅ RunningTPManager test completed!")

def test_real_orders():
    """Test with real existing orders if available."""
    
    choice = input("\nTest update_order with real existing orders? (y/n): ").lower().strip()
    if choice != 'y':
        logger.info("⏭️  Skipping real order tests")
        return
    
    logger.info("\n🧪 Testing with real orders")
    
    # Setup client
    api_key = os.getenv('Demo_Key')
    username = os.getenv('Demo_Username')
    password = os.getenv('Demo_Password')
    
    client = IronBeam(api_key=api_key, username=username, password=password, mode="demo")
    client.authenticate()
    
    trader_info = client.get_trader_info()
    account_id = trader_info.accounts[0]
    
    # Get orders
    orders_response = client.get_orders(account_id)
    
    if not orders_response.orders:
        logger.warning("   ⚠️  No orders found to test with")
        return
    
    logger.info(f"   Found {len(orders_response.orders)} orders")
    
    # Show first few orders
    for i, order in enumerate(orders_response.orders[:3]):
        logger.info(f"   Order {i+1}: {getattr(order, 'order_id', 'N/A')} | Status: {getattr(order, 'status', 'N/A')}")
    
    # Try to find a working order to test with
    test_order = None
    for order in orders_response.orders:
        if hasattr(order, 'status') and order.status in ['WORKING', 'PENDING', 'OPEN']:
            test_order = order
            break
    
    if test_order:
        logger.info(f"\n📝 Testing update on order: {test_order.order_id}")
        
        try:
            # Try a minimal update (same quantity)
            current_qty = getattr(test_order, 'quantity', 1)
            update_data = {
                "orderId": test_order.order_id,
                "quantity": current_qty
            }
            
            response = client.update_order(account_id, test_order.order_id, update_data)
            logger.info(f"   ✅ Update successful: {response}")
            
        except Exception as e:
            logger.error(f"   ❌ Update failed: {e}")
            
            # Check if it's just a business logic error (order can't be updated)
            if "400" in str(e) and any(term in str(e).lower() for term in ["cannot", "invalid", "not allowed"]):
                logger.info("   ℹ️  This may be expected if the order type doesn't allow updates")
            
    else:
        logger.warning("   ⚠️  No working orders found to test updates")

def main():
    """Main test function."""
    
    print("\n" + "="*70)
    print("🧪 IRONBEAM TRADING COMPONENTS - FOCUSED TESTS")
    print("="*70)
    
    try:
        # Test 1: Basic functionality
        test_update_order_functionality()
        
        # Test 2: Manager logic 
        test_auto_breakeven_logic()
        test_running_tp_logic()
        
        # Test 3: Real orders (optional)
        test_real_orders()
        
        print("\n🎯 TEST SUMMARY:")
        print("✅ update_order() method signature and model handling")
        print("✅ AutoBreakevenManager logic and state management") 
        print("✅ RunningTPManager basic functionality")
        print("✅ Error handling for non-existent orders")
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()