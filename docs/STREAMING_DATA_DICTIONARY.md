# IronBeam API Streaming Market Data Dictionary

This document provides a comprehensive data dictionary for all streaming market data features available through the IronBeam API. The streaming API provides real-time market data through WebSocket connections across three main data streams: **Quotes**, **Depth**, and **Trades**.

## Overview

The IronBeam streaming API delivers market data through WebSocket connections using a subscription-based model. Clients must:

1. Create a stream ID using `/stream/create`
2. Subscribe to desired data types (quotes, depth, trades)
3. Connect to the WebSocket stream at `/stream/{streamId}`
4. Receive real-time data updates

**Stream Limitations:**
- Maximum 10 instruments per stream
- Property names are abbreviated for stream optimization
- New stream ID required after each WebSocket disconnection
- Streaming models (QuoteFull, TradeOpt, etc.) use abbreviated field names different from REST API models

## Stream Data Structure

The WebSocket stream returns data in the following top-level fields:

| Field | Data Type | Description |
|-------|-----------|-------------|
| `q` | List[QuoteFull] | Quote data updates |
| `d` | List[Depth] | Market depth (order book) updates |
| `tr` | List[TradeOpt] | Trade execution data |
| `p` | PingMessage | Keep-alive ping messages (every 5 seconds) |
| `r` | Response | Reset messages (account/trading day changes) |

---

## 1. QUOTES STREAM (`q` field)

**Description:** Full quote information providing comprehensive market data for subscribed symbols. Includes last trade, bid/ask prices, volumes, and market statistics.

### QuoteFull Properties

| Property | Type | Full Name | Description | Example |
|----------|------|-----------|-------------|---------|
| **s** | string | Symbol | Trading symbol identifier | "XCME:ES.U25" |
| **l** | float | Last Price | Last trade price | 4500.25 |
| **sz** | int | Size | Last trade size (contracts) | 10 |
| **ch** | float | Change | Price change from previous settle | -2.50 |
| **op** | float | Open Price | Opening price for the session | 4502.75 |
| **hi** | float | High Price | Session high price | 4510.00 |
| **lo** | float | Low Price | Session low price | 4495.00 |
| **ags** | AggressorSideType | Aggressor Side | Side that initiated the last trade | 1 (BUY) |
| **td** | TickDirectionType | Tick Direction | Price movement direction | 2 |
| **stt** | float | Settle Price | Settlement price | 4502.75 |
| **stts** | string | Settle Date String | Settlement date | "2025-10-29" |
| **sttst** | int | Settle Timestamp | Settlement timestamp (milliseconds) | 1761350400000 |
| **pstt** | float | Previous Settle | Previous settlement price | 4505.25 |
| **pstts** | string | Previous Settle Date | Previous settlement date string | "2025-10-28" |
| **sttch** | float | Settle Change | Settlement price change | -2.50 |
| **hb** | float | High Bid | Highest bid price | 4500.00 |
| **la** | float | Low Ask | Lowest ask price | 4500.50 |
| **b** | float | Bid Price | Current best bid price | 4500.00 |
| **bt** | int | Bid Timestamp | Bid timestamp (milliseconds) | 1761350400000 |
| **bs** | int | Bid Size | Number of contracts at bid | 25 |
| **ibc** | int | Implied Bid Count | Number of implied orders at bid | 5 |
| **ibs** | int | Implied Bid Size | Total implied bid size | 15 |
| **a** | float | Ask Price | Current best ask price | 4500.50 |
| **at** | int | Ask Timestamp | Ask timestamp (milliseconds) | 1761350400000 |
| **var_as** | int | Ask Size | Number of contracts at ask | 30 |
| **ias** | int | Implied Ask Size | Total implied ask size | 20 |
| **iac** | int | Implied Ask Count | Number of implied orders at ask | 8 |
| **tt** | int | Trade Timestamp | Last trade timestamp (milliseconds) | 1761350400000 |
| **tdt** | string | Trade Date | Trade date string | "2025-10-29" |
| **secs** | SecurityStatusType | Security Status | Current security trading status | 2 |
| **sdt** | string | Status Date | Security status date | "2025-10-29" |
| **oi** | int | Open Interest | Total open interest | 150000 |
| **tv** | int | Total Volume | Total session volume | 50000 |
| **bv** | int | Block Volume | Block trade volume | 5000 |
| **swv** | int | Swaps Volume | Swaps trading volume | 2000 |
| **pv** | int | Physical Volume | Physical delivery volume | 1000 |

