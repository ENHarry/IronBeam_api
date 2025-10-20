"""
Combined Strategy Example

Demonstrates using both Auto Breakeven and Running TP together
on the same position for comprehensive trade management.
"""

import asyncio
from ironbeam import (
    IronBeam,
    IronBeamStream,
    AsyncExecutor,
    AutoBreakevenConfig,
    RunningTPConfig,
    PositionState,
    OrderSide,
    OrderType,
    DurationType
)


async def full_trade_management_example():
    """
    Complete example: Place order, then manage with both auto breakeven and running TP.
    """
    # Initialize client
    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )

    # Authenticate
    client.authenticate()
    print(f"Authenticated successfully")

    account_id = "your_account_id"
    symbol = "XCME:ES.Z24"

    # Step 1: Place an order
    print(f"\n=== Placing Order ===")
    order_request = {
        "accountId": account_id,
        "exchSym": symbol,
        "side": "BUY",
        "quantity": 1,
        "orderType": "MARKET",
        "duration": "DAY",
        "stopLoss": 4980.0,    # Initial stop loss 20 ticks below
        "takeProfit": 5100.0,  # Initial take profit 100 ticks above
        "waitForOrderId": True
    }

    order_response = client.place_order(account_id, order_request)
    order_id = order_response.get('orderId')
    print(f"Order placed: {order_id}")

    # Wait for fill (in real scenario, you'd monitor order status)
    await asyncio.sleep(2)

    # Get current position info
    positions_response = client.get_positions(account_id)
    # Find our position (simplified - in production, match by order ID)
    entry_price = 5000.0  # Get from fill data in production

    # Step 2: Create position state
    position = PositionState(
        order_id=order_id,
        account_id=account_id,
        symbol=symbol,
        side=OrderSide.BUY,
        entry_price=entry_price,
        quantity=1,
        current_stop_loss=4980.0,
        current_take_profit=5100.0
    )

    # Step 3: Configure auto breakeven
    breakeven_config = AutoBreakevenConfig(
        trigger_mode="ticks",
        trigger_levels=[20, 40, 60],  # Move SL at +20, +40, +60
        sl_offsets=[10, 30, 50],      # To entry+10, entry+30, entry+50
        enabled=True
    )

    # Step 4: Configure running TP
    tp_config = RunningTPConfig(
        # Use both strategies
        enable_trailing_extremes=True,
        enable_profit_levels=True,
        profit_level_triggers=[30, 60, 90],

        # Multiple adjustment modes
        extend_by_ticks=20,
        trail_offset_ticks=50,
        resistance_support_levels=[5100, 5150, 5200, 5250],

        enabled=True
    )

    # Step 5: Set up async executor with WebSocket
    print(f"\n=== Starting Trade Management ===")
    stream = IronBeamStream(client)
    executor = AsyncExecutor(client, account_id, stream)

    # Add both managers
    await executor.add_auto_breakeven(order_id, position, breakeven_config)
    await executor.add_running_tp(order_id, position, tp_config)

    # Start execution
    await executor.start()

    print(f"\nManaging position {order_id} on {symbol}")
    print(f"Entry: {entry_price}")
    print(f"Initial SL: {position.current_stop_loss}")
    print(f"Initial TP: {position.current_take_profit}")
    print("\n--- Auto Breakeven Levels ---")
    print(f"  Move 1: Price @ {entry_price + 20} → SL to {entry_price + 10}")
    print(f"  Move 2: Price @ {entry_price + 40} → SL to {entry_price + 30}")
    print(f"  Move 3: Price @ {entry_price + 60} → SL to {entry_price + 50}")
    print("\n--- Running TP Strategy ---")
    print(f"  Trailing highest high with 50 tick offset")
    print(f"  Extending TP by 20 ticks at profit levels: 30, 60, 90")
    print(f"  Target resistance levels: {tp_config.resistance_support_levels}")
    print("\nMonitoring... (Press Ctrl+C to stop)")

    try:
        # Run indefinitely until stopped
        while True:
            await asyncio.sleep(1)

            # Optionally check position status periodically
            # positions = client.get_positions(account_id)
            # Update display, etc.

    except KeyboardInterrupt:
        print("\n\nStopping trade management...")

    finally:
        await executor.stop()
        print("Executor stopped")
        print(f"\nFinal position state:")
        print(f"  SL moves completed: {position.breakeven_moves_completed}")
        print(f"  Current SL: {position.current_stop_loss}")
        print(f"  TP moves completed: {position.tp_moves_completed}")
        print(f"  Current TP: {position.current_take_profit}")


