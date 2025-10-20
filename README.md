# IronBeam Python SDK

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python SDK for the IronBeam API with automated trade and risk management.

## Features

### Core API Client
- ✅ **Full API Coverage**: All 49 IronBeam API endpoints implemented
- ✅ **Authentication**: Secure token-based authentication with logout support
- ✅ **Account Management**: Balance, positions, risk, fills, orders
- ✅ **Market Data**: Quotes, depth, trades, historical data
- ✅ **Order Management**: Place, update, cancel orders (single & batch)
- ✅ **Symbol Search**: Futures, options, spreads, security definitions
- ✅ **Simulated Trading**: Demo account management and cash operations
- ✅ **Pydantic Models**: Full type safety with validation

### Advanced Streaming
- ✅ **WebSocket Support**: Real-time market data streaming
- ✅ **Auto-Reconnect**: Exponential backoff with subscription restoration
- ✅ **Event Callbacks**: Quote, depth, trade, error handlers
- ✅ **Subscription Management**: Subscribe/unsubscribe to symbols and indicators
- ✅ **Connection State**: CONNECTED, RECONNECTING, DISCONNECTED states

### Automated Trade Management 🎯

#### Auto Breakeven
Automatically moves stop loss up to 3 times based on profit levels:
- **Trigger Modes**: Ticks or percentage-based
- **Custom Levels**: Configure trigger and offset levels per move
- **Position Tracking**: State management to prevent duplicate moves
- **Both Sides**: LONG and SHORT position support

**Example**: LONG at 5000
- Move 1: Price @ 5020 → SL to 5010
- Move 2: Price @ 5040 → SL to 5030
- Move 3: Price @ 5060 → SL to 5050

#### Running Take Profit
Dynamically adjusts take profit with multiple strategies:
- **Trailing Extremes**: Follow highest high (LONG) / lowest low (SHORT)
- **Profit Levels**: Trigger moves at specific profit milestones
- **Multiple Modes**:
  - Mode A: Extend TP by X ticks
  - Mode B: Trail current price + offset
  - Mode C: Move to resistance/support levels
- **Combined Strategies**: Use multiple triggers and modes simultaneously

### Execution Engines

#### ThreadedExecutor (Polling-based)
- Polls positions via REST API at regular intervals
- Simple, reliable, works anywhere
- Configurable poll interval (default 1s)
- Automatic rate limiting

#### AsyncExecutor (Event-driven)
- Real-time execution via WebSocket streaming
- <100ms latency on price updates
- Event-driven architecture
- Efficient resource usage
- Best for production and scalping

## Installation

```bash
pip install -e .
```

Or install dependencies:
```bash
pip install requests pydantic websockets
```

## Quick Start

### Basic Usage

```python
from ironbeam import IronBeam

# Initialize and authenticate
client = IronBeam(
    api_key="your_api_key",
    username="your_username",
    password="your_password"
)
client.authenticate()

# Get account info
trader_info = client.get_trader_info()
balance = client.get_account_balance("account_id")
positions = client.get_positions("account_id")

# Place an order
order = {
    "accountId": "account_id",
    "exchSym": "XCME:ES.Z24",
    "side": "BUY",
    "quantity": 1,
    "orderType": "MARKET",
    "duration": "DAY"
}
response = client.place_order("account_id", order)
```

### Auto Breakeven

```python
from ironbeam import (
    ThreadedExecutor,
    AutoBreakevenConfig,
    PositionState,
    OrderSide
)

# Configure auto breakeven
config = AutoBreakevenConfig(
    trigger_mode="ticks",
    trigger_levels=[20, 40, 60],
    sl_offsets=[10, 30, 50],
    enabled=True
)

# Create position state
position = PositionState(
    order_id="12345",
    account_id="account_id",
    symbol="XCME:ES.Z24",
    side=OrderSide.BUY,
    entry_price=5000.0,
    quantity=1,
    current_stop_loss=4980.0
)

# Start executor
executor = ThreadedExecutor(client, "account_id")
executor.add_auto_breakeven("12345", position, config)
executor.start()
```

### Running Take Profit

```python
from ironbeam import RunningTPConfig, AsyncExecutor
import asyncio

async def main():
    # Configure running TP
    config = RunningTPConfig(
        enable_trailing_extremes=True,
        enable_profit_levels=True,
        profit_level_triggers=[30, 60, 90],
        extend_by_ticks=20,
        trail_offset_ticks=50,
        resistance_support_levels=[5100, 5150, 5200],
        enabled=True
    )

    position = PositionState(
        order_id="12345",
        account_id="account_id",
        symbol="XCME:ES.Z24",
        side=OrderSide.BUY,
        entry_price=5000.0,
        quantity=1,
        current_take_profit=5050.0
    )

    # Use async executor for real-time updates
    executor = AsyncExecutor(client, "account_id")
    await executor.add_running_tp("12345", position, config)
    await executor.start()

    # Run until interrupted
    await asyncio.sleep(3600)
    await executor.stop()

asyncio.run(main())
```

### Combined Strategy

```python
# Use both auto breakeven and running TP together
executor = AsyncExecutor(client, "account_id")

await executor.add_auto_breakeven(order_id, position, breakeven_config)
await executor.add_running_tp(order_id, position, tp_config)

await executor.start()
```

### WebSocket Streaming

