"""
Example 2: Account Management
Demonstrates account balance, positions, risk, and fills
"""
from ironbeam import IronBeam, AccountBalanceRequest, BalanceType

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"


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


def example_account_balance(client, account_id):
    """Get account balance with different methods."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Account Balance")
    print("="*70)

    # Method 1: Simple string parameter (legacy)
    print("\n1. Using simple string parameter:")
    balance = client.get_account_balance(account_id)

    print(f"  Account ID: {account_id}")
    print(f"  Status: {balance.status}")

    for bal in balance.balances:
        print(f"\n  Currency: {bal.currency_code}")
        print(f"  Cash Balance: ${bal.cash_balance:,.2f}")
        print(f"  Open Trade Equity: ${bal.open_trade_equity:,.2f}")
        if bal.unrealized_pl is not None:
            print(f"  Unrealized P&L: ${bal.unrealized_pl:,.2f}")
        if bal.margin_balance is not None:
            print(f"  Margin Balance: ${bal.margin_balance:,.2f}")
        if bal.available_for_trading is not None:
            print(f"  Available for Trading: ${bal.available_for_trading:,.2f}")

    # Method 2: Typed request with specific balance type
    print("\n2. Using typed AccountBalanceRequest:")
    balance_req = AccountBalanceRequest(
        account_id=account_id,
        balance_type=BalanceType.CURRENT_OPEN
    )
    balance2 = client.get_account_balance(balance_req)

    print(f"  ✓ Retrieved {BalanceType.CURRENT_OPEN.value} balance")
    print(f"  Cash Balance: ${balance2.balances[0].cash_balance:,.2f}")


def example_positions(client, account_id):
    """Get and display current positions."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Positions")
    print("="*70)

    positions = client.get_positions(account_id)

    print(f"  Total Positions: {len(positions.positions)}")

    if len(positions.positions) == 0:
        print("  No open positions")
    else:
        for i, pos in enumerate(positions.positions, 1):
            print(f"\n  Position {i}:")
            print(f"    Symbol: {pos.exch_sym}")
            print(f"    Side: {pos.side}")  # LONG or SHORT
            print(f"    Quantity: {pos.quantity}")
            print(f"    Entry Price: ${pos.price:,.2f}")

            if pos.unrealized_pl is not None:
                pnl_color = "profit" if pos.unrealized_pl >= 0 else "loss"
                print(f"    Unrealized P&L: ${pos.unrealized_pl:,.2f} ({pnl_color})")

            if pos.date_opened:
                print(f"    Opened: {pos.date_opened}")

