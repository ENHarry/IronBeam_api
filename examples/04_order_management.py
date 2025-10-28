"""
Example 4: Order Management
Demonstrates placing, updating, and cancelling various order types
"""
from ironbeam import IronBeam, OrderRequest, OrderUpdateRequest, OrderType, OrderSide, DurationType, OrderStatus
import time

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

# Test symbol
TEST_SYMBOL = "XCEC:MGC.Z25"  # Micro Gold


def setup_client():
    """Initialize and authenticate client."""
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    client.authenticate()
    trader_info = client.get_trader_info()
    return client, trader_info.accounts[0]


def get_reference_price(client):
    """Get current market price for calculations."""
    try:
        quotes = client.get_quotes([TEST_SYMBOL])
        if quotes.quotes and quotes.quotes[0].last_price:
            return quotes.quotes[0].last_price
    except:
        pass
    return 2700.0  # Default for MGC


def example_market_order(client, account_id):
    """Place a market order (executes immediately at current price)."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Market Order")
    print("="*70)

    print(f"\n  Placing MARKET BUY order for {TEST_SYMBOL}...")

    # Create market order
    order = OrderRequest(
        account_id=account_id,
        exch_sym=TEST_SYMBOL,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=1,
        duration=DurationType.DAY
    )

    try:
        response = client.place_order(account_id, order)

        print(f"  ✓ Market order placed!")
        print(f"    Order ID: {response.order_id}")
        if response.strategy_id:
            print(f"    Strategy ID: {response.strategy_id}")
        print(f"    Status: {response.status}")

        # Wait briefly for fill
        print(f"\n  Checking for fill...")
        time.sleep(2)

        positions = client.get_positions(account_id)
        for pos in positions.positions:
            if TEST_SYMBOL in pos.exch_sym:
                print(f"  ✓ Position opened: {pos.quantity} @ ${pos.price:,.2f}")

        return response.order_id

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def example_limit_order(client, account_id, ref_price):
    """Place a limit order (executes only at specified price or better)."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Limit Order")
    print("="*70)

    # Set limit price below current market (buy limit)
    limit_price = round(ref_price - 10, 2)

    print(f"\n  Placing LIMIT BUY order at ${limit_price:,.2f}")
    print(f"  (Current market: ~${ref_price:,.2f})")

    order = OrderRequest(
        account_id=account_id,
        exch_sym=TEST_SYMBOL,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=1,
        limit_price=limit_price,
        duration=DurationType.DAY
    )

    try:
        response = client.place_order(account_id, order)

        print(f"  ✓ Limit order placed!")
        print(f"    Order ID: {response.order_id}")
        print(f"    Limit Price: ${limit_price:,.2f}")
        print(f"    Status: {response.status}")
        print(f"\n  Note: Order will only execute if price reaches ${limit_price:,.2f}")

        return response.order_id

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def example_stop_order(client, account_id, ref_price):
    """Place a stop order (becomes market order when stop price is hit)."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Stop Order")
    print("="*70)

    # Set stop price above current market
    stop_price = round(ref_price + 15, 2)

    print(f"\n  Placing STOP BUY order at ${stop_price:,.2f}")
    print(f"  (Current market: ~${ref_price:,.2f})")

    order = OrderRequest(
        account_id=account_id,
        exch_sym=TEST_SYMBOL,
        side=OrderSide.BUY,
        order_type=OrderType.STOP,
        quantity=1,
        stop_price=stop_price,
        duration=DurationType.DAY
    )

    try:
        response = client.place_order(account_id, order)

        print(f"  ✓ Stop order placed!")
        print(f"    Order ID: {response.order_id}")
        print(f"    Stop Price: ${stop_price:,.2f}")
        print(f"    Status: {response.status}")
        print(f"\n  Note: Becomes market order if price reaches ${stop_price:,.2f}")

        return response.order_id

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def example_stop_limit_order(client, account_id, ref_price):
    """Place a stop-limit order (becomes limit order when stop price is hit)."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Stop-Limit Order")
    print("="*70)

    stop_price = round(ref_price + 20, 2)
    limit_price = round(stop_price + 5, 2)  # Limit 5 above stop

    print(f"\n  Placing STOP-LIMIT BUY order")
    print(f"    Stop Price: ${stop_price:,.2f}")
    print(f"    Limit Price: ${limit_price:,.2f}")
    print(f"    (Current market: ~${ref_price:,.2f})")

    order = OrderRequest(
        account_id=account_id,
        exch_sym=TEST_SYMBOL,
        side=OrderSide.BUY,
        order_type=OrderType.STOP_LIMIT,
        quantity=1,
        stop_price=stop_price,
        limit_price=limit_price,
        duration=DurationType.DAY
    )

    try:
        response = client.place_order(account_id, order)

        print(f"  ✓ Stop-limit order placed!")
        print(f"    Order ID: {response.order_id}")
        print(f"    Stop: ${stop_price:,.2f}, Limit: ${limit_price:,.2f}")
        print(f"\n  Note: Becomes limit order at ${limit_price:,.2f} when price hits ${stop_price:,.2f}")

        return response.order_id

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def example_bracket_order(client, account_id, ref_price):
    """Place a bracket order (entry with stop-loss and take-profit)."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Bracket Order")
    print("="*70)

    entry_price = round(ref_price - 5, 2)
    stop_loss = round(entry_price - 20, 2)
    take_profit = round(entry_price + 40, 2)

    print(f"\n  Placing BRACKET order:")
    print(f"    Entry (Limit): ${entry_price:,.2f}")
    print(f"    Stop Loss: ${stop_loss:,.2f}")
    print(f"    Take Profit: ${take_profit:,.2f}")
    print(f"    Risk/Reward: 1:2 ratio")

    order = OrderRequest(
        account_id=account_id,
        exch_sym=TEST_SYMBOL,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=1,
        limit_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        duration=DurationType.DAY
    )

    try:
        response = client.place_order(account_id, order)

        print(f"  ✓ Bracket order placed!")
        print(f"    Order ID: {response.order_id}")
        if response.strategy_id:
            print(f"    Strategy ID: {response.strategy_id}")
        print(f"\n  This creates 3 related orders:")
        print(f"    1. Entry limit buy @ ${entry_price:,.2f}")
        print(f"    2. Stop loss sell @ ${stop_loss:,.2f}")
        print(f"    3. Take profit sell @ ${take_profit:,.2f}")

        return response.order_id, response.strategy_id

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None, None


def example_update_order(client, account_id, order_id, ref_price):
    """Update an existing order."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Update Order")
    print("="*70)

    if not order_id:
        print("  No order to update")
        return

    new_limit = round(ref_price - 8, 2)

    print(f"\n  Updating order {order_id}")
    print(f"  New limit price: ${new_limit:,.2f}")

    update_req = OrderUpdateRequest(
        order_id=order_id,
        limit_price=new_limit
    )

    try:
        response = client.update_order(account_id, order_id, update_req)

        print(f"  ✓ Order updated!")
        print(f"    Status: {response.status}")
        if response.order_id:
            print(f"    Order ID: {response.order_id}")

    except Exception as e:
        print(f"  ✗ Error: {e}")


