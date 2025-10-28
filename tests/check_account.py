"""
Quick check of current account status after order test
"""
from ironbeam import IronBeam
import json

DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

def main():
    print("\n" + "="*70)
    print("ACCOUNT STATUS CHECK")
    print("="*70)
    
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    
    client.authenticate()
    
    trader_info = client.get_trader_info()
    account_id = trader_info['accounts'][0]
    
    # Check balance
    print("\n💰 BALANCE:")
    balance_data = client.get_account_balance(account_id)
    balance = balance_data['balances'][0]
    print(f"  Cash Balance: ${balance['cashBalance']:,.2f}")
    print(f"  Available: ${balance['cashBalanceAvailable']:,.2f}")
    print(f"  Total Equity: ${balance['totalEquity']:,.2f}")
    print(f"  Open Trade Equity: ${balance.get('openTradeEquity', 0):,.2f}")
    
    # Check positions
    print("\n📊 POSITIONS:")
    positions_data = client.get_positions(account_id)
    positions = positions_data.get('positions', [])
    
    if positions:
        for pos in positions:
            print(f"\n  Symbol: {pos.get('exchSym', 'N/A')}")
            print(f"  Net Position: {pos.get('netPosition', 0)}")
            print(f"  Long: {pos.get('longQuantity', 0)} @ ${pos.get('longAvgPrice', 0)}")
            print(f"  Short: {pos.get('shortQuantity', 0)} @ ${pos.get('shortAvgPrice', 0)}")
            print(f"  Unrealized PnL: ${pos.get('unrealizedPnl', 0):,.2f}")
    else:
        print("  No open positions")
    
    # Check open orders
    print("\n📋 OPEN ORDERS:")
    orders_response = client.get_orders(account_id, "WORKING")
    orders = orders_response.get('orders', [])
    
    if orders:
        working_orders = [o for o in orders if o.get('status') in ['NEW', 'PARTIALLY_FILLED', 'PENDING_NEW']]
        filled_orders = [o for o in orders if o.get('status') == 'FILLED']
        cancelled_orders = [o for o in orders if o.get('status') == 'CANCELLED']
        
        print(f"  Working: {len(working_orders)}")
        print(f"  Filled: {len(filled_orders)}")
        print(f"  Cancelled: {len(cancelled_orders)}")
        
        if working_orders:
            print("\n  Active orders:")
            for order in working_orders:
                print(f"    {order.get('side')} {order.get('quantity')} {order.get('exchSym')} @ {order.get('limitPrice')}")
    else:
        print("  No orders")
    
    # Check fills
    print("\n✅ FILLS (last 5):")
    fills_response = client.get_fills(account_id)
    fills = fills_response.get('fills', [])
    
    if fills:
        for fill in fills[:5]:
            print(f"  {fill.get('fillDate', 'N/A')}")
            print(f"    {fill.get('side')} {fill.get('quantity')} {fill.get('exchSym')} @ ${fill.get('price')}")
            print(f"    Fill ID: {fill.get('fillId')}")
            print()
    else:
        print("  No fills")
    
    print("\n" + "="*70)
    
    # If we have a position, offer to close it
    if positions:
        print("\n⚠️  YOU HAVE AN OPEN POSITION!")
        print("   You may want to close it to avoid risk.")
        print("\n   To close the position, you would place an offsetting order.")
        print("   (Not automated in this test script)")

if __name__ == "__main__":
    main()