def example_risk(client, account_id):
    """Get and display risk information."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Risk Management")
    print("="*70)

    risk = client.get_risk(account_id)

    print(f"  Status: {risk.status}")
    print(f"  Total Risk Entries: {len(risk.risks)}")

    # Show all risk entries
    for i, r in enumerate(risk.risks, 1):
        print(f"\n  Risk Entry {i}:")
        print(f"    Account: {r.account_id}")

        if r.reg_code:
            print(f"    Regulation: {r.reg_code}")
        if r.currency_code:
            print(f"    Currency: {r.currency_code}")
        if r.liquidation_value is not None:
            print(f"    Liquidation Value: ${r.liquidation_value:,.2f}")
        if r.margin_requirement is not None:
            print(f"    Margin Requirement: ${r.margin_requirement:,.2f}")
        if r.buying_power is not None:
            print(f"    Buying Power: ${r.buying_power:,.2f}")

    # Convenience access to first risk entry
    if risk.risk:
        print(f"\n  ✓ Primary Account: {risk.risk.account_id}")


def example_fills(client, account_id):
    """Get and display fill history."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Fill History")
    print("="*70)

    fills = client.get_fills(account_id)

    print(f"  Total Fills: {len(fills.fills)}")

    if len(fills.fills) == 0:
        print("  No fills in history")
    else:
        # Group fills by symbol
        fills_by_symbol = {}
        for fill in fills.fills:
            symbol = fill.exch_sym
            if symbol not in fills_by_symbol:
                fills_by_symbol[symbol] = []
            fills_by_symbol[symbol].append(fill)

        print(f"\n  Symbols with fills: {len(fills_by_symbol)}")

        # Show recent fills (last 5)
        print(f"\n  Recent Fills (last 5):")
        for i, fill in enumerate(fills.fills[:5], 1):
            print(f"\n  Fill {i}:")
            if fill.fill_id:
                print(f"    Fill ID: {fill.fill_id}")
            print(f"    Order ID: {fill.order_id}")
            print(f"    Symbol: {fill.exch_sym}")
            print(f"    Side: {fill.side}")  # BUY or SELL
            print(f"    Quantity: {fill.quantity}")
            if fill.price is not None:
                print(f"    Fill Price: ${fill.price:,.2f}")
            if fill.fill_time:
                print(f"    Fill Time: {fill.fill_time}")

        # Show summary by symbol
        print(f"\n  Summary by Symbol:")
        for symbol, symbol_fills in fills_by_symbol.items():
            buy_qty = sum(f.quantity for f in symbol_fills if f.side.value == "BUY")
            sell_qty = sum(f.quantity for f in symbol_fills if f.side.value == "SELL")
            net = buy_qty - sell_qty

            print(f"\n    {symbol}:")
            print(f"      Total Fills: {len(symbol_fills)}")
            print(f"      Buy Quantity: {buy_qty}")
            print(f"      Sell Quantity: {sell_qty}")
            print(f"      Net Position: {net:+.0f}")


def example_account_summary(client, account_id):
    """Comprehensive account summary."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Complete Account Summary")
    print("="*70)

    # Get all account data
    trader = client.get_trader_info()
    balance = client.get_account_balance(account_id)
    positions = client.get_positions(account_id)
    risk = client.get_risk(account_id)
    fills = client.get_fills(account_id)

    # Display summary
    print(f"\n  ACCOUNT: {account_id}")
    print(f"  Trader ID: {trader.trader_id}")
    print(f"  Account Type: {'LIVE' if trader.is_live else 'DEMO'}")

    print(f"\n  BALANCE:")
    bal = balance.balances[0]
    print(f"    Cash: ${bal.cash_balance:,.2f}")
    print(f"    Open Trade Equity: ${bal.open_trade_equity:,.2f}")

    print(f"\n  POSITIONS:")
    print(f"    Open Positions: {len(positions.positions)}")
    if positions.positions:
        total_value = sum(pos.quantity * pos.price for pos in positions.positions)
        print(f"    Total Position Value: ${total_value:,.2f}")

    print(f"\n  RISK:")
    if risk.risks:
        r = risk.risks[0]
        if r.margin_requirement is not None:
            print(f"    Margin Requirement: ${r.margin_requirement:,.2f}")
        if r.buying_power is not None:
            print(f"    Buying Power: ${r.buying_power:,.2f}")

    print(f"\n  ACTIVITY:")
    print(f"    Total Fills: {len(fills.fills)}")

    print(f"\n  ✓ Account summary complete")


def main():
    """Run all account management examples."""
    print("\n" + "="*70)
    print("IRONBEAM SDK - ACCOUNT MANAGEMENT EXAMPLES")
    print("="*70)

    # Setup
    client, account_id = setup_client()
    print(f"\n✓ Authenticated - Account: {account_id}")

    # Run examples
    example_account_balance(client, account_id)
    example_positions(client, account_id)
    example_risk(client, account_id)
    example_fills(client, account_id)
    example_account_summary(client, account_id)

    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Balance can be retrieved with simple string or typed request")
    print("  2. Positions show all open trades with P&L")
    print("  3. Risk info includes margin and buying power")
    print("  4. Fills provide complete trade history")
    print("  5. All responses are fully typed with Pydantic models")


if __name__ == "__main__":
    main()
