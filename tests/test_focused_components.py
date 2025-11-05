#!/usr/bin/env python3
"""
Focused test script for IronBeam trading components with real order IDs.
Tests update_order, AutoBreakevenManager, and RunningTPManager.
"""

import os
import sys
from unittest.mock import Mock, patch
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

from ironbeam import (
    IronBeam, OrderUpdateRequest, OrderResponse, OrderSide,
    PositionState, AutoBreakevenConfig, RunningTPConfig,
    BreakevenState
)
from ironbeam.trade_manager import AutoBreakevenManager, RunningTPManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_with_real_client():
    """Test with real IronBeam client using actual orders."""
    
    # Setup real client
    api_key = os.getenv('Demo_Key')
    username = os.getenv('Demo_Username')
    password = os.getenv('Demo_Password')
    
    if not all([api_key, username, password]):
        raise ValueError("Missing credentials in .env file")
    
    client = IronBeam(api_key=api_key, username=username, password=password, mode="demo")
    client.authenticate()
    
    # Get account info
    trader_info = client.get_trader_info()
    account_id = trader_info.accounts[0]
    logger.info(f"✅ Authenticated - Account: {account_id}")
    
    # Get existing orders to test with
    logger.info("\n🔍 Getting existing orders to test with...")
    orders_response = client.get_orders(account_id)
    
    if not orders_response.orders:
        logger.warning("⚠️  No existing orders found. Please place an order first to test update functionality.")
        return
    
    # Find a suitable order to test with
    test_order = None
    for order in orders_response.orders:
        if hasattr(order, 'order_id') and hasattr(order, 'status'):
            if order.status in ['PENDING', 'WORKING', 'OPEN']:
                test_order = order
                break
    
    if not test_order:
        logger.warning("⚠️  No suitable pending/working orders found for testing.")
        logger.info("📋 Available orders:")
        for order in orders_response.orders[:5]:  # Show first 5
            logger.info(f"   Order: {getattr(order, 'order_id', 'N/A')} | Status: {getattr(order, 'status', 'N/A')}")
        return
    
    logger.info(f"🎯 Using order for testing: {test_order.order_id} (Status: {test_order.status})")
    
    # Test 1: Update order with minimal change
    logger.info("\n📝 Test 1: Update Order Quantity")
    try:
        current_qty = getattr(test_order, 'quantity', 1)
        update_data = {
            "orderId": test_order.order_id,
            "quantity": current_qty  # Keep same quantity
        }
        
        logger.info(f"   Updating order {test_order.order_id} with data: {update_data}")
        response = client.update_order(account_id, test_order.order_id, update_data)
        logger.info(f"   ✅ SUCCESS: {response}")
        
    except Exception as e:
        logger.error(f"   ❌ FAILED: {e}")
        
        # If it fails, let's see the detailed error
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            logger.error(f"   API Response: {e.response.text}")

