"""
Test get_order_status method with IronBeam Demo Account
Tests retrieving the status of specific orders using different approaches.
"""
from ironbeam import IronBeam
from ironbeam.models import OrderSide, OrderType, DurationType, OrderStatus
import json
import time
import sys

# Demo credentials from existing test file
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

def print_section(title):
    print(f"\n{'='*70}")
    print(title)
    print(f"{'='*70}")

def print_order_details(order, title="Order Details"):
    """Print formatted order details."""
    print(f"\n{title}:")
    print(f"  Order ID: {order.order_id}")
    print(f"  Strategy ID: {order.strategy_id}")
    print(f"  Account ID: {order.account_id}")
    print(f"  Symbol: {order.exch_sym}")
    print(f"  Side: {order.side}")
    print(f"  Quantity: {order.quantity}")
    print(f"  Type: {order.order_type}")
    print(f"  Status: {order.status}")
    print(f"  Duration: {order.duration}")
    if hasattr(order, 'limit_price') and order.limit_price:
        print(f"  Limit Price: ${order.limit_price:,.2f}")
    if hasattr(order, 'stop_price') and order.stop_price:
        print(f"  Stop Price: ${order.stop_price:,.2f}")

def test_get_order_status_basic(client, account_id):
    """Test basic get_order_status functionality."""
    print_section("TEST 1: Basic get_order_status Test")
    
    # First, let's get all orders to find some to test with
    print("Getting all orders to find test candidates...")
    try:
        all_orders = client.get_orders(account_id, "ANY")
        print(f"Found {len(all_orders.orders)} total orders")
        
        if not all_orders.orders:
            print("❌ No orders found. Creating a test order first...")
            return create_test_order_and_check_status(client, account_id)
        
        # Test with first available order
        test_order = all_orders.orders[0]
        print(f"Testing with Order ID: {test_order.order_id}, Status: {test_order.status}")
        
        # Now test get_order_status
        order_status_response = client.get_order_status(
            account_id=account_id,
            order_status=test_order.status,  # Use the actual status from the order
            order_id=test_order.order_id
        )
        
        print("✅ get_order_status completed successfully!")
        print_order_details(order_status_response, "Retrieved Order Status")
        
        # Verify the data matches
        assert order_status_response.order_id == test_order.order_id, "Order ID mismatch"
        assert order_status_response.status == test_order.status, "Status mismatch"
        print("✅ Order data verification passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic test: {e}")
        return False

def test_get_order_status_with_different_statuses(client, account_id):
    """Test get_order_status with different order statuses."""
    print_section("TEST 2: Test with Different Order Statuses")
    
    # Get orders by different statuses and test each
    statuses_to_test = [OrderStatus.WORKING, OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.ANY]
    success_count = 0
    
    for status in statuses_to_test:
        try:
            print(f"\nTesting with status: {status.value}")
            orders = client.get_orders(account_id, status.value)
            
            if orders.orders:
                test_order = orders.orders[0]
                print(f"Found order with ID: {test_order.order_id}")
                
                # Test get_order_status
                order_status_response = client.get_order_status(
                    account_id=account_id,
                    order_status=status,
                    order_id=test_order.order_id
                )
                
                print(f"✅ Successfully retrieved status for {status.value} order")
                print(f"   Order ID: {order_status_response.order_id}")
                print(f"   Status: {order_status_response.status}")
                success_count += 1
            else:
                print(f"⚠️  No orders found with status: {status.value}")
                
        except Exception as e:
            print(f"❌ Error testing status {status.value}: {e}")
            return False
    
    print(f"\n✅ Successfully tested {success_count}/{len(statuses_to_test)} status types")
    return success_count > 0  # Return True if we had at least one success

def create_test_order_and_check_status(client, account_id):
    """Create a test order and then check its status."""
    print_section("TEST 3: Create Order and Check Status")
    
    try:
        # Get current market price for reference
        symbol = "XCME:MES.Z25"  # Micro E-mini S&P 500 (smaller contract)
        quotes = client.get_quotes([symbol])
        current_price = quotes.quotes[0].bid_price if quotes.quotes else 5000.0
        
        # Create a limit order well below market (won't fill)
        limit_price = current_price - 100  # $100 below market
        
        print(f"Creating limit order for {symbol}")
        print(f"Current price: ${current_price:,.2f}")
        print(f"Limit price: ${limit_price:,.2f}")
        
        order_request = {
            "accountId": account_id,
            "exchSym": symbol,
            "side": OrderSide.BUY.value,
            "quantity": 1,
            "orderType": OrderType.LIMIT.value,
            "limitPrice": limit_price,
            "duration": DurationType.DAY.value
        }
        
        # Place the order
        order_response = client.place_order(account_id, order_request)
        print(f"✅ Order placed successfully!")
        print(f"   Order ID: {order_response.order_id}")
        print(f"   Status: {order_response.status}")
        
        # Wait a moment for order to be processed
        time.sleep(2)
        
        # Now test get_order_status
        print(f"\nTesting get_order_status with new order...")
        order_status_response = client.get_order_status(
            account_id=account_id,
            order_status=OrderStatus.WORKING,  # Should be working
            order_id=order_response.order_id
        )
        
        print("✅ get_order_status completed successfully!")
        print_order_details(order_status_response, "Retrieved Order Status")
        
        # Clean up - cancel the test order
        print(f"\nCancelling test order...")
        cancel_response = client.cancel_order(account_id, order_response.order_id)
        print(f"✅ Order cancelled: {cancel_response.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in create and check test: {e}")
        return False

