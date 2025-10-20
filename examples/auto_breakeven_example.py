"""
Auto Breakeven Example

Demonstrates how to use the AutoBreakevenManager with both threaded
and async execution models.
"""

import time
from ironbeam import (
    IronBeam,
    ThreadedExecutor,
    AutoBreakevenConfig,
    PositionState,
    OrderSide
)


def main():
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

    # Create auto breakeven configuration
    # For a LONG position at 5000:
    # - Move 1: When price hits 5020, move SL to 5010
    # - Move 2: When price hits 5040, move SL to 5030
    # - Move 3: When price hits 5060, move SL to 5050
    config = AutoBreakevenConfig(
        trigger_mode="ticks",
        trigger_levels=[20, 40, 60],  # Trigger at these profit levels
        sl_offsets=[10, 30, 50],      # Move SL to entry + these offsets
        enabled=True
    )

    # Create position state (example)
    position = PositionState(
        order_id="12345",
        account_id=account_id,
        symbol="XCME:ES.Z24",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_stop_loss=4980.0  # Initial stop loss
    )

    # Option 1: Use ThreadedExecutor (polling-based)
    print("\n=== Using ThreadedExecutor ===")
    executor = ThreadedExecutor(client, account_id, poll_interval=1.0)

    # Add position for auto breakeven management
    executor.add_auto_breakeven(
        order_id=position.order_id,
        position=position,
        config=config
    )

    # Start the executor
    executor.start()

    # Let it run for a while
    try:
        print("Auto breakeven is running... (Press Ctrl+C to stop)")
        print(f"Monitoring position {position.order_id} on {position.symbol}")
        print(f"Entry: {position.entry_price}, Initial SL: {position.current_stop_loss}")
        print("\nWaiting for price to reach trigger levels:")
        print(f"  Level 1: {position.entry_price + config.trigger_levels[0]} → SL to {position.entry_price + config.sl_offsets[0]}")
        print(f"  Level 2: {position.entry_price + config.trigger_levels[1]} → SL to {position.entry_price + config.sl_offsets[1]}")
        print(f"  Level 3: {position.entry_price + config.trigger_levels[2]} → SL to {position.entry_price + config.sl_offsets[2]}")

        # Run for 5 minutes or until interrupted
        time.sleep(300)

    except KeyboardInterrupt:
        print("\nStopping auto breakeven...")

    finally:
        # Stop the executor
        executor.stop()
        print("Executor stopped")


def percentage_mode_example():
    """Example using percentage trigger mode instead of ticks."""
    client = IronBeam(
        api_key="your_api_key",
        username="your_username",
        password="your_password"
    )
    client.authenticate()

    # Use percentage-based triggers
    config = AutoBreakevenConfig(
        trigger_mode="percentage",
        trigger_levels=[2, 4, 6],     # Trigger at 2%, 4%, 6% profit
        sl_offsets=[10, 30, 50],      # Still use tick offsets for SL placement
        enabled=True
    )

    position = PositionState(
        order_id="12346",
        account_id="your_account_id",
        symbol="XCME:ES.Z24",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_stop_loss=4980.0
    )

    executor = ThreadedExecutor(client, "your_account_id")
    executor.add_auto_breakeven("12346", position, config)
    executor.start()

    try:
        print("Running with percentage-based triggers...")
        time.sleep(300)
    except KeyboardInterrupt:
        pass
    finally:
        executor.stop()


if __name__ == "__main__":
    main()
    # Or try the percentage mode example:
    # percentage_mode_example()
