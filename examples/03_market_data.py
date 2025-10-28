"""
Example 3: Market Data
Demonstrates quotes, market depth, trades, and symbol search
"""
from ironbeam import IronBeam

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

# Test symbols
SYMBOLS = ["XCEC:MGC.Z25", "XCME:ES.Z25", "XCME:NQ.Z25"]


def setup_client():
    """Initialize and authenticate client."""
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    client.authenticate()
    return client


def example_quotes(client):
    """Get real-time quotes for symbols."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Market Quotes")
    print("="*70)

    print(f"\n  Requesting quotes for {len(SYMBOLS)} symbols...")

    quotes = client.get_quotes(SYMBOLS)

    print(f"  Status: {quotes.status}")
    print(f"  Quotes received: {len(quotes.quotes)}")

    for quote in quotes.quotes:
        print(f"\n  Symbol: {quote.exch_sym}")

        if quote.last_price:
            print(f"    Last: ${quote.last_price:,.2f}")

        if quote.bid_price and quote.ask_price:
            spread = quote.ask_price - quote.bid_price
            print(f"    Bid: ${quote.bid_price:,.2f} x {quote.bid_size or 'N/A'}")
            print(f"    Ask: ${quote.ask_price:,.2f} x {quote.ask_size or 'N/A'}")
            print(f"    Spread: ${spread:.2f}")

        if quote.open_price:
            print(f"    Open: ${quote.open_price:,.2f}")
        if quote.high_price:
            print(f"    High: ${quote.high_price:,.2f}")
        if quote.low_price:
            print(f"    Low: ${quote.low_price:,.2f}")

        if quote.change:
            change_pct = (quote.change / quote.last_price * 100) if quote.last_price else 0
            print(f"    Change: ${quote.change:+,.2f} ({change_pct:+.2f}%)")

        if quote.volume:
            print(f"    Volume: {quote.volume:,}")


def example_market_depth(client):
    """Get market depth (order book) data."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Market Depth (Order Book)")
    print("="*70)

    symbol = SYMBOLS[0]  # Use Micro Gold
    print(f"\n  Requesting market depth for {symbol}...")

    depth_response = client.get_depth([symbol])

    print(f"  Status: {depth_response.status}")

    if depth_response.depths:
        depth = depth_response.depths[0]
        print(f"\n  Symbol: {depth.exch_sym}")

        # Display bid side
        print(f"\n  BID SIDE (Top 5):")
        for i, level in enumerate(depth.bids[:5], 1):
            print(f"    {i}. ${level.price:,.2f} x {level.size}")

        # Display ask side
        print(f"\n  ASK SIDE (Top 5):")
        for i, level in enumerate(depth.asks[:5], 1):
            print(f"    {i}. ${level.price:,.2f} x {level.size}")

        # Calculate bid/ask spread
        if depth.bids and depth.asks:
            best_bid = depth.bids[0].price
            best_ask = depth.asks[0].price
            spread = best_ask - best_bid
            mid_price = (best_bid + best_ask) / 2

            print(f"\n  SPREAD ANALYSIS:")
            print(f"    Best Bid: ${best_bid:,.2f}")
            print(f"    Best Ask: ${best_ask:,.2f}")
            print(f"    Spread: ${spread:.2f}")
            print(f"    Mid Price: ${mid_price:,.2f}")
    else:
        print("  No depth data available")


def example_symbol_search(client):
    """Search for symbols by keyword."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Symbol Search")
    print("="*70)

    keywords = ["gold", "oil", "es"]

    for keyword in keywords:
        print(f"\n  Searching for '{keyword}'...")

        result = client.get_symbols(keyword, limit=5, prefer_active=True)

        print(f"  Found {len(result['symbols'])} results:")

        for sym in result['symbols']:
            symbol = sym.get('symbol', 'N/A')
            desc = sym.get('description', 'N/A')
            currency = sym.get('currency', 'N/A')
            sym_type = sym.get('symbolType', 'N/A')

            print(f"    {symbol:<25} {desc:<40} [{sym_type}, {currency}]")


def example_futures_search(client):
    """Search for futures contracts."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Futures Search")
    print("="*70)

    exchanges = [
        ("CME", "ES"),      # E-mini S&P 500
        ("COMEX", "MGC"),   # Micro Gold
        ("NYMEX", "CL")     # Crude Oil
    ]

    for exchange, product in exchanges:
        print(f"\n  Searching {exchange} for {product} futures...")

        try:
            result = client.search_futures(exchange, product)

            symbols = result.get('symbols', [])
            print(f"  Found {len(symbols)} contracts:")

            # Show first 5 contracts
            for sym in symbols[:5]:
                symbol = sym.get('symbol', 'N/A')
                month = sym.get('maturityMonth', 'N/A')
                year = sym.get('maturityYear', 'N/A')
                desc = sym.get('description', 'N/A')

                print(f"    {symbol:<15} {month} {year} - {desc}")

            if len(symbols) > 5:
                print(f"    ... and {len(symbols) - 5} more contracts")

        except Exception as e:
            print(f"  Error: {e}")


