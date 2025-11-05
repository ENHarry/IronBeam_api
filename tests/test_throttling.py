#!/usr/bin/env python3
"""
Test the enhanced RunningTPManager with throttling functionality.
"""

import sys
import time
from pathlib import Path

# Add the ironbeam directory to the path
ironbeam_path = Path(__file__).parent
sys.path.insert(0, str(ironbeam_path))

# Import ironbeam modules
from ironbeam.trade_manager import RunningTPManager, PositionState, RunningTPConfig
from ironbeam.models import OrderSide

def test_throttling():
    """Test that throttling prevents excessive API calls."""
    
    # Mock client that tracks update calls
    class MockClient:
        def __init__(self):
            self.update_calls = []
            
        def update_order(self, account_id, order_id, update_request):
            self.update_calls.append({
                'timestamp': time.time(),
                'order_id': order_id,
                'new_tp': update_request.get('stopLoss', 0)
            })
            return {'success': True}
    
    # Create test manager
    mock_client = MockClient()
    manager = RunningTPManager(
        client=mock_client,
        account_id="TEST123"
    )
    
    # Create test position
    position = PositionState(
        order_id="TEST_ORDER",
        account_id="TEST123",
        symbol="AAPL",
        side=OrderSide.BUY,
        entry_price=150.0,
        quantity=100,
        current_take_profit=155.0
    )
    
    # Create config with trailing enabled
    config = RunningTPConfig(
        enabled=True,
        enable_trailing_extremes=True,
        extend_by_ticks=0.05
    )
    
    # Start monitoring
    manager.start_monitoring("TEST_ORDER", position, config)
    
    print("Testing throttling functionality...")
    print(f"Throttling interval: {manager.min_update_interval_seconds} seconds")
    
    # Test rapid updates (should be throttled)
    prices = [150.1, 150.2, 150.3, 150.4, 150.5]
    for i, price in enumerate(prices):
        print(f"\nUpdate {i+1}: Price = {price}")
        result = manager.check_and_update("TEST_ORDER", price)
        print(f"  Update result: {result}")
        print(f"  Total API calls: {len(mock_client.update_calls)}")
        time.sleep(1)  # 1 second between updates (less than throttle interval)
    
    print(f"\nFinal API call count: {len(mock_client.update_calls)}")
    print("API call details:")
    for i, call in enumerate(mock_client.update_calls):
        print(f"  Call {i+1}: TP={call['new_tp']:.2f} at {call['timestamp']:.1f}")
    
    # Test that updates work after throttle interval
    print(f"\nWaiting {manager.min_update_interval_seconds} seconds for throttle to reset...")
    time.sleep(manager.min_update_interval_seconds + 0.1)
    
    print("Testing update after throttle interval...")
    result = manager.check_and_update("TEST_ORDER", 150.6)
    print(f"Update result: {result}")
    print(f"Final API call count: {len(mock_client.update_calls)}")

if __name__ == "__main__":
    test_throttling()