### Related Enumerations

#### AggressorSideType
| Value | Description |
|-------|-------------|
| 0 | INVALID |
| 1 | BUY |
| 2 | SELL |

#### TickDirectionType
| Value | Description |
|-------|-------------|
| 255 | INVALID |
| 0 | SAME |
| 1 | PLUS (price up) |
| 2 | MINUS (price down) |

#### SecurityStatusType
| Value | Typical Meaning |
|-------|----------------|
| 2 | Trading |
| 4 | Trading Halt |
| 15 | Fast Market |
| 17 | No Open/No Resume |
| 18 | Price Indication |
| 20 | Additional Info Required |
| 21 | Regulatory Halt |
| 22 | Volatility Trading Pause |
| 24 | Volatility Trading Pause - Straddle Condition |
| 25 | Volatility Guard |
| 26 | Volatility Guard - Settlement Price in Effect |
| 30 | Ready to Trade (start of session) |
| 31 | Not Available for Trading (end of session) |
| 103 | Cancel Only |
| 126 | Unknown or Invalid |

---

## 2. DEPTH STREAM (`d` field)

**Description:** Market depth data showing bid and ask levels with order book information for subscribed symbols.

### Depth Properties

| Property | Type | Full Name | Description | Example |
|----------|------|-----------|-------------|---------|
| **s** | string | Symbol | Trading symbol identifier | "XCME:ES.U25" |
| **b** | List[DepthLevel] | Bid Levels | Array of bid depth levels | See DepthLevel below |
| **a** | List[DepthLevel] | Ask Levels | Array of ask depth levels | See DepthLevel below |

### DepthLevel Properties

| Property | Type | Full Name | Description | Example |
|----------|------|-----------|-------------|---------|
| **l** | int | Level | 0-based level number (0=best price) | 0 |
| **t** | int | Timestamp | Time in milliseconds | 1761350400000 |
| **s** | SideShort | Side | Bid or Ask side indicator | "B" |
| **p** | float | Price | Price at this level | 4500.00 |
| **o** | int | Orders | Number of orders at this level | 5 |
| **sz** | float | Size | Total size of all orders at level | 25 |
| **ioc** | int | Implied Order Count | Number of implied orders at level | 2 |
| **var_is** | float | Implied Size | Total implied size at level | 10 |

### Related Enumerations

#### SideShort
| Value | Description |
|-------|-------------|
| B | Bid (Buy side) |
| A | Ask (Sell side) |

---

## 3. TRADES STREAM (`tr` field)

**Description:** Real-time trade execution data with comprehensive trade details and market impact information.

**Note:** The streaming API uses `TradeOpt` model with abbreviated field names, which differs from the `Trade` model used in REST API responses.

### TradeOpt Properties

