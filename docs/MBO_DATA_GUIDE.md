# IronBeam API - MBO (Market By Order) Data Guide

## Summary

Based on testing with demo account **51392077**, here's what we found about market data subscriptions:

---

## Available Subscriptions

### 1. **subscribe_quotes()** - Top of Book
```python
stream.subscribe_quotes(["XCME:ES.Z25"])
```
**Provides:**
- Best bid/ask prices
- Last traded price
- Bid/ask sizes
- Daily statistics (open, high, low, volume)

**Data received in previous test:**
```json
{
  "q": [{
    "s": "XCME:ES.Z25",
    "l": 6825.25,      // Last
    "sz": 26,          // Size
    "ch": 50.25,       // Change
    "op": 6778.25,     // Open
    "hi": 6841.25,     // High
    "lo": 6776.5       // Low
  }]
}
```

---

### 2. **subscribe_depths()** - Order Book Depth (MBP)
```python
stream.subscribe_depths(["XCME:ES.Z25"])
```
**Likely provides:**
- Multiple price levels (bid/ask ladder)
- Aggregated volume at each price
- Market By Price (MBP) data
- Depth of market

**Expected structure:**
```json
{
  "d": [{
    "s": "XCME:ES.Z25",
    "bids": [
      {"price": 6825.00, "size": 125},
      {"price": 6824.75, "size": 89},
      {"price": 6824.50, "size": 156}
    ],
    "asks": [
      {"price": 6825.25, "size": 98},
      {"price": 6825.50, "size": 145},
      {"price": 6825.75, "size": 67}
    ]
  }]
}
```

---

### 3. **subscribe_trades()** - Time & Sales
```python
stream.subscribe_trades(["XCME:ES.Z25"])
```
**Provides:**
- Executed trades
- Trade price and size
- Trade timestamp
- Aggressor side (if available)

**Expected structure:**
```json
{
  "t": [{
    "s": "XCME:ES.Z25",
    "p": 6825.25,     // Price
    "sz": 5,          // Size
    "ts": 1729900000, // Timestamp
    "side": "B"       // Buy/Sell
  }]
}
```

---

## MBO vs MBP - Understanding the Difference

### MBP (Market By Price) - Aggregated
- **What:** Total volume at each price level
- **Example:** "150 contracts available at $6825.00"
- **Use case:** General market depth, trading decisions
- **Bandwidth:** Lower
- **Subscription:** `subscribe_depths()` likely provides this

### MBO (Market By Order) - Individual Orders
- **What:** Each individual order in the book
- **Example:** "Order #12345: 5 contracts at $6825.00, Order #12346: 3 contracts at $6825.00"
- **Use case:** Order flow analysis, queue position
- **Bandwidth:** Higher
- **Subscription:** May require special entitlement

---

## Testing Results

### ✅ Working:
- `subscribe_quotes()` - **Confirmed working** (received ES quote data)
- `subscribe_depths()` - **Subscription successful** (no data received yet)
- `subscribe_trades()` - **Subscription successful** (no data received yet)

### ⚠️ Limitations Found:
1. **Demo account** may have limited market data access
2. **Market hours** - Testing outside trading hours may show no data
3. **Data entitlements** - MBO may require premium subscription
4. **REST endpoints** - Some REST calls return 400 errors (may need different format)

---

## How to Identify MBO Data

If `subscribe_depths()` provides MBO data, you'll see:

```json
{
  "d": [{
    "s": "XCME:ES.Z25",
    "bids": [
      {
        "orderId": "ABC123",
        "price": 6825.00,
        "size": 5,
        "position": 1
      },
      {
        "orderId": "DEF456",
        "price": 6825.00,
        "size": 3,
        "position": 2
      }
    ]
  }]
}
```

Key indicators of MBO:
- ✅ Individual `orderId` fields
- ✅ Queue `position` information
- ✅ Multiple orders at same price level
- ✅ Order-level granularity

---

## Recommended Testing Approach

### 1. Test During Market Hours
```python
# E-mini S&P 500 (ES) trading hours (CT):
# Sunday 5:00 PM - Friday 4:00 PM (with daily maintenance 4:00-5:00 PM)

import asyncio
from ironbeam import IronBeam, IronBeamStream

async def test_live_market():
    client = IronBeam(...)
    client.authenticate()
    
    stream = IronBeamStream(client)
    await stream.connect()
    
    # Subscribe to all data types
    stream.subscribe_quotes(["XCME:ES.Z25"])
    stream.subscribe_depths(["XCME:ES.Z25"])
    stream.subscribe_trades(["XCME:ES.Z25"])
    
    # Listen and analyze
    await stream.listen()
```

### 2. Check Data Structure
When you receive depth messages:
```python
async def on_message(msg):
    if 'd' in msg:  # Depth data
        depth = msg['d'][0]
        bids = depth.get('bids', [])
        
        if bids:
            first_bid = bids[0]
            
            # Check for MBO indicators
            if 'orderId' in first_bid:
                print("✅ This is MBO data!")
            else:
                print("ℹ️  This is MBP data (aggregated)")
            
            print(f"Bid structure: {first_bid}")
```

---

## Conclusion & Next Steps

### Most Likely Scenario:
**`subscribe_depths()` provides MBP (Market By Price) data** - aggregated order book.

This is the industry standard for most retail and semi-professional trading APIs. It shows:
- Multiple price levels
- Total volume at each level
- Sufficient for most trading strategies

### To Get True MBO Data:
1. **Check account entitlements**
   - Contact IronBeam support
   - Ask about MBO data access
   - May require premium subscription

2. **Verify during market hours**
   - Test when ES futures are actively trading
   - More data should flow through subscriptions

3. **Use Live Account**
   - Demo accounts may have restricted data
   - Test with live credentials if appropriate

### For Most Trading Use Cases:
**`subscribe_depths()` with MBP data is sufficient** for:
- Analyzing market depth
- Seeing supply/demand
- Making trading decisions
- Order placement strategies
- Most algorithmic trading

---

## Quick Reference

| Subscription | Data Type | Use Case | MBO? |
|--------------|-----------|----------|------|
| `subscribe_quotes()` | Top of book | Quick prices | ❌ |
| `subscribe_depths()` | Order book | Market depth | Maybe (likely MBP) |
| `subscribe_trades()` | Executions | Time & sales | ❌ |

**Best for MBO:** `subscribe_depths()` during market hours with proper entitlements

---

## Example: Monitor Order Book
```python
import asyncio
from ironbeam import IronBeam, IronBeamStream

async def monitor_order_book():
    client = IronBeam(
        api_key="cfcf8651c7914cf988ffc026db9849b1",
        username="51392077",
        password="207341"
    )
    client.authenticate()
    
    stream = IronBeamStream(client)
    
    async def on_message(msg):
        # Check for depth data
        if 'd' in msg:
            for depth in msg['d']:
                symbol = depth.get('s')
                bids = depth.get('bids', [])
                asks = depth.get('asks', [])
                
                print(f"\n{symbol} Order Book:")
                print(f"  Top Bid: {bids[0] if bids else 'N/A'}")
                print(f"  Top Ask: {asks[0] if asks else 'N/A'}")
                print(f"  Depth: {len(bids)} bids, {len(asks)} asks")
    
    stream.on_message(on_message)
    await stream.connect()
    
    # Subscribe to depth
    stream.subscribe_depths(["XCME:ES.Z25"])
    
    # Listen
    await stream.listen()

# Run during market hours
asyncio.run(monitor_order_book())
```

---

**Next Action:** Test during market hours (Sunday 5 PM - Friday 4 PM CT) to see actual depth data flowing through `subscribe_depths()`.
