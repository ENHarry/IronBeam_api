# IronBeam Python SDK

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/status-production_ready-green.svg)](https://github.com/ENHarry/IronBeam_api)

A comprehensive, production-ready Python SDK for the IronBeam API with automated trade and risk management, real-time WebSocket streaming, and robust field name compatibility.

## Features

### Core API Client
- ✅ **Full API Coverage**: All 49 IronBeam API endpoints implemented
- ✅ **Robust Field Compatibility**: Handles both API format ('s', 'b', 'a') and SDK format ('exchSym', 'bidPrice', 'askPrice') automatically
- ✅ **Pydantic v2 Models**: Full type safety with dual field name validation using AliasChoices
- ✅ **Bracket Order Support**: Comprehensive support for stop-loss and take-profit orders with proper field serialization
- ✅ **Authentication**: Secure token-based authentication with logout support
- ✅ **Account Management**: Balance, positions, risk, fills, orders
- ✅ **Market Data**: Quotes, depth, trades, historical data
- ✅ **Order Management**: Place, update, cancel orders (single & batch)
- ✅ **Symbol Search**: Futures, options, spreads, security definitions
- ✅ **Simulated Trading**: Demo account management and cash operations

### API Field Compatibility 🔧
The SDK intelligently handles field name variations between API responses and SDK expectations:

**Quote Data Fields**:
- `s` / `exchSym` - Exchange symbol
- `b` / `bidPrice` - Bid price 
- `a` / `askPrice` - Ask price
- `bs` / `bidSize` - Bid size
- `as` / `askSize` - Ask size

**Order Fields**:
- Automatically serializes to camelCase for API requests
- Validates both abbreviated and full field names in responses
- Ensures bracket orders work correctly with stop-loss/take-profit fields

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

### Via pip (Recommended)
```bash
pip install ironbeam-sdk
```

### Development Installation
```bash
git clone https://github.com/ENHarry/IronBeam_api.git
cd IronBeam_api
pip install -e .
```

### Manual Installation
```bash
pip install requests pydantic>=2.0 websockets
```

### Requirements
- **Python**: 3.7+
- **Pydantic**: 2.0+ (for AliasChoices field compatibility)
- **requests**: HTTP client for REST API
- **websockets**: WebSocket streaming support

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

# Get real-time quotes (handles both API formats automatically)
quotes = client.get_quotes(["XCME:ES.Z24", "XCME:NQ.Z24"])
for quote in quotes.quotes:
    print(f"Symbol: {quote.exch_sym}, Bid: {quote.bid_price}, Ask: {quote.ask_price}")

# Place a simple order
order = {
    "accountId": "account_id",
    "exchSym": "XCME:ES.Z24", 
    "side": "BUY",
    "quantity": 1,
    "orderType": "MARKET",
    "duration": "DAY"
}
response = client.place_order("account_id", order)

# Place a bracket order (with stop-loss and take-profit)
bracket_order = {
    "accountId": "account_id",
    "exchSym": "XCME:ES.Z24",
    "side": "BUY", 
    "quantity": 1,
    "orderType": "LIMIT",
    "duration": "DAY",
    "price": 5000.0,
    "stopLoss": 4950.0,  # Stop loss 50 points below
    "takeProfit": 5050.0  # Take profit 50 points above
}
bracket_response = client.place_order("account_id", bracket_order)
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
    # Quotes automatically handle both API field formats
    print(f"Quote: {quote.exch_sym} | Bid: {quote.bid_price} | Ask: {quote.ask_price}")

async def main():
    stream = IronBeamStream(client)
    stream.on_quote(on_quote)

    await stream.connect()
    stream.subscribe_quotes(["XCME:ES.Z24", "XCME:NQ.Z24"])

    await stream.listen()

asyncio.run(main())
```

## Data Model Compatibility & Robustness

### Field Name Flexibility
The SDK uses Pydantic v2's `AliasChoices` to handle field name variations seamlessly:

```python
# These are equivalent - SDK handles both formats
api_format = {"s": "XCME:ES.Z24", "b": 5000.0, "a": 5000.25}
sdk_format = {"exchSym": "XCME:ES.Z24", "bidPrice": 5000.0, "askPrice": 5000.25}

# Both work identically
quote1 = Quote(**api_format)
quote2 = Quote(**sdk_format)
# quote1.exch_sym == quote2.exch_sym == "XCME:ES.Z24"
```

### Robust Response Handling
- **Optional Fields**: Response models handle missing optional fields gracefully
- **Mixed Formats**: Can process responses with mixed field name formats
- **Backward Compatibility**: Maintains compatibility with existing code
- **Type Safety**: Full Pydantic validation with proper type hints

### Order Serialization
```python
# OrderRequest automatically serializes to API format
order = OrderRequest(
    account_id="12345",
    exch_sym="XCME:ES.Z24", 
    side="BUY",
    quantity=1,
    order_type="LIMIT",
    price=5000.0,
    stop_loss=4950.0,  # Automatically becomes "stopLoss" in API call
    take_profit=5050.0  # Automatically becomes "takeProfit" in API call
)
# Results in: {"accountId": "12345", "exchSym": "XCME:ES.Z24", "stopLoss": 4950.0, ...}
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

See the comprehensive documentation and examples:

### 📁 Code Examples
- **[examples/](examples/)** - Complete working examples and tutorials:
  - [auto_breakeven_example.py](examples/auto_breakeven_example.py) - Auto breakeven usage
  - [running_tp_example.py](examples/running_tp_example.py) - Running TP strategies  
  - [combined_strategy_example.py](examples/combined_strategy_example.py) - Both features together
  - [01_authentication_examples.py](examples/01_authentication_examples.py) - Authentication patterns
  - [02_account_management.py](examples/02_account_management.py) - Account operations
  - [03_market_data.py](examples/03_market_data.py) - Market data access
  - [04_order_management.py](examples/04_order_management.py) - Order placement and management
  - [05_streaming_websocket.py](examples/05_streaming_websocket.py) - WebSocket streaming setup

### 📁 Utility Scripts
- **[scripts/](scripts/)** - Standalone utility scripts:
  - [reset_demo_account.py](scripts/reset_demo_account.py) - Reset demo account balances
  - [simple_reset.py](scripts/simple_reset.py) - Simple account reset
  - [super_simple_reset.py](scripts/super_simple_reset.py) - Minimal reset script

### 📁 Documentation
- **[docs/](docs/)** - Comprehensive documentation:
  - [MBO Data Guide](docs/MBO_DATA_GUIDE.md) - Market by Order data format
  - [Streaming Data Dictionary](docs/STREAMING_DATA_DICTIONARY.md) - WebSocket data reference
  - [Demo Account Reset](docs/DEMO_ACCOUNT_RESET.md) - Account management guide
  - [Publishing Guide](docs/PUBLISHING_GUIDE.md) - Package publication instructions

## Architecture

```
ironbeam/
├── client.py           # REST API client with authentication
├── models.py           # Pydantic v2 models with AliasChoices compatibility
├── streaming.py        # WebSocket streaming with auto-reconnect
├── trade_manager.py    # Auto breakeven & Running TP strategies
├── execution_engine.py # ThreadedExecutor & AsyncExecutor engines
└── exceptions.py       # Custom exceptions and error handling
```

### Key Architecture Features

**Dual Field Name Support**: 
- `models.py` uses `AliasChoices` for maximum API compatibility
- Handles IronBeam API's field name variations automatically
- Maintains type safety and validation

**Robust Error Handling**:
- Custom exceptions for different error types
- Graceful handling of API field format changes
- Comprehensive validation with helpful error messages

**Flexible Execution**:
- ThreadedExecutor for simple polling-based execution
- AsyncExecutor for high-performance WebSocket-driven execution
- Both support auto-breakeven and running take-profit strategies

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

- **Python 3.7+**
- **pydantic >= 2.0** (required for AliasChoices field compatibility)
- **requests** (HTTP client for REST API)
- **websockets** (WebSocket streaming support)

### Compatibility Notes
- Pydantic v2 is required for the dual field name support that makes the SDK robust against API field format changes
- The SDK is tested with Python 3.7+ but works best with Python 3.8+
- WebSocket features require a stable internet connection for optimal performance

## License

MIT License - see [LICENSE](LICENSE) for details

## Disclaimer

This is an unofficial but production-ready SDK for the IronBeam API. The SDK has been thoroughly tested and includes robust error handling and field compatibility features. However, always test thoroughly in a demo environment before using with live trading accounts.

**Production Features**:
- ✅ Comprehensive field name compatibility
- ✅ Robust error handling and validation
- ✅ Extensive testing with various API response formats
- ✅ Auto-reconnect and state management for streaming
- ✅ Thread-safe execution engines

**Recommended Testing**:
- Always test your strategies in demo accounts first
- Validate bracket orders and risk management features
- Test network connectivity and error handling scenarios

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions:
- GitHub Issues: [https://github.com/ENHarry/IronBeam_api/issues](https://github.com/ENHarry/IronBeam_api/issues)
- IronBeam API Docs: [https://docs.ironbeamapi.com/](https://docs.ironbeamapi.com/)
