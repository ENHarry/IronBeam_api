# IronBeam SDK - Examples Directory

Complete usage examples for all 48 API endpoints plus trade management features.

## Quick Navigation

| File | Functions | Status | Description |
|------|-----------|--------|-------------|
| [09_quick_reference.py](09_quick_reference.py) | All (48) | ✅ Complete | One-liner examples for every function |
| [01_authentication_examples.py](01_authentication_examples.py) | 2 | ✅ Complete | Authentication and logout |
| [auto_breakeven_example.py](auto_breakeven_example.py) | Trade Mgmt | ✅ Complete | Auto breakeven usage |
| [running_tp_example.py](running_tp_example.py) | Trade Mgmt | ✅ Complete | Running take profit strategies |
| [combined_strategy_example.py](combined_strategy_example.py) | Trade Mgmt | ✅ Complete | Both features together |
| 02_account_examples.py | 6 | 📝 Template | Account information |
| 03_market_data_examples.py | 6 | 📝 Template | Market data feeds |
| 04_order_management_examples.py | 8 | 📝 Template | Trading operations |
| 05_symbol_search_examples.py | 9 | 📝 Template | Symbol lookups |
| 06_streaming_examples.py | 13 | 📝 Template | WebSocket streaming |
| 07_simulated_accounts_examples.py | 6 | 📝 Template | Demo accounts |
| 08_trade_management_workflows.py | N/A | 📝 Template | Complete workflows |

---

## Function Index

### Authentication (2 functions)
**File**: [01_authentication_examples.py](01_authentication_examples.py)
- `authenticate()` - Get auth token
- `logout()` - Invalidate token

**Quick Reference**: Line 22-26 in [09_quick_reference.py](09_quick_reference.py)

### Account Information (6 functions)
**File**: 02_account_examples.py (template below)
- `get_trader_info()` - Trader details
- `get_user_info()` - User information
- `get_account_balance()` - Account balance
- `get_positions()` - Open positions
- `get_risk()` - Risk metrics
- `get_fills()` - Trade fills

**Quick Reference**: Line 32-47 in [09_quick_reference.py](09_quick_reference.py)

### Market Data (6 functions)
**File**: 03_market_data_examples.py (template below)
- `get_quotes()` - Real-time quotes
- `get_depth()` - Market depth
- `get_trades()` - Historical trades
- `get_security_definitions()` - Security info
- `get_security_margin()` - Margin requirements
- `get_security_status()` - Security status

**Quick Reference**: Line 53-75 in [09_quick_reference.py](09_quick_reference.py)

### Order Management (8 functions)
**File**: 04_order_management_examples.py (template below)
- `place_order()` - Submit orders
- `update_order()` - Modify orders
- `cancel_order()` - Cancel single order
- `cancel_multiple_orders()` - Batch cancel
- `get_orders()` - Query orders
- `get_order_fills()` - Fill history
- `get_to_order_id()` - Strategy → Order ID
- `get_to_strategy_id()` - Order → Strategy ID

**Quick Reference**: Line 99-137 in [09_quick_reference.py](09_quick_reference.py)

### Symbol Search (9 functions)
**File**: 05_symbol_search_examples.py (template below)
- `get_symbols()` - Search symbols
- `get_exchange_sources()` - Exchanges
- `get_complexes()` - Market complexes
- `search_futures()` - Futures contracts
- `search_option_groups()` - Option groups
- `search_options()` - Option chains
- `search_option_spreads()` - Option spreads
- `get_strategy_id()` - Strategy ID

**Quick Reference**: Line 81-97 in [09_quick_reference.py](09_quick_reference.py)

### Streaming (13 functions)
**File**: 06_streaming_examples.py (template below)
- `create_stream()` - Create stream
- `subscribe_quotes()` - Quote subscriptions
- `subscribe_depths()` - Depth subscriptions
- `subscribe_trades()` - Trade subscriptions
- `unsubscribe_quotes()` / `unsubscribe_depths()` / `unsubscribe_trades()` - Unsubscribe
- `subscribe_tick_bars()` - Tick bars
- `subscribe_trade_bars()` - Trade bars
- `subscribe_time_bars()` - Time bars
- `subscribe_volume_bars()` - Volume bars
- `unsubscribe_indicator()` - Unsubscribe indicator
- `IronBeamStream` - WebSocket class

