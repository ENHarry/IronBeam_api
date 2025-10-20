"""
Quick Reference Guide - All IronBeam SDK Functions

One-liner examples for every function in the SDK.
Copy-paste ready code snippets.

Total Functions: 48 API endpoints + Trade Management
"""

from ironbeam import IronBeam, OrderSide, OrderType, DurationType
from ironbeam import ThreadedExecutor, AsyncExecutor
from ironbeam import AutoBreakevenConfig, RunningTPConfig, PositionState
import asyncio

# ============================================================================
# INITIALIZATION
# ============================================================================

client = IronBeam(
    api_key="your_api_key",
    username="your_username",
    password="your_password"
)

# ============================================================================
# AUTHENTICATION (2 functions)
# ============================================================================

# 1. authenticate() - Get auth token
token = client.authenticate()

# 2. logout() - Invalidate token
client.logout()

# ============================================================================
# ACCOUNT INFORMATION (6 functions)
# ============================================================================

# 3. get_trader_info() - Get trader details
trader_info = client.get_trader_info()

# 4. get_user_info() - Get user information
user_info = client.get_user_info()

# 5. get_account_balance() - Get account balance
balance = client.get_account_balance("account_id", balance_type="CURRENT_OPEN")

# 6. get_positions() - Get open positions
positions = client.get_positions("account_id")

# 7. get_risk() - Get risk metrics
risk = client.get_risk("account_id")

# 8. get_fills() - Get trade fills
fills = client.get_fills("account_id")

# ============================================================================
# MARKET DATA (6 functions)
# ============================================================================

# 9. get_quotes() - Get real-time quotes
quotes = client.get_quotes(["XCME:ES.Z24", "XCME:NQ.Z24"])

# 10. get_depth() - Get market depth
depth = client.get_depth(["XCME:ES.Z24"])

# 11. get_trades() - Get historical trades
trades = client.get_trades(
    symbol="XCME:ES.Z24",
    from_time="20240101",
    to_time="20240131",
    max_records=100,
    earlier=True
)

# 12. get_security_definitions() - Get security info
sec_defs = client.get_security_definitions(["XCME:ES.Z24"])

# 13. get_security_margin() - Get margin requirements
margin = client.get_security_margin(["XCME:ES.Z24"])

# 14. get_security_status() - Get security status
status = client.get_security_status(["XCME:ES.Z24"])

# ============================================================================
# SYMBOL SEARCH (9 functions)
# ============================================================================

# 15. get_symbols() - Search symbols by text
symbols = client.get_symbols(text="ES", limit=10, prefer_active=True)

# 16. get_exchange_sources() - Get available exchanges
exchanges = client.get_exchange_sources()

# 17. get_complexes() - Get market complexes
complexes = client.get_complexes("CME")

# 18. search_futures() - Search futures contracts
futures = client.search_futures(exchange="CME", market_group="ES")

# 19. search_option_groups() - Search option groups
option_groups = client.search_option_groups(complex="ES")

# 20. search_options() - Search options
options = client.search_options(symbol="ES")

# 21. search_option_spreads() - Search option spreads
spreads = client.search_option_spreads(symbol="ES")

# 22. get_strategy_id() - Get strategy ID from order IDs
strategy_id = client.get_strategy_id("account_id", ["order1", "order2"])

# ============================================================================
# ORDER MANAGEMENT (8 functions)
# ============================================================================

# 23. place_order() - Place new order
order = {
    "accountId": "account_id",
    "exchSym": "XCME:ES.Z24",
    "side": "BUY",
    "quantity": 1,
    "orderType": "MARKET",
    "duration": "DAY"
}
response = client.place_order("account_id", order)

# 24. place_order() with bracket (SL/TP)
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
bracket_response = client.place_order("account_id", bracket_order)

# 25. update_order() - Modify existing order
update = {
    "orderId": "order_id",
    "quantity": 2,
    "limitPrice": 5010.0
}
update_response = client.update_order("account_id", "order_id", update)

# 26. cancel_order() - Cancel single order
cancel_response = client.cancel_order("account_id", "order_id")

# 27. cancel_multiple_orders() - Cancel multiple orders
multi_cancel = client.cancel_multiple_orders("account_id", ["order1", "order2"])

# 28. get_orders() - Get orders by status
orders = client.get_orders("account_id", order_status="WORKING")
all_orders = client.get_orders("account_id", order_status="ANY")

# 29. get_order_fills() - Get order fill history
order_fills = client.get_order_fills("account_id")

# 30. get_to_order_id() - Convert strategy ID to order ID
order_id = client.get_to_order_id("account_id", "strategy_id")

# 31. get_to_strategy_id() - Convert order ID to strategy ID
strat_id = client.get_to_strategy_id("account_id", "order_id")

# ============================================================================
# STREAMING (13 functions)
# ============================================================================

# 32. create_stream() - Create WebSocket stream
stream_id = client.create_stream()