def test_with_mocked_client():
    """Test managers with mocked client for safe testing."""
    
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTING WITH MOCKED CLIENT")
    logger.info("="*60)
    
    # Create mock client
    mock_client = Mock(spec=IronBeam)
    account_id = "TEST_ACCOUNT"
    
    # Mock successful update response
    mock_response = OrderResponse(
        order_id="TEST_ORDER",
        status="UPDATED",
        filled_quantity=0,
        remaining_quantity=1,
        average_fill_price=0.0
    )
    mock_client.update_order.return_value = mock_response
    
    # Test AutoBreakevenManager
    logger.info("\n🔧 Testing AutoBreakevenManager")
    
    manager = AutoBreakevenManager(mock_client, account_id)
    
    # Create position
    position = PositionState(
        order_id="TEST_ORDER",
        account_id=account_id,
        symbol="XCME:MES.Z25",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_stop_loss=4980.0,
        current_take_profit=5020.0
    )
    
    # Create config with correct parameters
    config = AutoBreakevenConfig(
        enabled=True,
        trigger_levels=[15.0, 30.0, 45.0],  # ticks
        sl_offsets=[5.0, 15.0, 25.0],       # ticks  
        trigger_mode="ticks"
    )
    
    # Start monitoring
    manager.start_monitoring("TEST_ORDER", position, config)
    
    # Test scenarios
    test_prices = [
        (5010.0, False, "Below trigger"),
        (5015.0, True, "First trigger"),
        (5030.0, True, "Second trigger"),
        (5045.0, True, "Third trigger")
    ]
    
    for price, should_update, description in test_prices:
        logger.info(f"   Testing: {description} (Price: ${price})")
        was_updated = manager.check_and_update("TEST_ORDER", price)
        logger.info(f"   Result: Updated={was_updated}, Moves={position.breakeven_moves_completed}, SL=${position.current_stop_loss}")
        
        if was_updated == should_update:
            logger.info("   ✅ PASSED")
        else:
            logger.error(f"   ❌ FAILED: Expected {should_update}, got {was_updated}")
    
    # Test RunningTPManager
    logger.info("\n🔧 Testing RunningTPManager")
    
    tp_manager = RunningTPManager(mock_client, account_id)
    
    # Create new position for TP testing
    tp_position = PositionState(
        order_id="TP_TEST_ORDER",
        account_id=account_id,
        symbol="XCME:MES.Z25",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_stop_loss=4980.0,
        current_take_profit=5020.0
    )
    
    # Create config with correct parameters from the actual class definition
    tp_config = RunningTPConfig()
    tp_config.enable_trailing_extremes = True
    tp_config.enable_profit_levels = True
    tp_config.profit_level_triggers = [25.0, 50.0]  # ticks
    tp_config.extend_by_ticks = 20.0  # Extend TP by 20 ticks
    
    # Start monitoring
    tp_manager.start_monitoring("TP_TEST_ORDER", tp_position, tp_config)
    
    # Test scenarios
    tp_test_prices = [
        (5010.0, "Initial movement"),
        (5025.0, "First profit level"),
        (5035.0, "Higher high"),
        (5050.0, "Second profit level")
    ]
    
    for price, description in tp_test_prices:
        logger.info(f"   Testing: {description} (Price: ${price})")
        was_updated = tp_manager.check_and_update("TP_TEST_ORDER", price)
        logger.info(f"   Result: Updated={was_updated}, TP=${tp_position.current_take_profit}")
        logger.info(f"   High/Low: ${tp_position.highest_price}/${tp_position.lowest_price}")

def test_order_update_request_model():
    """Test the OrderUpdateRequest model."""
    
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTING OrderUpdateRequest Model")
    logger.info("="*60)
    
    # Test different ways to create OrderUpdateRequest
    test_cases = [
        {
            "name": "Stop Loss Update",
            "data": OrderUpdateRequest(
                order_id="TEST_001",
                stop_loss=4950.0,
                quantity=1
            )
        },
        {
            "name": "Take Profit Update", 
            "data": OrderUpdateRequest(
                order_id="TEST_002",
                take_profit=5050.0,
                quantity=1
            )
        },
        {
            "name": "Limit Price Update",
            "data": OrderUpdateRequest(
                order_id="TEST_003",
                limit_price=5000.0,
                quantity=2
            )
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n📝 Testing: {test_case['name']}")
        model = test_case['data']
        
        # Test model dump
        model_dict = model.model_dump(by_alias=True, exclude_none=True)
        logger.info(f"   Model dict: {model_dict}")
        
        # Verify required fields
        assert 'orderId' in model_dict, "orderId should be in model dict"
        logger.info("   ✅ Model validation passed")

def main():
    """Main test function."""
    
    print("\n" + "="*80)
    print("🧪 FOCUSED IRONBEAM TRADING COMPONENTS TEST")
    print("="*80)
    
    # Test 1: Model validation
    test_order_update_request_model()
    
    # Test 2: Mocked client tests (always safe to run)
    test_with_mocked_client()
    
    # Test 3: Real client tests (optional)
    use_real_client = input("\nTest with real IronBeam client using existing orders? (y/n): ").lower().strip() == 'y'
    
    if use_real_client:
        try:
            test_with_real_client()
        except Exception as e:
            logger.error(f"❌ Real client test failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        logger.info("⏭️  Skipping real client tests")
    
    logger.info("\n🎯 Test Summary:")
    logger.info("• OrderUpdateRequest model: ✅ Tested")
    logger.info("• AutoBreakevenManager: ✅ Tested with mocked data")
    logger.info("• RunningTPManager: ✅ Tested with mocked data")
    logger.info("• Real API calls: " + ("✅ Tested" if use_real_client else "⏭️ Skipped"))

if __name__ == "__main__":
    main()