```python
from ironbeam import IronBeamStream
import asyncio

async def on_quote(quote):
    print(f"Quote: {quote}")

async def main():
    stream = IronBeamStream(client)
    stream.on_quote(on_quote)

    await stream.connect()
    stream.subscribe_quotes(["XCME:ES.Z24", "XCME:NQ.Z24"])

    await stream.listen()

asyncio.run(main())
```

## API Coverage

### Authentication
- `authenticate()` - Get auth token
- `logout()` - Invalidate token

### Account Information
- `get_trader_info()` - Trader details
- `get_user_info()` - User information
- `get_account_balance()` - Account balance
- `get_positions()` - Open positions
- `get_risk()` - Risk metrics
- `get_fills()` - Trade fills

### Market Data
- `get_quotes()` - Real-time quotes
- `get_depth()` - Market depth
- `get_trades()` - Historical trades
- `get_security_definitions()` - Security info
- `get_security_margin()` - Margin requirements
- `get_security_status()` - Security status

### Order Management
- `place_order()` - Submit new order
- `update_order()` - Modify existing order
- `cancel_order()` - Cancel single order
- `cancel_multiple_orders()` - Batch cancel
- `get_orders()` - Query orders
- `get_order_fills()` - Order fill history
- `get_to_order_id()` - Strategy ID → Order ID
- `get_to_strategy_id()` - Order ID → Strategy ID

### Symbol Search
- `get_symbols()` - Search symbols
- `search_futures()` - Search futures
- `search_options()` - Search options
- `search_option_spreads()` - Search option spreads
- `search_option_groups()` - Search option groups
- `get_exchange_sources()` - Available exchanges
- `get_complexes()` - Market complexes
- `get_strategy_id()` - Get strategy ID

### Streaming Subscriptions
- `subscribe_quotes()` - Subscribe to quotes
- `subscribe_depths()` - Subscribe to depth
- `subscribe_trades()` - Subscribe to trades
- `unsubscribe_quotes()` - Unsubscribe quotes
- `unsubscribe_depths()` - Unsubscribe depth
- `unsubscribe_trades()` - Unsubscribe trades
- `subscribe_tick_bars()` - Tick bar indicators
- `subscribe_trade_bars()` - Trade bar indicators
- `subscribe_time_bars()` - Time bar indicators
- `subscribe_volume_bars()` - Volume bar indicators
- `unsubscribe_indicator()` - Unsubscribe indicator

### Simulated Accounts
- `create_simulated_trader()` - Create demo trader
- `add_simulated_account()` - Add demo account
- `simulated_account_reset()` - Reset account
- `simulated_account_expire()` - Expire account
- `simulated_account_add_cash()` - Add cash
- `simulated_account_get_cash_report()` - Cash report

## Examples

See the [examples/](examples/) directory for complete examples:
- [auto_breakeven_example.py](examples/auto_breakeven_example.py) - Auto breakeven usage
- [running_tp_example.py](examples/running_tp_example.py) - Running TP strategies
- [combined_strategy_example.py](examples/combined_strategy_example.py) - Both features together

## Architecture

```
ironbeam/
├── client.py           # REST API client
├── models.py           # Pydantic models & enums
├── streaming.py        # WebSocket streaming
├── trade_manager.py    # Auto breakeven & Running TP
├── execution_engine.py # ThreadedExecutor & AsyncExecutor
└── exceptions.py       # Custom exceptions
```

## Configuration Examples

### Auto Breakeven Configs

```python
# Aggressive (quick breakeven)
AutoBreakevenConfig(
    trigger_levels=[10, 20, 30],
    sl_offsets=[5, 15, 25]
)

# Conservative (wider levels)
AutoBreakevenConfig(
    trigger_levels=[50, 100, 150],
    sl_offsets=[25, 75, 125]
)

# Percentage-based
AutoBreakevenConfig(
    trigger_mode="percentage",
    trigger_levels=[2, 4, 6],  # 2%, 4%, 6% profit
    sl_offsets=[10, 30, 50]
)
```

### Running TP Configs

```python
# Trailing only
RunningTPConfig(
    enable_trailing_extremes=True,
    trail_offset_ticks=50
)

# Profit levels only
RunningTPConfig(
    enable_profit_levels=True,
    profit_level_triggers=[30, 60, 90],
    extend_by_ticks=25
)

# Combined with all modes
RunningTPConfig(
    enable_trailing_extremes=True,
    enable_profit_levels=True,
    profit_level_triggers=[30, 60, 90],
    extend_by_ticks=20,
    trail_offset_ticks=50,
    resistance_support_levels=[5100, 5150, 5200]
)
```

## ThreadedExecutor vs AsyncExecutor

| Feature | ThreadedExecutor | AsyncExecutor |
|---------|-----------------|---------------|
| **Latency** | 1-2 seconds | <100ms |
| **Connection** | REST polling | WebSocket streaming |
| **Resource Usage** | Low | Medium |
| **Complexity** | Simple | Moderate |
| **Best For** | Development, testing | Production, scalping |
| **Deployment** | Works anywhere | Requires persistent connection |

## Requirements

- Python 3.7+
- requests
- pydantic
- websockets

## License

MIT License - see [LICENSE](LICENSE) for details

## Disclaimer

This is an unofficial SDK. Use at your own risk. Always test thoroughly in a demo environment before using with live trading accounts.

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions:
- GitHub Issues: [https://github.com/ENHarry/IronBeam_api/issues](https://github.com/ENHarry/IronBeam_api/issues)
- IronBeam API Docs: [https://docs.ironbeamapi.com/](https://docs.ironbeamapi.com/)
