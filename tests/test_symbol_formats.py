"""
Test different symbol formats for streaming subscriptions
"""
import asyncio
from ironbeam import IronBeam, IronBeamStream

# Demo credentials
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"

async def test_format(client, stream, symbol_format, description):
    """Test a specific symbol format"""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"Format: {symbol_format}")
    print(f"{'='*70}")
    
    try:
        # Try quote subscription
        print("  Trying quote subscription...")
        stream.subscribe_quotes([symbol_format])
        print(f"  ✓ Quote subscription SUCCESS")
        return True
    except Exception as e:
        print(f"  ✗ Quote subscription failed: {str(e)[:100]}")
        return False

async def main():
    print("\n" + "="*70)
    print("SYMBOL FORMAT TESTING FOR STREAMING")
    print("="*70)
    
    # Initialize client
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    
    client.authenticate()
    print("✓ Authenticated")
    
    # Test different symbol formats
    test_formats = [
        ("XCME:ES.Z25", "Full format with exchange prefix"),
        ("ES.Z25", "Short format without exchange"),
        ("ESZ25", "Compact format (no dots)"),
        ("ES", "Product code only"),
        ("CME:ES.Z25", "CME instead of XCME"),
        ("XCME_ES.Z25", "Underscore separator"),
        ("ES/Z25", "Slash separator"),
    ]
    
    results = {}
    
    for symbol, description in test_formats:
        # Create new stream for each test
        stream = IronBeamStream(client)
        
        try:
            await stream.connect()
            success = await test_format(client, stream, symbol, description)
            results[symbol] = success
            await stream.close()
        except Exception as e:
            print(f"  ✗ Stream error: {e}")
            results[symbol] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    successful = [k for k, v in results.items() if v]
    failed = [k for k, v in results.items() if not v]
    
    if successful:
        print("\n✓ Successful formats:")
        for fmt in successful:
            print(f"  - {fmt}")
    
    if failed:
        print("\n✗ Failed formats:")
        for fmt in failed:
            print(f"  - {fmt}")
    
    if not successful:
        print("\n⚠️  All formats failed - this may be a demo account limitation")
        print("   or the symbols may not be available for streaming.")
    
    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    
    if successful:
        print(f"Use format: {successful[0]}")
    else:
        print("Demo account may have limited streaming access.")
        print("Try with live account or during market hours.")

if __name__ == "__main__":
    asyncio.run(main())