# 33. subscribe_quotes() - Subscribe to quotes
client.subscribe_quotes(stream_id, ["XCME:ES.Z24", "XCME:NQ.Z24"])

# 34. subscribe_depths() - Subscribe to market depth
client.subscribe_depths(stream_id, ["XCME:ES.Z24"])

# 35. subscribe_trades() - Subscribe to trades
client.subscribe_trades(stream_id, ["XCME:ES.Z24"])

# 36. unsubscribe_quotes() - Unsubscribe from quotes
client.unsubscribe_quotes(stream_id, ["XCME:NQ.Z24"])

# 37. unsubscribe_depths() - Unsubscribe from depth
client.unsubscribe_depths(stream_id, ["XCME:ES.Z24"])

# 38. unsubscribe_trades() - Unsubscribe from trades
client.unsubscribe_trades(stream_id, ["XCME:ES.Z24"])

# 39. subscribe_tick_bars() - Subscribe to tick bar indicator
client.subscribe_tick_bars(stream_id, "XCME:ES.Z24", bar_size=100)

# 40. subscribe_trade_bars() - Subscribe to trade bar indicator
client.subscribe_trade_bars(stream_id, "XCME:ES.Z24", bar_size=50)

# 41. subscribe_time_bars() - Subscribe to time bar indicator
client.subscribe_time_bars(stream_id, "XCME:ES.Z24", bar_size=60)  # 60 seconds

# 42. subscribe_volume_bars() - Subscribe to volume bar indicator
client.subscribe_volume_bars(stream_id, "XCME:ES.Z24", bar_size=1000)

# 43. unsubscribe_indicator() - Unsubscribe from indicator
client.unsubscribe_indicator(stream_id, "indicator_id")

# ============================================================================
# SIMULATED ACCOUNTS (6 functions)
# ============================================================================

# 44. create_simulated_trader() - Create demo trader
trader_details = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "password": "password123",
    "templateId": "template_id",
    "address1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "zipCode": "10001",
    "phone": "555-1234"
}
trader = client.create_simulated_trader(trader_details)

# 45. add_simulated_account() - Add demo account
account_details = {
    "traderId": "trader_id",
    "password": "password123",
    "templateId": "template_id"
}
account = client.add_simulated_account(account_details)

# 46. simulated_account_reset() - Reset demo account
client.simulated_account_reset("account_id", "password")

# 47. simulated_account_expire() - Expire demo account
client.simulated_account_expire("account_id", "password")

# 48. simulated_account_add_cash() - Add cash to demo account
client.simulated_account_add_cash("account_id", "password", amount=10000, currency="USD")

# 49. simulated_account_get_cash_report() - Get cash report
cash_report = client.simulated_account_get_cash_report("account_id")

# ============================================================================
# ADVANCED STREAMING (WebSocket)
# ============================================================================

async def streaming_example():
    from ironbeam import IronBeamStream

    # Create stream object
    stream = IronBeamStream(client)

    # Set up callbacks
    async def on_quote(quote):
        print(f"Quote: {quote}")

    stream.on_quote(on_quote)

    # Connect
    await stream.connect()

    # Subscribe
    stream.subscribe_quotes(["XCME:ES.Z24"])

    # Listen
    await stream.listen()

# Run streaming
# asyncio.run(streaming_example())

# ============================================================================
# AUTO BREAKEVEN (Trade Management)
# ============================================================================

# Configure auto breakeven
breakeven_config = AutoBreakevenConfig(
    trigger_mode="ticks",
    trigger_levels=[20, 40, 60],
    sl_offsets=[10, 30, 50],
    enabled=True
)

# Create position state
position = PositionState(
    order_id="order_id",
    account_id="account_id",
    symbol="XCME:ES.Z24",
    side=OrderSide.BUY,
    entry_price=5000.0,
    quantity=1,
    current_stop_loss=4980.0
)

# Threaded execution
executor = ThreadedExecutor(client, "account_id", poll_interval=1.0)
executor.add_auto_breakeven("order_id", position, breakeven_config)
executor.start()

# Async execution
async def async_breakeven():
    async_executor = AsyncExecutor(client, "account_id")
    await async_executor.add_auto_breakeven("order_id", position, breakeven_config)
    await async_executor.start()

# asyncio.run(async_breakeven())

# ============================================================================
# RUNNING TAKE PROFIT (Trade Management)
# ============================================================================

# Configure running TP
tp_config = RunningTPConfig(
    enable_trailing_extremes=True,
    enable_profit_levels=True,
    profit_level_triggers=[30, 60, 90],
    extend_by_ticks=20,
    trail_offset_ticks=50,
    resistance_support_levels=[5100, 5150, 5200],
    enabled=True
)

# Add to executor
executor.add_running_tp("order_id", position, tp_config)