**Quick Reference**: Line 143-184 in [09_quick_reference.py](09_quick_reference.py)

### Simulated Accounts (6 functions)
**File**: 07_simulated_accounts_examples.py (template below)
- `create_simulated_trader()` - Create demo trader
- `add_simulated_account()` - Add demo account
- `simulated_account_reset()` - Reset account
- `simulated_account_expire()` - Expire account
- `simulated_account_add_cash()` - Add cash
- `simulated_account_get_cash_report()` - Cash report

**Quick Reference**: Line 190-217 in [09_quick_reference.py](09_quick_reference.py)

### Trade Management
**Files**: [auto_breakeven_example.py](auto_breakeven_example.py), [running_tp_example.py](running_tp_example.py), [combined_strategy_example.py](combined_strategy_example.py)
- `AutoBreakevenConfig` - Configure auto breakeven
- `AutoBreakevenManager` - Manage auto breakeven
- `RunningTPConfig` - Configure running TP
- `RunningTPManager` - Manage running TP
- `ThreadedExecutor` - Polling-based execution
- `AsyncExecutor` - Event-driven execution
- `PositionState` - Position tracking

**Quick Reference**: Line 236-282 in [09_quick_reference.py](09_quick_reference.py)

---

## How to Use These Examples

### 1. Start with Quick Reference
Open [09_quick_reference.py](09_quick_reference.py) for a complete overview of all functions.

### 2. Deep Dive into Categories
Pick a category and open the corresponding file for detailed examples with explanations.

### 3. Copy-Paste and Modify
All examples are ready to use - just replace credentials and account IDs.

### 4. Learn Common Patterns
Check the "Common Patterns" section at the end of [09_quick_reference.py](09_quick_reference.py).

---

## Example Templates

### Template: Account Examples (02_account_examples.py)

```python
from ironbeam import IronBeam

client = IronBeam(api_key="...", username="...", password="...")
client.authenticate()

# Example: Get trader info
trader_info = client.get_trader_info()
print(f"Trader ID: {trader_info['traderId']}")
print(f"Accounts: {trader_info['accounts']}")

# Example: Get account balance
balance = client.get_account_balance("account_id")
for bal in balance['balances']:
    print(f"{bal['currencyCode']}: ${bal['cashBalance']:.2f}")

# Example: Get positions
positions = client.get_positions("account_id")
for pos in positions['positions']:
    print(f"{pos['exchSym']}: {pos['quantity']} @ {pos['price']}")
```

### Template: Market Data Examples (03_market_data_examples.py)

```python
# Example: Get quotes
quotes = client.get_quotes(["XCME:ES.Z24", "XCME:NQ.Z24"])
for quote in quotes['quotes']:
    print(f"{quote['exchSym']}: "
          f"Bid={quote.get('bidPrice')}, "
          f"Ask={quote.get('askPrice')}, "
          f"Last={quote.get('lastPrice')}")

# Example: Get market depth
depth = client.get_depth(["XCME:ES.Z24"])
for d in depth['depths']:
    print(f"\nDepth for {d['exchSym']}:")
    print(f"  Bids: {len(d['bids'])} levels")
    print(f"  Asks: {len(d['asks'])} levels")
```

### Template: Order Examples (04_order_management_examples.py)

```python
# Example: Place market order
order = {
    "accountId": "account_id",
    "exchSym": "XCME:ES.Z24",
    "side": "BUY",
    "quantity": 1,
    "orderType": "MARKET",
    "duration": "DAY"
}
response = client.place_order("account_id", order)
print(f"Order ID: {response['orderId']}")

# Example: Place limit order with bracket
bracket_order = {
    "accountId": "account_id",
    "exchSym": "XCME:ES.Z24",
    "side": "BUY",
    "quantity": 1,
    "orderType": "LIMIT",
    "limitPrice": 5000.0,
    "stopLoss": 4980.0,
    "takeProfit": 5050.0,
    "duration": "DAY"
}
response = client.place_order("account_id", bracket_order)

# Example: Update order
update = {"orderId": "order_id", "limitPrice": 5010.0}
client.update_order("account_id", "order_id", update)

# Example: Cancel order
client.cancel_order("account_id", "order_id")

# Example: Get working orders
working = client.get_orders("account_id", "WORKING")
print(f"Working orders: {len(working['orders'])}")
```

