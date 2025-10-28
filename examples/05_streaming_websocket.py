"""
Example 5: WebSocket Streaming
Demonstrates real-time market data streaming via WebSockets
"""
import asyncio
from ironbeam import IronBeam, IronBeamStream

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

# Test symbols
SYMBOLS = ["XCEC:MGC.Z25", "XCME:ES.Z25"]


def setup_client():
    """Initialize and authenticate client."""
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    client.authenticate()
    return client


async def example_basic_streaming(client):
    """Basic streaming with quotes, depth, and trades."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Streaming")
    print("="*70)

    # Create stream
    stream = IronBeamStream(client)

    # Message counter
    message_count = {'total': 0, 'quotes': 0, 'depths': 0, 'trades': 0}

    # Define message handler
    async def on_message(msg):
        message_count['total'] += 1

        # Identify message type
        if 'q' in msg or 'quotes' in str(msg).lower():
            message_count['quotes'] += 1
        elif 'd' in msg or 'depth' in str(msg).lower():
            message_count['depths'] += 1
        elif 't' in msg or 'trade' in str(msg).lower():
            message_count['trades'] += 1

        # Print first few messages
        if message_count['total'] <= 3:
            print(f"\n  Message {message_count['total']}:")
            print(f"    {str(msg)[:150]}...")

    # Define connection handler
    async def on_connect(stream_id):
        print(f"\n  ✓ Connected to stream: {stream_id}")

    # Define error handler
    async def on_error(error):
        print(f"\n  ✗ Stream error: {error}")

    # Register handlers
    stream.on_message(on_message)
    stream.on_connect(on_connect)
    stream.on_error(on_error)

    print(f"\n  Connecting to WebSocket...")

    try:
        # Connect
        await stream.connect()

        # Subscribe to data
        print(f"\n  Subscribing to quotes for {SYMBOLS}...")
        stream.subscribe_quotes(SYMBOLS)

        print(f"  Subscribing to depth for {SYMBOLS}...")
        stream.subscribe_depths(SYMBOLS)

        print(f"  Subscribing to trades for {SYMBOLS}...")
        stream.subscribe_trades(SYMBOLS)

        # Start listening
        print(f"\n  Listening for 15 seconds...")
        listen_task = asyncio.create_task(stream.listen())

        # Wait with progress
        for i in range(15):
            await asyncio.sleep(1)
            if i % 5 == 4:
                print(f"    {i+1}s - Messages: {message_count['total']}")

        # Stop and close
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass

        await stream.close()

        # Print summary
        print(f"\n  Streaming Summary:")
        print(f"    Total Messages: {message_count['total']}")
        print(f"    Quote Messages: {message_count['quotes']}")
        print(f"    Depth Messages: {message_count['depths']}")
        print(f"    Trade Messages: {message_count['trades']}")

    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def example_quote_processing(client):
    """Stream and process quote data."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Processing Quote Data")
    print("="*70)

    stream = IronBeamStream(client)

    # Store latest quotes
    latest_quotes = {}

    async def on_message(msg):
        # Try to extract quote data
        if isinstance(msg, dict):
            # Check for quote message structure
            if 'q' in msg and isinstance(msg['q'], list):
                for quote in msg['q']:
                    symbol = quote.get('s', 'unknown')
                    last = quote.get('l')
                    bid = quote.get('b')
                    ask = quote.get('a')

                    if last:
                        latest_quotes[symbol] = {
                            'last': last,
                            'bid': bid,
                            'ask': ask
                        }

    async def on_connect(stream_id):
        print(f"  ✓ Connected: {stream_id}")

    stream.on_message(on_message)
    stream.on_connect(on_connect)

    try:
        await stream.connect()
        stream.subscribe_quotes(SYMBOLS)

        print(f"\n  Collecting quotes for 10 seconds...")

        listen_task = asyncio.create_task(stream.listen())
        await asyncio.sleep(10)

        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass

        await stream.close()

        # Display collected quotes
        print(f"\n  Latest Quotes Collected:")
        for symbol, quote in latest_quotes.items():
            print(f"\n    {symbol}:")
            print(f"      Last: ${quote['last']:,.2f}" if quote['last'] else "      Last: N/A")
            if quote['bid'] and quote['ask']:
                spread = quote['ask'] - quote['bid']
                print(f"      Bid: ${quote['bid']:,.2f}")
                print(f"      Ask: ${quote['ask']:,.2f}")
                print(f"      Spread: ${spread:.2f}")

    except Exception as e:
        print(f"\n  ✗ Error: {e}")


