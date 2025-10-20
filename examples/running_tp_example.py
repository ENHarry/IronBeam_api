"""
Running Take Profit Example

Demonstrates how to use the RunningTPManager with multiple strategies:
1. Trailing extremes (highest high / lowest low)
2. Profit level triggers
3. Multiple adjustment modes (extend, trail, resistance/support)
"""

import asyncio
from ironbeam import (
    IronBeam,
    IronBeamStream,
    AsyncExecutor,
    RunningTPConfig,
    PositionState,
    OrderSide
)


async def main():
    # Initialize client
    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )

    # Authenticate
    client.authenticate()
    print(f"Authenticated: {client.token[:20]}...")

    account_id = "your_account_id"

    # Example 1: Trailing extremes with extend mode
    print("\n=== Example 1: Trailing Extremes ===")
    config_trailing = RunningTPConfig(
        enable_trailing_extremes=True,
        enable_profit_levels=False,
        extend_by_ticks=20,  # Extend TP by 20 ticks each time
        trailing_lookback_ticks=10,
        enabled=True
    )

    position = PositionState(
        order_id="12345",
        account_id=account_id,
        symbol="XCME:ES.Z24",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_take_profit=5050.0  # Initial TP
    )

    # Use AsyncExecutor for real-time WebSocket updates
    stream = IronBeamStream(client)
    executor = AsyncExecutor(client, account_id, stream)

    # Add position for running TP management
    await executor.add_running_tp(
        order_id=position.order_id,
        position=position,
        config=config_trailing
    )

    # Start the executor
    await executor.start()

    print(f"Monitoring {position.symbol} with trailing extremes...")
    print(f"Entry: {position.entry_price}, Initial TP: {position.current_take_profit}")
    print("TP will extend by 20 ticks as price makes new highs")

    try:
        # Run for 5 minutes
        await asyncio.sleep(300)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        await executor.stop()
        print("Executor stopped")


async def profit_levels_example():
    """Example using profit level triggers."""
    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )
    client.authenticate()

    # Trigger TP moves at specific profit levels
    config = RunningTPConfig(
        enable_trailing_extremes=False,
        enable_profit_levels=True,
        profit_level_triggers=[30, 60, 90],  # Move TP at +30, +60, +90 ticks profit
        profit_trigger_mode="ticks",
        extend_by_ticks=25,  # Extend TP by 25 ticks each trigger
        enabled=True
    )

    position = PositionState(
        order_id="12346",
        account_id="your_account_id",
        symbol="XCME:ES.Z24",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_take_profit=5050.0
    )

    executor = AsyncExecutor(client, "your_account_id")
    await executor.add_running_tp("12346", position, config)
    await executor.start()

    print("Running with profit level triggers...")
    print("TP will move when profit reaches 30, 60, and 90 ticks")

    try:
        await asyncio.sleep(300)
    except KeyboardInterrupt:
        pass
    finally:
        await executor.stop()


async def combined_modes_example():
    """Example combining multiple strategies and modes."""
    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )
    client.authenticate()

    # Use both trailing and profit levels, with multiple adjustment modes
    config = RunningTPConfig(
        # Enable both trigger conditions
        enable_trailing_extremes=True,
        enable_profit_levels=True,
        profit_level_triggers=[30, 60, 90],
        profit_trigger_mode="ticks",

        # Use multiple adjustment modes
        extend_by_ticks=20,          # Mode A: Extend by 20 ticks
        trail_offset_ticks=50,       # Mode B: Trail price by 50 ticks
        resistance_support_levels=[  # Mode C: Target these levels
            5050, 5100, 5150, 5200
        ],

        trailing_lookback_ticks=10,
        enabled=True
    )

    position = PositionState(
        order_id="12347",
        account_id="your_account_id",
        symbol="XCME:ES.Z24",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_take_profit=5050.0
    )

    executor = AsyncExecutor(client, "your_account_id")
    await executor.add_running_tp("12347", position, config)
    await executor.start()

    print("Running with combined strategies:")
    print("  - Trailing highest high")
    print("  - Profit level triggers at 30, 60, 90 ticks")
    print("  - TP adjustment: extend, trail, and resistance levels")

    try:
        await asyncio.sleep(300)
    except KeyboardInterrupt:
        pass
    finally:
        await executor.stop()


async def short_position_example():
    """Example for SHORT positions."""
    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )
    client.authenticate()

    # For SHORT positions, trail the lowest low
    config = RunningTPConfig(
        enable_trailing_extremes=True,
        trail_offset_ticks=50,  # Trail below price by 50 ticks
        enabled=True
    )

    position = PositionState(
        order_id="12348",
        account_id="your_account_id",
        symbol="XCME:ES.Z24",
        side=OrderSide.SELL,  # SHORT position
        entry_price=5000.0,
        quantity=1,
        current_take_profit=4950.0  # TP below entry for SHORT
    )

    executor = AsyncExecutor(client, "your_account_id")
    await executor.add_running_tp("12348", position, config)
    await executor.start()

    print("Running TP for SHORT position...")
    print("TP will trail downward as price makes new lows")

    try:
        await asyncio.sleep(300)
    except KeyboardInterrupt:
        pass
    finally:
        await executor.stop()


if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())

    # Or try other examples:
    # asyncio.run(profit_levels_example())
    # asyncio.run(combined_modes_example())
    # asyncio.run(short_position_example())
