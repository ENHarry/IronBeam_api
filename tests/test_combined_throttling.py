#!/usr/bin/env python3
"""
Test both AutoBreakevenManager and RunningTPManager with throttling functionality.
"""

import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from ironbeam.trade_manager import AutoBreakevenManager, RunningTPManager, PositionState, AutoBreakevenConfig, RunningTPConfig
from ironbeam.models import OrderSide

def test_both_managers():
    """Test throttling on both trade managers."""
    
    # Mock client that tracks update calls
    class MockClient:
        def __init__(self):
            self.update_calls = []
            
        def update_order(self, account_id, order_id, update_request):
            self.update_calls.append({
                'timestamp': time.time(),
                'order_id': order_id,
                'stop_loss': update_request.get('stopLoss', 0),
                'manager_type': 'breakeven' if update_request.get('stopLoss', 0) != 0 else 'take_profit'
            })
            return {'success': True}
    
    # Create test managers
    mock_client = MockClient()
    breakeven_manager = AutoBreakevenManager(
        client=mock_client,
        account_id="TEST123"
    )
    tp_manager = RunningTPManager(
        client=mock_client,
        account_id="TEST123"
    )
    
    print("=== Testing AutoBreakevenManager Throttling ===")
    
    # Create test position for breakeven
    be_position = PositionState(
        order_id="BE_ORDER",
        account_id="TEST123",
        symbol="AAPL",
        side=OrderSide.BUY,
        entry_price=150.0,
        quantity=100,
        current_stop_loss=149.0
    )
    
    # Create breakeven config
    be_config = AutoBreakevenConfig(
        enabled=True,
        trigger_levels=[0.5, 1.0, 1.5],  # Trigger at $0.50, $1.00, $1.50 profit
        sl_offsets=[0.1, 0.2, 0.3]       # Move SL to +$0.10, +$0.20, +$0.30
    )
    
    breakeven_manager.start_monitoring("BE_ORDER", be_position, be_config)
    
    # Test rapid breakeven updates (should be throttled)
    print(f"Breakeven throttling interval: {breakeven_manager.min_update_interval_seconds}s")
    
    # Trigger first breakeven move
    print("\nTriggering breakeven moves...")
    prices = [150.6, 150.7, 150.8]  # Above $0.50 profit trigger
    for i, price in enumerate(prices):
        print(f"Update {i+1}: Price = {price}")
        result = breakeven_manager.check_and_update("BE_ORDER", price)
        print(f"  Breakeven result: {result}")
        print(f"  Total API calls: {len(mock_client.update_calls)}")
        time.sleep(1)  # 1 second between updates
    
    print("\n=== Testing RunningTPManager Throttling ===")
    
    # Create test position for TP
    tp_position = PositionState(
        order_id="TP_ORDER",
        account_id="TEST123",
        symbol="MSFT",
        side=OrderSide.BUY,
        entry_price=300.0,
        quantity=50,
        current_take_profit=305.0
    )
    
    # Create TP config
    tp_config = RunningTPConfig(
        enabled=True,
        enable_trailing_extremes=True,
        extend_by_ticks=0.05
    )
    
    tp_manager.start_monitoring("TP_ORDER", tp_position, tp_config)
    
    print(f"TP throttling interval: {tp_manager.min_update_interval_seconds}s")
    
    # Test rapid TP updates (should be throttled)
    print("\nTriggering TP moves...")
    tp_prices = [300.1, 300.2, 300.3, 300.4]
    for i, price in enumerate(tp_prices):
        print(f"Update {i+1}: Price = {price}")
        result = tp_manager.check_and_update("TP_ORDER", price)
        print(f"  TP result: {result}")
        print(f"  Total API calls: {len(mock_client.update_calls)}")
        time.sleep(1)  # 1 second between updates
    
    print(f"\n=== Final Results ===")
    print(f"Total API calls across both managers: {len(mock_client.update_calls)}")
    print("Call details:")
    for i, call in enumerate(mock_client.update_calls):
        call_type = "Breakeven SL" if call['stop_loss'] > 0 and call['stop_loss'] < 200 else "Take Profit"
        print(f"  Call {i+1}: {call_type} = {call['stop_loss']:.2f} for {call['order_id']} at {call['timestamp']:.1f}")
    
    # Test after throttle period
    print(f"\nWaiting {max(breakeven_manager.min_update_interval_seconds, tp_manager.min_update_interval_seconds)} seconds...")
    time.sleep(max(breakeven_manager.min_update_interval_seconds, tp_manager.min_update_interval_seconds) + 0.1)
    
    print("Testing updates after throttle cooldown...")
    be_result = breakeven_manager.check_and_update("BE_ORDER", 151.1)  # Trigger next breakeven level
    tp_result = tp_manager.check_and_update("TP_ORDER", 300.5)
    
    print(f"Post-cooldown breakeven result: {be_result}")
    print(f"Post-cooldown TP result: {tp_result}")
    print(f"Final total API calls: {len(mock_client.update_calls)}")

if __name__ == "__main__":
    test_both_managers()