async def example_depth_analysis(client):
    """Stream and analyze order book depth."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Order Book Depth Analysis")
    print("="*70)

    stream = IronBeamStream(client)

    # Track depth updates
    depth_updates = {'count': 0}
    latest_depth = {}

    async def on_message(msg):
        if isinstance(msg, dict) and 'd' in msg:
            depth_updates['count'] += 1

            # Parse depth data
            depths = msg.get('d', [])
            for depth in depths:
                if isinstance(depth, dict):
                    symbol = depth.get('s')
                    bids = depth.get('b', [])
                    asks = depth.get('a', [])

                    if symbol and (bids or asks):
                        latest_depth[symbol] = {
                            'bids': bids[:5],  # Top 5 levels
                            'asks': asks[:5]
                        }

    async def on_connect(stream_id):
        print(f"  ✓ Connected: {stream_id}")

    stream.on_message(on_message)
    stream.on_connect(on_connect)

    try:
        await stream.connect()

        # Subscribe to depth only
        stream.subscribe_depths([SYMBOLS[0]])  # Just one symbol

        print(f"\n  Collecting depth data for 10 seconds...")

        listen_task = asyncio.create_task(stream.listen())
        await asyncio.sleep(10)

        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass

        await stream.close()

        # Display results
        print(f"\n  Depth Updates Received: {depth_updates['count']}")

        if latest_depth:
            for symbol, depth in latest_depth.items():
                print(f"\n  Latest Order Book for {symbol}:")

                if depth['bids']:
                    print(f"\n    Top 5 Bids:")
                    for i, bid in enumerate(depth['bids'][:5], 1):
                        if isinstance(bid, dict):
                            price = bid.get('p', 0)
                            size = bid.get('s', 0)
                            print(f"      {i}. ${price:,.2f} x {size}")

                if depth['asks']:
                    print(f"\n    Top 5 Asks:")
                    for i, ask in enumerate(depth['asks'][:5], 1):
                        if isinstance(ask, dict):
                            price = ask.get('p', 0)
                            size = ask.get('s', 0)
                            print(f"      {i}. ${price:,.2f} x {size}")
        else:
            print("\n  No depth data received (may be outside market hours)")

    except Exception as e:
        print(f"\n  ✗ Error: {e}")


async def example_connection_lifecycle(client):
    """Demonstrate connection lifecycle management."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Connection Lifecycle")
    print("="*70)

    stream = IronBeamStream(client)

    connection_events = []

    async def on_connect(stream_id):
        event = f"Connected: {stream_id}"
        connection_events.append(event)
        print(f"  ✓ {event}")

    async def on_disconnect():
        event = "Disconnected"
        connection_events.append(event)
        print(f"  ✓ {event}")

    async def on_error(error):
        event = f"Error: {error}"
        connection_events.append(event)
        print(f"  ✗ {event}")

    stream.on_connect(on_connect)
    stream.on_error(on_error)

    print("\n  1. Connecting...")
    await stream.connect()
    await asyncio.sleep(1)

    print("\n  2. Subscribing to quotes...")
    stream.subscribe_quotes([SYMBOLS[0]])
    await asyncio.sleep(1)

    print("\n  3. Unsubscribing from quotes...")
    stream.unsubscribe_quotes([SYMBOLS[0]])
    await asyncio.sleep(1)

    print("\n  4. Closing connection...")
    await stream.close()

    print(f"\n  Lifecycle Events: {len(connection_events)}")
    for event in connection_events:
        print(f"    - {event}")


async def main():
    """Run all streaming examples."""
    print("\n" + "="*70)
    print("IRONBEAM SDK - WEBSOCKET STREAMING EXAMPLES")
    print("="*70)

    # Setup
    client = setup_client()
    print("\n✓ Authenticated")

    # Run examples
    await example_basic_streaming(client)
    await example_quote_processing(client)
    await example_depth_analysis(client)
    await example_connection_lifecycle(client)

    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Use IronBeamStream for WebSocket connections")
    print("  2. Register handlers for messages, connections, and errors")
    print("  3. Subscribe to quotes, depths, and trades separately")
    print("  4. Process messages in async handlers")
    print("  5. Always close stream when done")
    print("  6. Market data availability depends on market hours")


if __name__ == "__main__":
    asyncio.run(main())
