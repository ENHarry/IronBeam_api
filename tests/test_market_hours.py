"""
Market Hours Test - Run this during active trading hours
to see depth/MBO data structure

ES Futures Trading Hours (Central Time):
Sunday 5:00 PM - Friday 4:00 PM
Daily maintenance: 4:00 PM - 5:00 PM
"""
import asyncio
import json
from datetime import datetime
from ironbeam import IronBeam, IronBeamStream

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

async def main():
    print("\n" + "="*70)
    print("MARKET HOURS TEST - DEPTH DATA ANALYSIS")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nES Trading Hours: Sun 5PM - Fri 4PM CT (Daily break 4-5PM)")
    print("="*70)
    
    # Initialize
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    
    client.authenticate()
    print("✓ Authenticated")
    
    # Symbol to test
    symbol = "XCME:ES.Z25"
    
    # Data collectors
    depth_messages = []
    quote_messages = []
    trade_messages = []
    other_messages = []
    
    # Message handler
    async def on_message(msg):
        if isinstance(msg, dict):
            # Categorize message
            if 'd' in msg:
                depth_messages.append(msg)
                if len(depth_messages) == 1:
                    print(f"\n{'='*70}")
                    print("🎯 FIRST DEPTH MESSAGE RECEIVED!")
                    print(f"{'='*70}")
                    print(json.dumps(msg, indent=2))
                    
                    # Analyze structure
                    print(f"\n{'='*70}")
                    print("DEPTH DATA STRUCTURE ANALYSIS:")
                    print(f"{'='*70}")
                    
                    for depth in msg['d']:
                        symbol_name = depth.get('s', 'N/A')
                        bids = depth.get('bids', depth.get('b', []))
                        asks = depth.get('asks', depth.get('a', []))
                        
                        print(f"\nSymbol: {symbol_name}")
                        print(f"Bid levels: {len(bids)}")
                        print(f"Ask levels: {len(asks)}")
                        
                        if bids:
                            print(f"\nFirst bid structure:")
                            print(json.dumps(bids[0], indent=2))
                            
                            # Check for MBO indicators
                            first_bid = bids[0]
                            has_order_id = 'orderId' in first_bid or 'oid' in first_bid
                            has_position = 'position' in first_bid or 'pos' in first_bid
                            has_orders = 'orders' in first_bid
                            
                            print(f"\nMBO Indicators:")
                            print(f"  Has order ID: {has_order_id}")
                            print(f"  Has position: {has_position}")
                            print(f"  Has orders array: {has_orders}")
                            
                            if has_order_id or has_orders:
                                print(f"\n✅ THIS IS MBO (Market By Order) DATA!")
                                print(f"   Each order is visible individually")
                            else:
                                print(f"\nℹ️  THIS IS MBP (Market By Price) DATA")
                                print(f"   Orders are aggregated by price level")
                        
                        if asks:
                            print(f"\nFirst ask structure:")
                            print(json.dumps(asks[0], indent=2))
                
                elif len(depth_messages) % 10 == 0:
                    print(f"  Depth messages received: {len(depth_messages)}")
                    
            elif 'q' in msg:
                quote_messages.append(msg)
                if len(quote_messages) == 1:
                    print(f"\n✓ First quote received")
            elif 't' in msg:
                trade_messages.append(msg)
                if len(trade_messages) == 1:
                    print(f"\n✓ First trade received")
                    print(json.dumps(msg, indent=2)[:300])
            elif 'p' not in msg and 'b' not in msg:
                other_messages.append(msg)
    
    # Initialize stream
    stream = IronBeamStream(client)
    stream.on_message(on_message)
    
    print(f"\nConnecting to stream...")
    await stream.connect()
    print(f"✓ Connected (Stream ID: {stream.stream_id})")
    
    # Subscribe to all data types
    print(f"\nSubscribing to {symbol}...")
    
    try:
        stream.subscribe_quotes([symbol])
        print(f"  ✓ Quotes")
    except Exception as e:
        print(f"  ✗ Quotes: {e}")
    
    try:
        stream.subscribe_depths([symbol])
        print(f"  ✓ Depth (This should give MBO/MBP)")
    except Exception as e:
        print(f"  ✗ Depth: {e}")
    
    try:
        stream.subscribe_trades([symbol])
        print(f"  ✓ Trades")
    except Exception as e:
        print(f"  ✗ Trades: {e}")
    
    # Listen for data
    print(f"\n{'='*70}")
    print("LISTENING FOR DATA (30 seconds)")
    print(f"{'='*70}")
    print("Waiting for market data...")
    print("(If no data appears, market may be closed or data unavailable)")
    
    listen_task = asyncio.create_task(stream.listen())
    
    # Wait with progress
    for i in range(30):
        await asyncio.sleep(1)
        if i % 5 == 4:
            print(f"\n  {i+1}s - Depth:{len(depth_messages)} Quotes:{len(quote_messages)} Trades:{len(trade_messages)}")
    
    # Stop
    listen_task.cancel()
    try:
        await listen_task
    except asyncio.CancelledError:
        pass
    
    # Final summary
    print(f"\n{'='*70}")
    print("SESSION SUMMARY")
    print(f"{'='*70}")
    print(f"Duration: 30 seconds")
    print(f"Depth messages: {len(depth_messages)}")
    print(f"Quote messages: {len(quote_messages)}")
    print(f"Trade messages: {len(trade_messages)}")
    print(f"Other messages: {len(other_messages)}")
    
    if depth_messages:
        print(f"\n✅ SUCCESS! Depth data received.")
        print(f"   Check the analysis above to see if it's MBO or MBP.")
    elif quote_messages or trade_messages:
        print(f"\n⚠️  Quotes/trades received but no depth data.")
        print(f"   Depth may require special entitlements.")
    else:
        print(f"\n⚠️  No market data received.")
        print(f"   Possible reasons:")
        print(f"   - Market is closed")
        print(f"   - Demo account has limited data access")
        print(f"   - Symbol not available for streaming")
        print(f"\n   Try again during market hours or with live account.")
    
    await stream.close()
    
    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print(f"{'='*70}")
    
    # Save results if we got depth data
    if depth_messages:
        filename = f"depth_data_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'depth_messages': depth_messages[:5],  # First 5
                'quote_messages': quote_messages[:5],
                'trade_messages': trade_messages[:5],
                'summary': {
                    'total_depth': len(depth_messages),
                    'total_quotes': len(quote_messages),
                    'total_trades': len(trade_messages)
                }
            }, f, indent=2)
        print(f"\n✅ Sample data saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
