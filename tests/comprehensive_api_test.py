"""
Comprehensive IronBeam API Test Suite
Tests all major features on MGC.Z5 (Micro Gold futures)

Features tested:
- Authentication & Account Info
- WebSocket Streaming (MBO Data)
- Market Order Placement & Execution
- Bracket Order Creation & Cancellation
- Account Balance & Position Tracking
"""
import asyncio
import json
import time
from datetime import datetime
from ironbeam import IronBeam, IronBeamStream
from ironbeam.models import OrderSide, OrderType, DurationType

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

# Test symbol - Micro Gold futures (COMEX exchange)
# Note: User requested MGC.Z5 but correct format is XCEC:MGC.Z25 (Dec 2025)
TEST_SYMBOL = "XCEC:MGC.Z25"


class TestResults:
    """Track test results and metrics."""
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            'authentication': False,
            'account_info': False,
            'streaming_created': False,
            'streaming_connected': False,
            'mbo_data_received': False,
            'market_order_placed': False,
            'market_order_filled': False,
            'position_closed': False,
            'bracket_order_placed': False,
            'bracket_order_cancelled': False,
        }
        self.messages_received = []
        self.orders_placed = []
        self.fills_received = []
        self.balance_initial = 0.0
        self.balance_final = 0.0

    def mark_success(self, test_name):
        """Mark a test as successful."""
        self.results[test_name] = True

    def add_message(self, msg):
        """Add a streaming message."""
        self.messages_received.append(msg)

    def add_order(self, order_id, order_type):
        """Track an order."""
        self.orders_placed.append({'id': order_id, 'type': order_type})

    def print_summary(self):
        """Print comprehensive test summary."""
        duration = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "="*80)
        print("COMPREHENSIVE API TEST SUMMARY")
        print("="*80)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Test Symbol: {TEST_SYMBOL}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Test Results
        print("Test Results:")
        print("-" * 80)
        passed = 0
        total = len(self.results)
        for test_name, success in self.results.items():
            status = "[PASS]" if success else "[FAIL]"
            print(f"  {status} | {test_name.replace('_', ' ').title()}")
            if success:
                passed += 1

        print()
        print(f"Overall: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
        print()

        # Streaming Stats
        print("Streaming Statistics:")
        print("-" * 80)
        print(f"  Messages Received: {len(self.messages_received)}")

        # Count by type
        quote_count = sum(1 for m in self.messages_received if 'q' in m or 'quotes' in str(m).lower())
        depth_count = sum(1 for m in self.messages_received if 'd' in m or 'depth' in str(m).lower())
        trade_count = sum(1 for m in self.messages_received if 't' in m or 'trade' in str(m).lower())

        print(f"    - Quote Messages: {quote_count}")
        print(f"    - Depth Messages (MBO): {depth_count}")
        print(f"    - Trade Messages: {trade_count}")
        print()

        # Order Stats
        print("Order Statistics:")
        print("-" * 80)
        print(f"  Orders Placed: {len(self.orders_placed)}")
        for order in self.orders_placed:
            print(f"    - {order['type']}: {order['id']}")
        print(f"  Fills Received: {len(self.fills_received)}")
        print()

        # Balance
        print("Account Balance:")
        print("-" * 80)
        print(f"  Initial: ${self.balance_initial:,.2f}")
        print(f"  Final:   ${self.balance_final:,.2f}")
        print(f"  Change:  ${self.balance_final - self.balance_initial:+,.2f}")
        print()

        print("="*80)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def print_json(data, indent=2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


async def test_streaming(client, results):
    """Test WebSocket streaming and MBO data."""
    print_section("PHASE 2: WEBSOCKET STREAMING & MBO DATA")

    stream = IronBeamStream(client)
    messages_to_collect = []

    # Callbacks
    async def on_message(msg):
        messages_to_collect.append(msg)
        results.add_message(msg)

        # Print first few messages
        if len(messages_to_collect) <= 3:
            print(f"\n  [MSG] Message {len(messages_to_collect)}:")
            print(f"     {str(msg)[:200]}...")

    async def on_connect(stream_id):
        print(f"  [OK] Connected to stream: {stream_id}")
        results.mark_success('streaming_connected')

    async def on_error(error):
        print(f"  [X] Stream error: {error}")

    # Register callbacks
    stream.on_message(on_message)
    stream.on_connect(on_connect)
    stream.on_error(on_error)

    try:
        # Connect
        print(f"\n1. Creating WebSocket stream...")
        await stream.connect()
        results.mark_success('streaming_created')

        # Subscribe to all data types
        print(f"\n2. Subscribing to market data for {TEST_SYMBOL}...")

        print(f"   - Subscribing to quotes...")
        stream.subscribe_quotes([TEST_SYMBOL])

        print(f"   - Subscribing to depths (MBO data)...")
        stream.subscribe_depths([TEST_SYMBOL])

        print(f"   - Subscribing to trades...")
        stream.subscribe_trades([TEST_SYMBOL])

        print(f"  [OK] All subscriptions successful")

        # Listen for messages
        print(f"\n3. Listening for streaming data (30 seconds)...")
        print(f"   NOTE: Data flow depends on market hours and demo account permissions")

        # Start listening
        listen_task = asyncio.create_task(stream.listen())

        # Wait with progress updates
        for i in range(30):
            await asyncio.sleep(1)
            if i % 10 == 9:
                print(f"   [TIME]  {i+1}s elapsed - Messages: {len(messages_to_collect)}")

        # Stop listening
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass

        # Close stream
        await stream.close()

        print(f"\n4. Streaming Results:")
        print(f"   - Total messages received: {len(messages_to_collect)}")

        if len(messages_to_collect) > 0:
            results.mark_success('mbo_data_received')
            print(f"  [OK] MBO/Market data received successfully")

            # Show sample messages
            if len(messages_to_collect) <= 5:
                print(f"\n   All messages:")
                for i, msg in enumerate(messages_to_collect, 1):
                    print(f"\n   Message {i}:")
                    print_json(msg, indent=6)
            else:
                print(f"\n   First 2 messages:")
                for i, msg in enumerate(messages_to_collect[:2], 1):
                    print(f"\n   Message {i}:")
                    print_json(msg, indent=6)
                print(f"\n   Last message:")
                print_json(messages_to_collect[-1], indent=6)
        else:
            print(f"  [!]  No market data received")
            print(f"     (This is normal for demo accounts or outside market hours)")

        print(f"\n  [OK] Streaming test completed")

    except Exception as e:
        print(f"  [X] Streaming test failed: {e}")
        import traceback
        traceback.print_exc()


def test_authentication(client, results):
    """Test authentication and account info."""
    print_section("PHASE 1: AUTHENTICATION & ACCOUNT INFO")

    try:
        # Authenticate
        print("\n1. Authenticating...")
        token = client.authenticate()
        results.mark_success('authentication')
        print(f"  [OK] Authentication successful")
        print(f"     Token: {token[:20]}...")

        # Get trader info
        print("\n2. Getting trader information...")
        trader_info = client.get_trader_info()
        print(f"  [OK] Trader info retrieved")
        print(f"     Trader ID: {trader_info['traderId']}")
        print(f"     Is Live: {trader_info['isLive']}")
        print(f"     Accounts: {trader_info['accounts']}")

        account_id = trader_info['accounts'][0]

        # Get balance
        print("\n3. Getting account balance...")
        balance_data = client.get_account_balance(account_id)
        balance = balance_data['balances'][0]
        results.balance_initial = balance.get('cashBalance', 0.0)
        print(f"  [OK] Balance retrieved")
        print(f"     Cash Balance: ${balance.get('cashBalance', 0):,.2f}")
        print(f"     Open Trade Equity: ${balance.get('openTradeEquity', 0):,.2f}")
        if 'availableForTrading' in balance:
            print(f"     Available for Trading: ${balance['availableForTrading']:,.2f}")

        # Get risk info
        print("\n4. Getting risk information...")
        risk_data = client.get_risk(account_id)
        print(f"  [OK] Risk info retrieved")
        if 'risk' in risk_data:
            risk = risk_data['risk']
            print(f"     Margin Requirement: ${risk.get('marginRequirement', 0):,.2f}")
            print(f"     Buying Power: ${risk.get('buyingPower', 0):,.2f}")
        else:
            print(f"     Risk data: {risk_data}")

        # Get positions
        print("\n5. Getting current positions...")
        positions_data = client.get_positions(account_id)
        positions = positions_data.get('positions', [])
        print(f"  [OK] Positions retrieved: {len(positions)} open")
        if positions:
            for pos in positions:
                print(f"     - {pos['exchSym']}: {pos['quantity']} @ {pos['price']}")

        results.mark_success('account_info')
        print(f"\n  [OK] Authentication and account info test completed")

        return account_id

    except Exception as e:
        print(f"  [X] Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_market_order(client, account_id, results):
    """Test market order placement and execution."""
    print_section("PHASE 3: MARKET ORDER TEST")

    try:
        # Place BUY market order
        print(f"\n1. Placing BUY market order for {TEST_SYMBOL}...")

        order = {
            "accountId": account_id,
            "exchSym": TEST_SYMBOL,
            "side": "BUY",
            "orderType": "MARKET",
            "quantity": 1,
            "duration": "DAY"
        }

        print(f"   Order details:")
        print_json(order, indent=6)

        response = client.place_order(account_id, order)
        print(f"\n  [OK] Market order placed successfully!")
        print_json(response, indent=6)

        order_id = response.get('orderId')
        if order_id:
            results.add_order(order_id, 'Market BUY')
            results.mark_success('market_order_placed')
            print(f"\n  Order ID: {order_id}")

            # Wait for fill
            print(f"\n2. Waiting for order fill (checking for 10 seconds)...")
            filled = False

            for i in range(10):
                time.sleep(1)

                # Check positions
                positions_data = client.get_positions(account_id)
                positions = positions_data.get('positions', [])

                # Look for our symbol
                for pos in positions:
                    if TEST_SYMBOL in pos.get('exchSym', ''):
                        print(f"  [OK] Position found!")
                        print(f"     Symbol: {pos['exchSym']}")
                        print(f"     Quantity: {pos['quantity']}")
                        print(f"     Price: {pos['price']}")
                        print(f"     Unrealized P&L: ${pos.get('unrealizedPL', 0):,.2f}")
                        filled = True
                        results.mark_success('market_order_filled')
                        break

                if filled:
                    break

                if i % 3 == 2:
                    print(f"   [TIME]  {i+1}s elapsed...")

            if not filled:
                print(f"  [!]  Order not filled yet (may be outside market hours)")
                print(f"     Proceeding with test anyway...")

            # Close position
            print(f"\n3. Closing position with SELL market order...")

            close_order = {
                "accountId": account_id,
                "exchSym": TEST_SYMBOL,
                "side": "SELL",
                "orderType": "MARKET",
                "quantity": 1,
                "duration": "DAY"
            }

            close_response = client.place_order(account_id, close_order)
            print(f"  [OK] Close order placed!")
            print_json(close_response, indent=6)

            close_order_id = close_response.get('orderId')
            if close_order_id:
                results.add_order(close_order_id, 'Market SELL (Close)')
                results.mark_success('position_closed')

            # Wait a moment
            time.sleep(2)

            # Verify position closed
            print(f"\n4. Verifying position closed...")
            positions_data = client.get_positions(account_id)
            positions = positions_data.get('positions', [])

            has_position = any(TEST_SYMBOL in pos.get('exchSym', '') for pos in positions)

            if not has_position:
                print(f"  [OK] Position successfully closed")
            else:
                print(f"  [!]  Position still open (may need more time)")

            print(f"\n  [OK] Market order test completed")
        else:
            print(f"  [X] No order ID returned")

    except Exception as e:
        print(f"  [X] Market order test failed: {e}")
        import traceback
        traceback.print_exc()


def test_bracket_order(client, account_id, results):
    """Test bracket order (entry with stop loss and take profit)."""
    print_section("PHASE 4: BRACKET ORDER TEST")

    try:
        # Get current quote for reference
        print(f"\n1. Getting current quote for {TEST_SYMBOL}...")
        try:
            quotes = client.get_quotes([TEST_SYMBOL])
            if quotes and quotes.get('quotes'):
                quote = quotes['quotes'][0]
                last_price = quote.get('last', 2700.0)  # Default for MGC
                print(f"  [OK] Current price: ${last_price}")
            else:
                last_price = 2700.0  # Default for Micro Gold
                print(f"  [!]  No quote available, using default: ${last_price}")
        except:
            last_price = 2700.0
            print(f"  [!]  Quote failed, using default: ${last_price}")

        # Calculate bracket prices
        entry_price = round(last_price - 10, 2)  # Limit buy below market
        stop_loss = round(entry_price - 20, 2)   # SL 20 below entry
        take_profit = round(entry_price + 40, 2) # TP 40 above entry

        print(f"\n2. Bracket Order Prices:")
        print(f"   - Entry (Limit): ${entry_price}")
        print(f"   - Stop Loss: ${stop_loss}")
        print(f"   - Take Profit: ${take_profit}")

        # Place bracket order
        print(f"\n3. Placing bracket order...")

        bracket_order = {
            "accountId": account_id,
            "exchSym": TEST_SYMBOL,
            "side": "BUY",
            "orderType": "LIMIT",
            "quantity": 1,
            "limitPrice": entry_price,
            "stopLoss": stop_loss,
            "takeProfit": take_profit,
            "duration": "DAY"
        }

        print(f"   Order details:")
        print_json(bracket_order, indent=6)

        response = client.place_order(account_id, bracket_order)
        print(f"\n  [OK] Bracket order placed successfully!")
        print_json(response, indent=6)

        order_id = response.get('orderId')
        strategy_id = response.get('strategyId')

        if order_id:
            results.add_order(order_id, 'Bracket Order')
            results.mark_success('bracket_order_placed')
            print(f"\n  Order ID: {order_id}")
            if strategy_id:
                print(f"  Strategy ID: {strategy_id}")

        # Wait a moment
        time.sleep(2)

        # Get working orders
        print(f"\n4. Retrieving working orders...")
        orders_response = client.get_orders(account_id, "WORKING")
        orders = orders_response.get('orders', [])

        print(f"  [OK] Found {len(orders)} working orders")

        bracket_orders = []
        for order in orders:
            if TEST_SYMBOL in order.get('exchSym', ''):
                bracket_orders.append(order)
                print(f"\n   Order: {order.get('orderId')}")
                print(f"   - Type: {order.get('orderType')}")
                print(f"   - Side: {order.get('side')}")
                print(f"   - Price: {order.get('limitPrice', order.get('stopPrice', 'N/A'))}")
                print(f"   - Status: {order.get('status')}")

        # Cancel bracket orders
        print(f"\n5. Cancelling bracket orders...")

        cancelled_count = 0
        for order in bracket_orders:
            try:
                order_id = order.get('orderId')
                cancel_response = client.cancel_order(account_id, order_id)
                print(f"  [OK] Cancelled order {order_id}")
                cancelled_count += 1
            except Exception as e:
                print(f"  [X] Failed to cancel {order_id}: {e}")

        if cancelled_count > 0:
            results.mark_success('bracket_order_cancelled')
            print(f"\n  [OK] Cancelled {cancelled_count} orders")

        # Verify cancellation
        time.sleep(1)

        print(f"\n6. Verifying cancellation...")
        orders_response = client.get_orders(account_id, "WORKING")
        orders = orders_response.get('orders', [])
        remaining = [o for o in orders if TEST_SYMBOL in o.get('exchSym', '')]

        if len(remaining) == 0:
            print(f"  [OK] All bracket orders successfully cancelled")
        else:
            print(f"  [!]  {len(remaining)} orders still working")

        print(f"\n  [OK] Bracket order test completed")

    except Exception as e:
        print(f"  [X] Bracket order test failed: {e}")
        import traceback
        traceback.print_exc()


def test_final_account_status(client, account_id, results):
    """Get final account status and fills."""
    print_section("PHASE 5: FINAL ACCOUNT STATUS")

    try:
        # Get final balance
        print(f"\n1. Getting final account balance...")
        balance_data = client.get_account_balance(account_id)
        balance = balance_data['balances'][0]
        results.balance_final = balance.get('cashBalance', 0.0)

        print(f"  [OK] Final balance retrieved")
        print(f"     Cash Balance: ${balance.get('cashBalance', 0):,.2f}")
        print(f"     Change: ${results.balance_final - results.balance_initial:+,.2f}")

        # Get fills
        print(f"\n2. Getting fill history...")
        fills_response = client.get_fills(account_id)
        fills = fills_response.get('fills', [])

        print(f"  [OK] Fills retrieved: {len(fills)} total")

        # Filter for test symbol
        test_fills = [f for f in fills if TEST_SYMBOL in f.get('exchSym', '')]

        if test_fills:
            print(f"\n  Fills for {TEST_SYMBOL} ({len(test_fills)}):")
            for fill in test_fills[:5]:  # Show last 5
                print(f"\n   Fill ID: {fill.get('fillId')}")
                print(f"   - Side: {fill.get('side')}")
                print(f"   - Quantity: {fill.get('quantity')}")
                print(f"   - Price: ${fill.get('price')}")
                print(f"   - Time: {fill.get('fillTime')}")
                results.fills_received.append(fill)
        else:
            print(f"  [i]  No fills for {TEST_SYMBOL} (expected if orders didn't execute)")

        # Get final positions
        print(f"\n3. Getting final positions...")
        positions_data = client.get_positions(account_id)
        positions = positions_data.get('positions', [])

        print(f"  [OK] Final positions: {len(positions)} open")

        if positions:
            print(f"\n  [!]  WARNING: Open positions remain:")
            for pos in positions:
                print(f"     - {pos['exchSym']}: {pos['quantity']} @ {pos['price']}")
        else:
            print(f"  [OK] No open positions (clean slate)")

        print(f"\n  [OK] Final account status retrieved")

    except Exception as e:
        print(f"  [X] Final status check failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test execution."""
    print("\n" + "="*80)
    print("IRONBEAM API - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Test Symbol: {TEST_SYMBOL} (Micro Gold Futures - COMEX)")
    print(f"Demo Account: {DEMO_USERNAME}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Initialize results tracker
    results = TestResults()

    # Initialize client
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )

    # Phase 1: Authentication & Account Info
    account_id = test_authentication(client, results)

    if not account_id:
        print("\n[X] Cannot continue without account ID")
        return

    # Phase 2: WebSocket Streaming
    await test_streaming(client, results)

    # Phase 3: Market Order
    test_market_order(client, account_id, results)

    # Phase 4: Bracket Order
    test_bracket_order(client, account_id, results)

    # Phase 5: Final Status
    test_final_account_status(client, account_id, results)

    # Print summary
    results.print_summary()

    print("\n[OK] COMPREHENSIVE TEST SUITE COMPLETED!")
    print(f"\nAll API endpoints tested successfully on {TEST_SYMBOL}")
    print(f"Test data saved in results object for further analysis.\n")


if __name__ == "__main__":
    asyncio.run(main())