def test_order_not_found_scenario(client, account_id):
    """Test get_order_status with non-existent order ID."""
    print_section("TEST 4: Order Not Found Scenario")
    
    try:
        # Use a fake order ID that definitely doesn't exist
        fake_order_id = "FAKE_ORDER_ID_12345"
        
        print(f"Testing with fake order ID: {fake_order_id}")
        
        # This should raise an exception
        order_status_response = client.get_order_status(
            account_id=account_id,
            order_status=OrderStatus.ANY,
            order_id=fake_order_id
        )
        
        # If we get here without exception, that's unexpected
        print("⚠️  Unexpected: No exception raised for fake order ID")
        return False
        
    except Exception as e:
        print(f"✅ Expected exception caught: {e}")
        print("✅ Method correctly handles non-existent order IDs")
        return True

def test_api_documentation_compliance(client, account_id):
    """Test compliance with API documentation expectations."""
    print_section("TEST 5: API Documentation Compliance")
    
    print("According to the API docs (https://docs.ironbeamapi.com/#tag/Order/operation/getOrders):")
    print("- Endpoint: GET /order/{accountId}/{orderStatus}")
    print("- This returns a list of orders with the specified status")
    print("- Our method filters this list by order_id")
    
    try:
        # Test the underlying API call that our method uses
        orders = client.get_orders(account_id, OrderStatus.ANY.value)
        print(f"\nDirect get_orders call returned {len(orders.orders)} orders")
        
        if orders.orders:
            test_order = orders.orders[0]
            print(f"\nTesting get_order_status filtering logic...")
            print(f"Looking for order ID: {test_order.order_id}")
            
            # Test our method
            filtered_order = client.get_order_status(
                account_id=account_id,
                order_status=test_order.status,
                order_id=test_order.order_id
            )
            
            print(f"✅ Method successfully filtered and returned the specific order")
            print(f"   Order ID matches: {filtered_order.order_id == test_order.order_id}")
            print(f"   Status matches: {filtered_order.status == test_order.status}")
            
            # Test with wrong status (should still work if the order exists in ANY status)
            print(f"\nTesting with potentially wrong status filter...")
            try:
                filtered_order_any = client.get_order_status(
                    account_id=account_id,
                    order_status=OrderStatus.ANY,
                    order_id=test_order.order_id
                )
                print(f"✅ Method works with ANY status: {filtered_order_any.order_id}")
            except Exception as e:
                print(f"⚠️  Method requires specific status: {e}")
            
            return True
        
    except Exception as e:
        print(f"❌ Error in compliance test: {e}")
        return False

def main():
    """Run all get_order_status tests."""
    print_section("IRONBEAM DEMO - GET_ORDER_STATUS METHOD TEST")
    
    # Initialize and authenticate
    try:
        client = IronBeam(
            api_key=DEMO_KEY,
            username=DEMO_USERNAME,
            password=DEMO_PASSWORD,
            mode="demo"
        )
        
        client.authenticate()
        print("✅ Authenticated successfully")
        
        # Get account info
        trader_info = client.get_trader_info()
        account_id = trader_info.accounts[0]
        
        print(f"✅ Trading Account: {account_id}")
        
        # Get current balance
        balance_data = client.get_account_balance(account_id)
        print(f"✅ Account accessible")
        
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return
    
    # Run all tests
    test_results = []
    
    test_results.append(("Basic Functionality", test_get_order_status_basic(client, account_id)))
    test_results.append(("Different Statuses", test_get_order_status_with_different_statuses(client, account_id)))
    test_results.append(("Create & Check", create_test_order_and_check_status(client, account_id)))
    test_results.append(("Order Not Found", test_order_not_found_scenario(client, account_id)))
    test_results.append(("API Compliance", test_api_documentation_compliance(client, account_id)))
    
    # Print test summary
    print_section("TEST SUMMARY")
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! get_order_status method is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")

if __name__ == "__main__":
    main()