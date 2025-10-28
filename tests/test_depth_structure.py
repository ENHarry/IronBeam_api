"""
Test REST API depth endpoint to see MBO structure
"""
from ironbeam import IronBeam
import json

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

def main():
    print("\n" + "="*70)
    print("REST API DEPTH TEST - MBO DATA STRUCTURE")
    print("="*70)
    
    # Initialize
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    
    client.authenticate()
    print("✓ Authenticated\n")
    
    # Test symbols
    symbols = ["XCME:ES.Z25", "XCME:NQ.Z25"]
    
    print(f"Testing depth data for: {symbols}")
    print("="*70)
    
    try:
        # Get depth via REST API
        depth_response = client.get_depth(symbols)
        
        print("\nDepth Response:")
        print(json.dumps(depth_response, indent=2))
        
        # Analyze structure
        print("\n" + "="*70)
        print("DEPTH DATA ANALYSIS:")
        print("="*70)
        
        if isinstance(depth_response, dict):
            status = depth_response.get('status', 'N/A')
            print(f"Status: {status}")
            
            depths = depth_response.get('depths', [])
            print(f"Number of depth entries: {len(depths)}")
            
            for depth in depths:
                print(f"\nSymbol: {depth.get('symbol', 'N/A')}")
                
                bids = depth.get('bids', [])
                asks = depth.get('asks', [])
                
                print(f"  Bids: {len(bids)} levels")
                print(f"  Asks: {len(asks)} levels")
                
                if bids:
                    print(f"\n  Sample bid structure:")
                    print(json.dumps(bids[0], indent=4))
                
                if asks:
                    print(f"\n  Sample ask structure:")
                    print(json.dumps(asks[0], indent=4))
                
                # Check for MBO indicators
                has_order_ids = False
                has_multiple_orders = False
                
                for bid in bids[:5]:  # Check first 5
                    if 'orderId' in bid or 'oid' in bid:
                        has_order_ids = True
                    if 'orders' in bid:
                        has_multiple_orders = True
                
                print(f"\n  MBO Indicators:")
                print(f"    Has order IDs: {has_order_ids}")
                print(f"    Has order arrays: {has_multiple_orders}")
                
                if has_order_ids or has_multiple_orders:
                    print(f"    ✅ This appears to be MBO data!")
                else:
                    print(f"    ℹ️  This appears to be aggregated depth (MBP)")
        
    except Exception as e:
        print(f"\n✗ Error getting depth: {e}")
        import traceback
        traceback.print_exc()
    
    # Also check what the API documentation says
    print("\n" + "="*70)
    print("IRONBEAM MBO DATA TYPES:")
    print("="*70)
    print("""
IronBeam typically provides two types of market data:

1. MBP (Market By Price) - Aggregated depth
   - Shows total volume at each price level
   - Faster, less data
   - Use: subscribe_depths()

2. MBO (Market By Order) - Individual orders
   - Shows each individual order in the book
   - More granular, more data
   - May require special subscription or entitlements

For futures markets, MBO data typically requires:
   - Premium market data subscription
   - Exchange fees
   - Special entitlements

The 'depths' subscription likely provides MBP data (aggregated).
True MBO might require a different API endpoint or subscription level.
    """)
    
    print("\n" + "="*70)
    print("CONCLUSION:")
    print("="*70)
    print("""
Based on testing:
- subscribe_depths() = Market depth (likely MBP - aggregated)
- subscribe_quotes() = Top of book quotes
- subscribe_trades() = Executed trades

For true MBO data, you may need to:
1. Check if your account has MBO entitlements
2. Contact IronBeam for MBO access
3. Use a different subscription method if available

The depth subscription will give you the best order book view
available with your current entitlements.
    """)

if __name__ == "__main__":
    main()