---

## Complete Workflows

### Workflow 1: Basic Trading
```python
# 1. Authenticate
client.authenticate()

# 2. Check balance
balance = client.get_account_balance("account_id")

# 3. Get quote
quotes = client.get_quotes(["XCME:ES.Z24"])
price = quotes['quotes'][0]['lastPrice']

# 4. Place order
order = {
    "accountId": "account_id",
    "exchSym": "XCME:ES.Z24",
    "side": "BUY",
    "quantity": 1,
    "orderType": "MARKET",
    "duration": "DAY"
}
response = client.place_order("account_id", order)

# 5. Monitor position
positions = client.get_positions("account_id")
```

### Workflow 2: Automated Trade Management
```python
from ironbeam import (
    ThreadedExecutor, AutoBreakevenConfig,
    RunningTPConfig, PositionState, OrderSide
)

# Place order (see above)
order_id = response['orderId']

# Configure auto breakeven
be_config = AutoBreakevenConfig(
    trigger_levels=[20, 40, 60],
    sl_offsets=[10, 30, 50]
)

# Configure running TP
tp_config = RunningTPConfig(
    enable_trailing_extremes=True,
    trail_offset_ticks=50
)

# Create position state
position = PositionState(
    order_id=order_id,
    account_id="account_id",
    symbol="XCME:ES.Z24",
    side=OrderSide.BUY,
    entry_price=price,
    quantity=1
)

# Start executor
executor = ThreadedExecutor(client, "account_id")
executor.add_auto_breakeven(order_id, position, be_config)
executor.add_running_tp(order_id, position, tp_config)
executor.start()
```

### Workflow 3: Real-Time Market Monitoring
```python
import asyncio
from ironbeam import IronBeamStream

async def main():
    stream = IronBeamStream(client)

    async def on_quote(quote):
        print(f"Quote: {quote['exchSym']} @ {quote.get('lastPrice')}")

    stream.on_quote(on_quote)
    await stream.connect()
    stream.subscribe_quotes(["XCME:ES.Z24", "XCME:NQ.Z24"])
    await stream.listen()

asyncio.run(main())
```

---

## Common Patterns

### Pattern 1: Error Handling
```python
try:
    response = client.place_order("account_id", order)
except AuthenticationError:
    client.authenticate()  # Re-auth and retry
    response = client.place_order("account_id", order)
except Exception as e:
    print(f"Error: {e}")
```

### Pattern 2: Batch Operations
```python
# Get quotes for multiple symbols
symbols = ["XCME:ES.Z24", "XCME:NQ.Z24", "XCME:YM.Z24"]
quotes = client.get_quotes(symbols)

# Cancel multiple orders
order_ids = ["order1", "order2", "order3"]
client.cancel_multiple_orders("account_id", order_ids)
```

### Pattern 3: Position Monitoring Loop
```python
import time

while True:
    positions = client.get_positions("account_id")
    for pos in positions['positions']:
        pnl = pos.get('unrealizedPL', 0)
        print(f"{pos['exchSym']}: ${pnl:.2f}")

    time.sleep(5)  # Update every 5 seconds
```

---

## Tips and Best Practices

### Security
✅ Use environment variables for credentials
✅ Never commit API keys to git
✅ Use `.env` files (add to `.gitignore`)
❌ Don't hardcode credentials

### Error Handling
✅ Always wrap API calls in try-except
✅ Handle `AuthenticationError` separately
✅ Log errors for debugging
✅ Implement retry logic for network errors

### Performance
✅ Use AsyncExecutor for low-latency needs
✅ Batch operations when possible
✅ Cache frequently accessed data
✅ Use WebSocket for real-time data (not polling)

### Testing
✅ Start with simulated/demo accounts
✅ Test error scenarios
✅ Verify order placement before going live
✅ Monitor logs carefully

---

## Need More Help?

- **SDK Documentation**: [README.md](../README.md)
- **API Docs**: https://docs.ironbeamapi.com/
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md)
- **Endpoint Verification**: [ENDPOINT_VERIFICATION.md](../ENDPOINT_VERIFICATION.md)

---

## Contributing Examples

Have a useful example? Please contribute!

1. Follow the existing format
2. Include error handling
3. Add comments
4. Test the code
5. Submit a pull request