def example_security_definitions(client):
    """Get detailed security definitions."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Security Definitions")
    print("="*70)

    symbols_to_check = [SYMBOLS[0]]  # Just check Micro Gold

    print(f"\n  Getting security definitions for {len(symbols_to_check)} symbol(s)...")

    try:
        defs = client.get_security_definitions(symbols_to_check)

        print(f"  Status: {defs.status}")

        for sec_def in defs.security_definitions:
            print(f"\n  Symbol: {sec_def.exch_sym}")
            print(f"    Currency: {sec_def.currency}")
            print(f"    Description: {sec_def.description}")

            if sec_def.contract_size:
                print(f"    Contract Size: {sec_def.contract_size}")
            if sec_def.tick_size:
                print(f"    Tick Size: {sec_def.tick_size}")
            if sec_def.tick_value:
                print(f"    Tick Value: ${sec_def.tick_value}")

            if sec_def.exchange:
                print(f"    Exchange: {sec_def.exchange}")
            if sec_def.product_type:
                print(f"    Product Type: {sec_def.product_type}")

    except Exception as e:
        print(f"  Error: {e}")


def example_popular_symbols(client):
    """Get curated list of popular symbols."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Popular Symbols")
    print("="*70)

    popular = client.get_popular_symbols()

    print("\n  EQUITY INDICES:")
    for sym in popular['equity_indices']:
        print(f"    {sym['symbol']:<20} {sym['name']:<35} [{sym['exchange']}]")

    print("\n  PRECIOUS METALS:")
    for sym in popular['commodities']['precious_metals']:
        print(f"    {sym['symbol']:<20} {sym['name']:<35} [{sym['exchange']}]")

    print("\n  ENERGY:")
    for sym in popular['commodities']['energy']:
        print(f"    {sym['symbol']:<20} {sym['name']:<35} [{sym['exchange']}]")

    print("\n  CURRENCIES:")
    for sym in popular['currencies']:
        print(f"    {sym['symbol']:<20} {sym['name']:<35} [{sym['exchange']}]")


def example_market_data_combination(client):
    """Combine multiple market data calls for analysis."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Combined Market Analysis")
    print("="*70)

    symbol = "XCEC:MGC.Z25"
    print(f"\n  Analyzing {symbol}...")

    # Get quote
    quotes = client.get_quotes([symbol])
    quote = quotes.quotes[0] if quotes.quotes else None

    # Get depth
    depth_resp = client.get_depth([symbol])
    depth = depth_resp.depths[0] if depth_resp.depths else None

    # Get definition
    try:
        defs = client.get_security_definitions([symbol])
        sec_def = defs.security_definitions[0] if defs.security_definitions else None
    except:
        sec_def = None

    # Display combined analysis
    print(f"\n  SYMBOL: {symbol}")

    if sec_def:
        print(f"  Description: {sec_def.description}")
        print(f"  Exchange: {sec_def.exchange}")

    if quote:
        print(f"\n  CURRENT PRICE:")
        print(f"    Last: ${quote.last_price:,.2f}")
        if quote.change:
            print(f"    Change: ${quote.change:+,.2f}")
        if quote.volume:
            print(f"    Volume: {quote.volume:,}")

    if depth and depth.bids and depth.asks:
        best_bid = depth.bids[0].price
        best_ask = depth.asks[0].price
        bid_size = depth.bids[0].size
        ask_size = depth.asks[0].size

        print(f"\n  ORDER BOOK:")
        print(f"    Best Bid: ${best_bid:,.2f} x {bid_size}")
        print(f"    Best Ask: ${best_ask:,.2f} x {ask_size}")
        print(f"    Spread: ${best_ask - best_bid:.2f}")

        # Calculate liquidity
        total_bid_liquidity = sum(level.size for level in depth.bids[:10])
        total_ask_liquidity = sum(level.size for level in depth.asks[:10])

        print(f"\n  LIQUIDITY (Top 10 levels):")
        print(f"    Bid Liquidity: {total_bid_liquidity}")
        print(f"    Ask Liquidity: {total_ask_liquidity}")


def main():
    """Run all market data examples."""
    print("\n" + "="*70)
    print("IRONBEAM SDK - MARKET DATA EXAMPLES")
    print("="*70)

    # Setup
    client = setup_client()
    print("\n✓ Authenticated")

    # Run examples
    example_quotes(client)
    example_market_depth(client)
    example_symbol_search(client)
    example_futures_search(client)
    example_security_definitions(client)
    example_popular_symbols(client)
    example_market_data_combination(client)

    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Quotes provide last price, bid/ask, and volume")
    print("  2. Market depth shows full order book")
    print("  3. Symbol search finds contracts by keyword")
    print("  4. Futures search finds contracts by exchange and product")
    print("  5. Security definitions provide contract specifications")
    print("  6. Combine multiple data sources for comprehensive analysis")


if __name__ == "__main__":
    main()