# Async execution
async def async_running_tp():
    async_executor = AsyncExecutor(client, "account_id")
    await async_executor.add_running_tp("order_id", position, tp_config)
    await async_executor.start()

# asyncio.run(async_running_tp())

# ============================================================================
# COMBINED TRADE MANAGEMENT
# ============================================================================

# Use both auto breakeven AND running TP together
async def combined_management():
    executor = AsyncExecutor(client, "account_id")
    await executor.add_auto_breakeven("order_id", position, breakeven_config)
    await executor.add_running_tp("order_id", position, tp_config)
    await executor.start()

# asyncio.run(combined_management())

# ============================================================================
# COMMON PATTERNS
# ============================================================================

# Pattern 1: Complete Trading Workflow
def complete_workflow():
    # Authenticate
    client.authenticate()

    # Check balance
    balance = client.get_account_balance("account_id")

    # Get quote
    quotes = client.get_quotes(["XCME:ES.Z24"])
    current_price = quotes['quotes'][0]['lastPrice']

    # Place order with bracket
    order = {
        "accountId": "account_id",
        "exchSym": "XCME:ES.Z24",
        "side": "BUY",
        "quantity": 1,
        "orderType": "MARKET",
        "stopLoss": current_price - 20,
        "takeProfit": current_price + 50,
        "duration": "DAY"
    }
    response = client.place_order("account_id", order)
    order_id = response['orderId']

    # Set up auto management
    position = PositionState(
        order_id=order_id,
        account_id="account_id",
        symbol="XCME:ES.Z24",
        side=OrderSide.BUY,
        entry_price=current_price,
        quantity=1
    )

    executor = ThreadedExecutor(client, "account_id")
    executor.add_auto_breakeven(order_id, position, breakeven_config)
    executor.add_running_tp(order_id, position, tp_config)
    executor.start()

# Pattern 2: Market Monitoring
def monitor_markets():
    # Get quotes for multiple symbols
    symbols = ["XCME:ES.Z24", "XCME:NQ.Z24", "XCME:YM.Z24"]
    quotes = client.get_quotes(symbols)

    for quote in quotes['quotes']:
        print(f"{quote['exchSym']}: Bid={quote['bidPrice']}, Ask={quote['askPrice']}")

# Pattern 3: Position Management
def manage_positions():
    positions = client.get_positions("account_id")

    for pos in positions['positions']:
        print(f"Position: {pos['exchSym']} | "
              f"Qty: {pos['quantity']} | "
              f"P&L: ${pos.get('unrealizedPL', 0):.2f}")

# Pattern 4: Order Status Check
def check_orders():
    working_orders = client.get_orders("account_id", "WORKING")
    filled_orders = client.get_orders("account_id", "FILLED")

    print(f"Working: {len(working_orders.get('orders', []))}")
    print(f"Filled: {len(filled_orders.get('orders', []))}")

"""
SUMMARY OF ALL FUNCTIONS:

AUTHENTICATION (2):
✅ authenticate()
✅ logout()

ACCOUNT (6):
✅ get_trader_info()
✅ get_user_info()
✅ get_account_balance()
✅ get_positions()
✅ get_risk()
✅ get_fills()

MARKET DATA (6):
✅ get_quotes()
✅ get_depth()
✅ get_trades()
✅ get_security_definitions()
✅ get_security_margin()
✅ get_security_status()

SYMBOL SEARCH (9):
✅ get_symbols()
✅ get_exchange_sources()
✅ get_complexes()
✅ search_futures()
✅ search_option_groups()
✅ search_options()
✅ search_option_spreads()
✅ get_strategy_id()

ORDER MANAGEMENT (8):
✅ place_order()
✅ update_order()
✅ cancel_order()
✅ cancel_multiple_orders()
✅ get_orders()
✅ get_order_fills()
✅ get_to_order_id()
✅ get_to_strategy_id()

STREAMING (13):
✅ create_stream()
✅ subscribe_quotes()
✅ subscribe_depths()
✅ subscribe_trades()
✅ unsubscribe_quotes()
✅ unsubscribe_depths()
✅ unsubscribe_trades()
✅ subscribe_tick_bars()
✅ subscribe_trade_bars()
✅ subscribe_time_bars()
✅ subscribe_volume_bars()
✅ unsubscribe_indicator()
✅ IronBeamStream (WebSocket class)

SIMULATED ACCOUNTS (6):
✅ create_simulated_trader()
✅ add_simulated_account()
✅ simulated_account_reset()
✅ simulated_account_expire()
✅ simulated_account_add_cash()
✅ simulated_account_get_cash_report()

TRADE MANAGEMENT:
✅ AutoBreakevenConfig
✅ AutoBreakevenManager
✅ RunningTPConfig
✅ RunningTPManager
✅ ThreadedExecutor
✅ AsyncExecutor
✅ PositionState

TOTAL: 48 API Functions + 7 Trade Management Features = 55 Features
"""
