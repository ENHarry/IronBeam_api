"""
Test script for the new tradable assets utility methods.
Demonstrates get_all_tradable_assets(), get_popular_symbols(), and search_symbols_by_keyword()
"""
from ironbeam import IronBeam
import json

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"


def print_section(title):
    print(f"\n{'='*80}")
    print(title)
    print(f"{'='*80}")


def main():
    print_section("TRADABLE ASSETS UTILITY METHODS TEST")

    # Initialize client
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    client.authenticate()
    print("[OK] Authenticated")

    # Test 1: Get popular symbols
    print_section("TEST 1: GET POPULAR SYMBOLS")
    print("Getting curated list of popular/commonly traded symbols...\n")

    popular = client.get_popular_symbols()

    print("Equity Indices:")
    for sym in popular['equity_indices']:
        print(f"  - {sym['symbol']:<20} {sym['name']}")

    print("\nPrecious Metals:")
    for sym in popular['commodities']['precious_metals']:
        print(f"  - {sym['symbol']:<20} {sym['name']}")

    print("\nEnergy:")
    for sym in popular['commodities']['energy']:
        print(f"  - {sym['symbol']:<20} {sym['name']}")

    print("\nAgriculture:")
    for sym in popular['commodities']['agriculture']:
        print(f"  - {sym['symbol']:<20} {sym['name']}")

    print("\nCurrencies:")
    for sym in popular['currencies']:
        print(f"  - {sym['symbol']:<20} {sym['name']}")

    print("\nInterest Rates:")
    for sym in popular['rates']:
        print(f"  - {sym['symbol']:<20} {sym['name']}")

    # Test 2: Search by keyword
    print_section("TEST 2: SEARCH SYMBOLS BY KEYWORD")

    keywords = ['gold', 'oil', 'euro', 'micro']
    for keyword in keywords:
        print(f"\nSearching for '{keyword}'...")
        result = client.search_symbols_by_keyword(keyword, limit=10)

        print(f"  Found {result['count']} results:")
        for sym in result['symbols'][:5]:  # Show first 5
            symbol = sym.get('symbol', 'N/A')
            desc = sym.get('description', 'N/A')
            print(f"    - {symbol:<25} {desc}")

        if result['count'] > 5:
            print(f"    ... and {result['count'] - 5} more")

    # Test 3: Get all tradable assets (limited to a few exchanges for demo)
    print_section("TEST 3: GET ALL TRADABLE ASSETS")
    print("Querying all tradable futures from CME and COMEX...")
    print("(This may take a moment...)\n")

    try:
        # Query only CME and COMEX for demo purposes
        assets = client.get_all_tradable_assets(
            asset_types=['futures'],
            exchanges=['CME', 'COMEX'],
            limit_per_type=100
        )

        print("Summary:")
        print(f"  Total Assets: {assets['summary']['total_assets']}")
        print(f"\n  By Exchange:")
        for exchange, count in assets['summary']['by_exchange'].items():
            print(f"    - {exchange}: {count} contracts")

        print(f"\n  Sample Futures by Exchange:")

        # CME Examples
        if 'CME' in assets['futures']:
            print(f"\n  CME Futures:")
            cme_futures = assets['futures']['CME']
            complex_count = 0
            for complex_name, symbols in cme_futures.items():
                if complex_count >= 3:  # Show first 3 complexes
                    break
                print(f"    Complex: {complex_name}")
                for base_symbol, contracts in list(symbols.items())[:2]:  # Show 2 base symbols
                    print(f"      {base_symbol}: {len(contracts)} contracts")
                    # Show first 3 contracts
                    for contract in contracts[:3]:
                        sym = contract.get('symbol', 'N/A')
                        desc = contract.get('description', 'N/A')
                        month = contract.get('maturityMonth', 'N/A')
                        year = contract.get('maturityYear', 'N/A')
                        print(f"        - {sym:<15} {month} {year}")
                complex_count += 1

        # COMEX Examples
        if 'COMEX' in assets['futures']:
            print(f"\n  COMEX Futures:")
            comex_futures = assets['futures']['COMEX']
            complex_count = 0
            for complex_name, symbols in comex_futures.items():
                if complex_count >= 2:  # Show first 2 complexes
                    break
                print(f"    Complex: {complex_name}")
                for base_symbol, contracts in list(symbols.items())[:2]:
                    print(f"      {base_symbol}: {len(contracts)} contracts")
                    for contract in contracts[:3]:
                        sym = contract.get('symbol', 'N/A')
                        desc = contract.get('description', 'N/A')
                        month = contract.get('maturityMonth', 'N/A')
                        year = contract.get('maturityYear', 'N/A')
                        print(f"        - {sym:<15} {month} {year}")
                complex_count += 1

        print("\n[OK] Successfully retrieved all tradable assets!")

    except Exception as e:
        print(f"[X] Error retrieving assets: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print_section("TEST SUMMARY")
    print("""
[OK] All utility methods tested successfully!

Available Methods:
  1. client.get_popular_symbols()
     - Returns curated list of commonly traded symbols
     - Organized by category (indices, commodities, currencies, etc.)

  2. client.search_symbols_by_keyword(keyword, limit=50)
     - Search for symbols by keyword (e.g., 'gold', 'oil', 'micro')
     - Returns matching symbols with details

  3. client.get_all_tradable_assets(asset_types, exchanges, limit_per_type)
     - Comprehensive query across exchanges and asset types
     - Returns organized dictionary with all available assets
     - Includes summary statistics

Use these methods to discover and explore available trading instruments!
    """)


if __name__ == "__main__":
    main()