def example_cancel_order(client, account_id, order_id):
    """Cancel an order."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Cancel Order")
    print("="*70)

    if not order_id:
        print("  No order to cancel")
        return

    print(f"\n  Cancelling order {order_id}...")

    try:
        response = client.cancel_order(account_id, order_id)

        print(f"  ✓ Order cancelled!")
        print(f"    Status: {response.get('status', 'N/A')}")
        print(f"    Message: {response.get('message', 'N/A')}")

    except Exception as e:
        print(f"  ✗ Error: {e}")


def example_get_orders(client, account_id):
    """Retrieve and display working orders."""
    print("\n" + "="*70)
    print("EXAMPLE 8: Get Working Orders")
    print("="*70)

    print(f"\n  Retrieving all working orders...")

    try:
        orders = client.get_orders(account_id, OrderStatus.WORKING.value)

        print(f"  Status: {orders.status}")
        print(f"  Working Orders: {len(orders.orders)}")

        if orders.orders:
            # Filter for test symbol
            test_orders = [o for o in orders.orders if TEST_SYMBOL in o.exch_sym]

            if test_orders:
                print(f"\n  Orders for {TEST_SYMBOL}:")

                for order in test_orders:
                    print(f"\n    Order ID: {order.order_id}")
                    print(f"      Type: {order.order_type}")
                    print(f"      Side: {order.side}")
                    print(f"      Quantity: {order.quantity}")

                    if order.limit_price:
                        print(f"      Limit Price: ${order.limit_price:,.2f}")
                    if order.stop_price:
                        print(f"      Stop Price: ${order.stop_price:,.2f}")

                    print(f"      Status: {order.status}")
                    print(f"      Duration: {order.duration}")

        return [o.order_id for o in orders.orders if TEST_SYMBOL in o.exch_sym]

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []


def example_cancel_all_test_orders(client, account_id, order_ids):
    """Cancel all test orders."""
    print("\n" + "="*70)
    print("EXAMPLE 9: Cancel All Test Orders")
    print("="*70)

    if not order_ids:
        print("  No orders to cancel")
        return

    print(f"\n  Cancelling {len(order_ids)} orders...")

    cancelled = 0
    for order_id in order_ids:
        try:
            client.cancel_order(account_id, order_id)
            print(f"  ✓ Cancelled {order_id}")
            cancelled += 1
        except Exception as e:
            print(f"  ✗ Failed to cancel {order_id}: {e}")

    print(f"\n  ✓ Cancelled {cancelled}/{len(order_ids)} orders")


def main():
    """Run all order management examples."""
    print("\n" + "="*70)
    print("IRONBEAM SDK - ORDER MANAGEMENT EXAMPLES")
    print("="*70)
    print(f"Symbol: {TEST_SYMBOL}")

    # Setup
    client, account_id = setup_client()
    print(f"\n✓ Authenticated - Account: {account_id}")

    # Get reference price
    ref_price = get_reference_price(client)
    print(f"✓ Reference price: ${ref_price:,.2f}")

    # Track orders for cleanup
    test_order_ids = []

    # Run examples (skip market order to avoid fills)
    # example_market_order(client, account_id)  # Skipped - would execute

    limit_id = example_limit_order(client, account_id, ref_price)
    if limit_id:
        test_order_ids.append(limit_id)

    stop_id = example_stop_order(client, account_id, ref_price)
    if stop_id:
        test_order_ids.append(stop_id)

    stop_limit_id = example_stop_limit_order(client, account_id, ref_price)
    if stop_limit_id:
        test_order_ids.append(stop_limit_id)

    bracket_id, strategy_id = example_bracket_order(client, account_id, ref_price)
    if bracket_id:
        test_order_ids.append(bracket_id)

    # Update first order
    if test_order_ids:
        example_update_order(client, account_id, test_order_ids[0], ref_price)

    # Cancel one order
    if len(test_order_ids) > 1:
        example_cancel_order(client, account_id, test_order_ids[1])
        test_order_ids.remove(test_order_ids[1])

    # Get all working orders
    working_order_ids = example_get_orders(client, account_id)

    # Cancel all remaining test orders
    example_cancel_all_test_orders(client, account_id, working_order_ids)

    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Market orders execute immediately")
    print("  2. Limit orders execute at specified price or better")
    print("  3. Stop orders trigger market orders at stop price")
    print("  4. Stop-limit orders trigger limit orders at stop price")
    print("  5. Bracket orders include stop-loss and take-profit")
    print("  6. Orders can be updated and cancelled")
    print("  7. All order types use the same OrderRequest model")


if __name__ == "__main__":
    main()
