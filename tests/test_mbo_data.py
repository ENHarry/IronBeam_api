"""
Test to identify which subscription provides MBO (Market By Order) data
Tests quotes, trades, and depth subscriptions separately
"""
import asyncio
import json
from ironbeam import IronBeam, IronBeamStream

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

async def test_subscription(client, sub_type, symbol):
    """Test a specific subscription type"""
    print(f"\n{'='*70}")
    print(f"TESTING: {sub_type.upper()} SUBSCRIPTION")
    print(f"Symbol: {symbol}")
    print(f"{'='*70}")
    
    stream = IronBeamStream(client)
    messages = []
    
    # Callback to capture messages
    async def on_message(msg):
        messages.append(msg)
        if len(messages) <= 3:  # Show first 3 messages
            print(f"\nMessage {len(messages)}:")
            print(json.dumps(msg, indent=2)[:500] + "..." if len(str(msg)) > 500 else json.dumps(msg, indent=2))
    
    stream.on_message(on_message)
    
    try:
        # Connect
        await stream.connect()
        print(f"✓ Connected (Stream ID: {stream.stream_id})")
        
        # Subscribe based on type
        if sub_type == "quotes":
            stream.subscribe_quotes([symbol])
            print(f"✓ Subscribed to QUOTES")
        elif sub_type == "trades":
            stream.subscribe_trades([symbol])
            print(f"✓ Subscribed to TRADES")
        elif sub_type == "depth":
            stream.subscribe_depths([symbol])
            print(f"✓ Subscribed to DEPTH (Market By Order)")
        
        # Listen for data
        print(f"\nListening for {sub_type} data (15 seconds)...")
        listen_task = asyncio.create_task(stream.listen())
        
        await asyncio.sleep(15)
        
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass
        
        # Analyze results
        print(f"\n{'='*70}")
        print(f"RESULTS FOR {sub_type.upper()}")
        print(f"{'='*70}")
        print(f"Total messages: {len(messages)}")
        
        if messages:
            # Analyze message structure
            msg_types = {}
            for msg in messages:
                if isinstance(msg, dict):
                    # Check for different data types
                    if 'q' in msg:
                        msg_types['quotes'] = msg_types.get('quotes', 0) + 1
                    if 't' in msg:
                        msg_types['trades'] = msg_types.get('trades', 0) + 1
                    if 'd' in msg:
                        msg_types['depth'] = msg_types.get('depth', 0) + 1
                    if 'b' in msg:
                        msg_types['balance'] = msg_types.get('balance', 0) + 1
                    if 'p' in msg:
                        msg_types['ping'] = msg_types.get('ping', 0) + 1
            
            print(f"\nMessage breakdown:")
            for mtype, count in msg_types.items():
                print(f"  {mtype}: {count}")
            
            # Show sample of each message type
            print(f"\nSample data structures:")
            shown_types = set()
            for msg in messages:
                if isinstance(msg, dict):
                    for key in ['q', 't', 'd', 'b', 'p']:
                        if key in msg and key not in shown_types:
                            shown_types.add(key)
                            print(f"\n  Type '{key}':")
                            print(f"  {json.dumps(msg, indent=4)[:300]}...")
            
            # Check for MBO indicators
            print(f"\n{'='*70}")
            print("MBO (Market By Order) ANALYSIS:")
            print(f"{'='*70}")
            
            has_order_book = False
            has_bids_asks = False
            has_order_ids = False
            
            for msg in messages:
                if isinstance(msg, dict):
                    # Check for depth/order book data
                    if 'd' in msg:
                        has_order_book = True
                        depth_data = msg['d']
                        if isinstance(depth_data, list):
                            for item in depth_data:
                                if 'b' in item or 'a' in item:  # bids/asks
                                    has_bids_asks = True
                                if 'oid' in item or 'orderId' in item:  # order IDs
                                    has_order_ids = True
            
            print(f"  Has order book data: {has_order_book}")
            print(f"  Has bids/asks: {has_bids_asks}")
            print(f"  Has order IDs: {has_order_ids}")
            
            if has_order_book and has_bids_asks:
                print(f"\n  ✅ This subscription likely provides MBO data!")
            else:
                print(f"\n  ❌ This subscription may not provide full MBO data")
        else:
            print("  No messages received")
        
        await stream.close()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("\n" + "="*70)
    print("MBO (MARKET BY ORDER) DATA IDENTIFICATION TEST")
    print("="*70)
    
    # Initialize
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    
    client.authenticate()
    print("✓ Authenticated")
    
    # Test symbol
    symbol = "XCME:ES.Z25"
    
    # Test each subscription type
    await test_subscription(client, "quotes", symbol)
    await asyncio.sleep(2)
    
    await test_subscription(client, "trades", symbol)
    await asyncio.sleep(2)
    
    await test_subscription(client, "depth", symbol)
    
    # Final summary
    print(f"\n{'='*70}")
    print("SUMMARY: MBO DATA SOURCES")
    print(f"{'='*70}")
    print("\nTypical MBO characteristics:")
    print("  - Order book with multiple price levels")
    print("  - Individual order IDs")
    print("  - Bid and ask queues")
    print("  - Order size and position in queue")
    print("\nCheck the 'DEPTH' subscription results above for MBO data.")
    print("\n✅ Test complete! Review the output above to identify MBO source.")

if __name__ == "__main__":
    asyncio.run(main())
