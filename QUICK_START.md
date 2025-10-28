# Quick Start Guide - IronBeam Demo Account

## 🚀 Quick Test Command

```bash
..\fin_venv\Scripts\python.exe demo_test_simple.py
```

---

## 📋 Demo Credentials

```python
DEMO_USERNAME = "51392077"
DEMO_PASSWORD = "207341"
DEMO_KEY = "cfcf8651c7914cf988ffc026db9849b1"
```

---

## 💻 Basic Usage

### 1. Initialize Client
```python
from ironbeam import IronBeam

client = IronBeam(
    api_key="cfcf8651c7914cf988ffc026db9849b1",
    username="51392077",
    password="207341"
)

# Authenticate
token = client.authenticate()
```

### 2. Get Account Info
```python
# Trader information
trader_info = client.get_trader_info()
print(f"Trader ID: {trader_info['traderId']}")
print(f"Accounts: {trader_info['accounts']}")

# Account balance
account_id = trader_info['accounts'][0]
balance = client.get_account_balance(account_id)
print(f"Balance: ${balance['balances'][0]['cashBalance']:,.2f}")
```

### 3. Search for Symbols
```python
# Search for futures contracts
futures = client.search_futures("CME", "ES")
symbols = futures.get('symbols', [])

print(f"Found {len(symbols)} contracts:")
for symbol in symbols[:5]:
    print(f"  - {symbol}")
```

### 4. Streaming (Async)
```python
import asyncio
from ironbeam import IronBeamStream

async def stream_data():
    stream = IronBeamStream(client)
    
    # Connect
    await stream.connect()
    
    # Subscribe
    stream.subscribe_quotes(["XCME:ES.Z25"])
    
    # Listen
    await stream.listen()

# Run
asyncio.run(stream_data())
```

---

## 📊 Account Status

✅ **Current Demo Account:**
- Balance: $50,000.00 USD
- Positions: None (0)
- Status: Active
- Type: Demo/Simulated

---

## 🎯 Available Test Scripts

| Script | Purpose | Complexity |
|--------|---------|------------|
| `demo_test_simple.py` | Basic functionality test | ⭐ Easy |
| `demo_streaming_test.py` | WebSocket streaming demo | ⭐⭐ Medium |
| `demo_market_data_test.py` | Market data exploration | ⭐⭐ Medium |
| `demo_test.py` | Full async test suite | ⭐⭐⭐ Advanced |

---

## ✅ Verified Features

- [x] Authentication
- [x] Account balance query
- [x] Position tracking  
- [x] Risk management
- [x] Symbol search (21 ES contracts found)
- [x] WebSocket streaming (3 messages received)
- [x] Stream connection/disconnection

---

## 📝 Symbol Format Examples

| Format | Example | Usage |
|--------|---------|-------|
| Full | `XCME:ES.Z25` | REST API quotes |
| Short | `ES.Z25` | Symbol search |
| Exchange | `CME` | Exchange queries |
| Product | `ES` | Product search |

**Contract Months:**
- H = March
- M = June
- U = September
- Z = December

**Active Contracts Found:**
- ES.Z25, ES.H26, ES.M26, ES.U26, ES.Z26...

---

## 🔧 Troubleshooting

### Empty Quote Data?
✓ **Normal** - Demo accounts may not have real-time data

### Subscription Errors?
✓ **Expected** - Some features require live accounts

### Connection Issues?
✓ Check token is valid and not expired

---

## 📚 Documentation

- Examples: `examples/` directory
- Quick Reference: `examples/09_quick_reference.py`
- Test Results: `TEST_SUMMARY.md`
- Detailed Results: `DEMO_TEST_RESULTS.md`

---

## 🎉 Success!

Your IronBeam demo account is ready to use!

**Next:** Run `demo_test_simple.py` to verify everything works.