| Property | Type | Full Name | Description | Example |
|----------|------|-----------|-------------|---------|
| **s** | string | Symbol | Trading symbol identifier | "XCME:ES.U25" |
| **p** | float | Price | Trade execution price | 4500.25 |
| **ch** | float | Change | Price change from previous trade | 0.25 |
| **sz** | float | Size | Trade size (contracts) | 10 |
| **sq** | float | Sequence Number | Trade sequence number | 12345678.0 |
| **st** | int | Send Time | Trade timestamp (milliseconds) | 1761350400000 |
| **td** | TickDirection | Tick Direction | Price movement direction | "PLUS" |
| **var_as** | AggressorSideType | Aggressor Side | Initiating side of trade | 1 |
| **tdt** | string | Trade Date | Trade date string | "2025-10-29" |
| **tid** | float | Trade ID | Unique trade identifier | 987654321.0 |
| **var_is** | bool | Is Settlement | Whether this is a settlement trade | false |
| **clx** | bool | Is Cancelled | Whether this trade was cancelled | false |
| **spt** | SystemPricedTrade | System Priced | System pricing classification | "SYSTEM" |
| **ist** | InvestigationStatus | Investigation Status | Trade investigation status | "COMPLETED" |
| **bt** | BlockTrade | Block Trade | Block trade classification | "NORMAL" |

### Related Enumerations

#### TickDirection
| Value | Description |
|-------|-------------|
| INVALID | Invalid direction |
| PLUS | Price increased |
| MINUS | Price decreased |
| SAME | Price unchanged |

#### SystemPricedTrade
| Value | Description |
|-------|-------------|
| INVALID | Invalid classification |
| SYSTEM | System-priced trade |
| CRACK | Crack spread trade |

#### InvestigationStatus
| Value | Description |
|-------|-------------|
| INVALID | Invalid status |
| INVESTIGATING | Under investigation |
| COMPLETED | Investigation completed |

#### BlockTrade
| Value | Description |
|-------|-------------|
| INVALID | Invalid block trade |
| NORMAL | Normal block trade |
| EFP | Exchange for Physical |
| EFS | Exchange for Swap |
| OFF_EXCHANGE | Off-exchange trade |
| NG | Natural Gas block trade |
| CCX | CCX block trade |
| EFR | Exchange for Risk |

---

## Subscription Management

### Creating Stream
```http
GET /stream/create
```
Returns a unique `streamId` for the WebSocket connection.

### Subscribing to Data

#### Quotes Subscription
```http
GET /market/quotes/subscribe/{streamId}?symbols=XCME:ES.U25,XCME:NQ.U25
```

#### Depth Subscription  
```http
GET /market/depths/subscribe/{streamId}?symbols=XCME:ES.U25,XCME:NQ.U25
```

#### Trades Subscription
```http
GET /market/trades/subscribe/{streamId}?symbols=XCME:ES.U25,XCME:NQ.U25
```

### WebSocket Connection
```
wss://live.ironbeamapi.com/v2/stream/{streamId}?token={authToken}
```

---

## Data Usage Examples

### Processing Quote Updates
```python
if 'q' in stream_data:
    for quote in stream_data['q']:
        symbol = quote['s']
        last_price = quote['l']
        bid_price = quote['b']
        ask_price = quote['a']
        volume = quote['tv']
        # Process quote data...
```

### Processing Depth Updates
```python
if 'd' in stream_data:
    for depth in stream_data['d']:
        symbol = depth['s']
        bid_levels = depth['b']  # List of bid levels
        ask_levels = depth['a']  # List of ask levels
        
        for level in bid_levels:
            price = level['p']
            size = level['sz']
            orders = level['o']
            # Process bid level...
```

### Processing Trade Updates
```python
if 'tr' in stream_data:
    for trade in stream_data['tr']:
        symbol = trade['s']
        price = trade['p']
        size = trade['sz']
        side = trade['var_as']  # 1=BUY, 2=SELL
        timestamp = trade['st']
        # Process trade data...
```

---

## Notes

- **Property Naming:** Field names are abbreviated to optimize streaming performance
- **Timestamps:** All timestamps are in milliseconds since Unix epoch
- **Optional Fields:** All properties are optional and may not be present in every message
- **Exchange Symbols:** Symbol format follows exchange:contract notation (e.g., "XCME:ES.U25")
- **Float Precision:** Prices and sizes maintain exchange-appropriate decimal precision
- **Stream Reliability:** Implement reconnection logic as WebSocket connections may drop

This data dictionary serves as the definitive reference for interpreting IronBeam streaming market data across all supported data types.