async def multiple_positions_example():
    """
    Manage multiple positions simultaneously with different configs.
    """
    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )
    client.authenticate()

    account_id = "your_account_id"

    # Position 1: ES - Aggressive
    position1 = PositionState(
        order_id="order1",
        account_id=account_id,
        symbol="XCME:ES.Z24",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_stop_loss=4980.0,
        current_take_profit=5100.0
    )

    config1_be = AutoBreakevenConfig(
        trigger_levels=[10, 20, 30],  # Aggressive - quick breakeven
        sl_offsets=[5, 15, 25],
        enabled=True
    )

    config1_tp = RunningTPConfig(
        enable_trailing_extremes=True,
        trail_offset_ticks=30,  # Tight trail
        enabled=True
    )

    # Position 2: NQ - Conservative
    position2 = PositionState(
        order_id="order2",
        account_id=account_id,
        symbol="XCME:NQ.Z24",
        side=OrderSide.BUY,
        entry_price=15000.0,
        quantity=1,
        current_stop_loss=14900.0,
        current_take_profit=15200.0
    )

    config2_be = AutoBreakevenConfig(
        trigger_levels=[50, 100, 150],  # Conservative - wider levels
        sl_offsets=[25, 75, 125],
        enabled=True
    )

    config2_tp = RunningTPConfig(
        enable_profit_levels=True,
        profit_level_triggers=[100, 200, 300],
        extend_by_ticks=50,
        enabled=True
    )

    # Set up executor
    executor = AsyncExecutor(client, account_id)

    # Add both positions
    await executor.add_auto_breakeven("order1", position1, config1_be)
    await executor.add_running_tp("order1", position1, config1_tp)

    await executor.add_auto_breakeven("order2", position2, config2_be)
    await executor.add_running_tp("order2", position2, config2_tp)

    await executor.start()

    print("Managing 2 positions with different strategies:")
    print("\nES - Aggressive:")
    print("  Quick breakeven, tight trailing TP")
    print("\nNQ - Conservative:")
    print("  Wide breakeven levels, profit-based TP")

    try:
        await asyncio.sleep(600)  # Run for 10 minutes
    except KeyboardInterrupt:
        pass
    finally:
        await executor.stop()


async def comparison_threaded_vs_async():
    """
    Compare ThreadedExecutor vs AsyncExecutor performance.
    """
    from ironbeam import ThreadedExecutor

    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )
    client.authenticate()

    position = PositionState(
        order_id="test_order",
        account_id="your_account_id",
        symbol="XCME:ES.Z24",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1
    )

    config = AutoBreakevenConfig(
        trigger_levels=[20, 40, 60],
        sl_offsets=[10, 30, 50]
    )

    print("\n=== ThreadedExecutor (Polling) ===")
    print("Pros: Simple, works anywhere, lower resource usage")
    print("Cons: 1-2 second latency, polling overhead")

    threaded = ThreadedExecutor(client, "your_account_id", poll_interval=1.0)
    threaded.add_auto_breakeven("test_order", position, config)
    threaded.start()

    await asyncio.sleep(5)
    threaded.stop()

    print("\n=== AsyncExecutor (WebSocket) ===")
    print("Pros: Real-time, event-driven, low latency (<100ms)")
    print("Cons: More complex, requires WebSocket connection")

    async_exec = AsyncExecutor(client, "your_account_id")
    await async_exec.add_auto_breakeven("test_order", position, config)
    await async_exec.start()

    await asyncio.sleep(5)
    await async_exec.stop()

    print("\nRecommendation:")
    print("  - Use ThreadedExecutor for simple scenarios, development, testing")
    print("  - Use AsyncExecutor for production, scalping, high-frequency trading")


if __name__ == "__main__":
    # Run full trade management example
    asyncio.run(full_trade_management_example())

    # Or try other examples:
    # asyncio.run(multiple_positions_example())
    # asyncio.run(comparison_threaded_vs_async())
