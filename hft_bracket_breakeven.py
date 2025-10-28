"""
HIGH-FREQUENCY BRACKET ORDER WITH AUTO BREAKEVEN
Optimized for low-latency trading

Features:
- Direct WebSocket connection (no threading overhead)
- Fast price updates via streaming
- Immediate order execution
- Efficient auto breakeven logic
- Minimal memory allocations
- Real-time P&L tracking
- Notifications on breakeven triggers
- Trailing stop functionality
"""

import os
import time
import asyncio
import logging
from collections import deque
from datetime import datetime
from dotenv import load_dotenv
from ironbeam import IronBeam
from ironbeam.streaming import IronBeamStream
from ironbeam.models import (
    OrderSide, OrderRequest, OrderUpdateRequest,
    OrderType, DurationType
)

# Fast logging for HFT (setup BEFORE winsound import)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Try to import winsound for audio notifications (Windows)
try:
    import winsound
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False
    logger.warning("⚠️  winsound not available - notifications will be visual only")

# Load environment
load_dotenv()


def play_notification(sound_type: str = "success"):
    """Play audio notification (Windows only)."""
    if not SOUND_ENABLED:
        return
    
    try:
        if sound_type == "success":
            winsound.Beep(1000, 200)  # 1000 Hz for 200ms
        elif sound_type == "warning":
            winsound.Beep(800, 150)
        elif sound_type == "breakeven":
            winsound.Beep(1500, 100)
            time.sleep(0.05)
            winsound.Beep(1500, 100)
        elif sound_type == "fill":
            winsound.Beep(2000, 300)
    except:
        pass


class PLTracker:
    """Real-time P&L tracking."""
    
    def __init__(self, entry_price: float, quantity: int, side: str):
        self.entry_price = entry_price
        self.quantity = quantity
        self.side = side.upper()
        self.peak_profit = 0
        self.peak_price = entry_price
        self.start_time = time.time()
        
    def calculate_pnl(self, current_price: float) -> dict:
        """Calculate real-time P&L."""
        if self.side == "BUY":
            price_diff = current_price - self.entry_price
        else:
            price_diff = self.entry_price - current_price
        
        pnl = price_diff * self.quantity
        pnl_percent = (price_diff / self.entry_price) * 100
        
        # Track peak profit
        if pnl > self.peak_profit:
            self.peak_profit = pnl
            self.peak_price = current_price
        
        # Calculate drawdown from peak
        if self.peak_profit > 0:
            drawdown = self.peak_profit - pnl
            drawdown_percent = (drawdown / self.peak_profit) * 100 if self.peak_profit > 0 else 0
        else:
            drawdown = 0
            drawdown_percent = 0
        
        elapsed = time.time() - self.start_time
        
        return {
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'peak_profit': self.peak_profit,
            'peak_price': self.peak_price,
            'drawdown': drawdown,
            'drawdown_percent': drawdown_percent,
            'elapsed_time': elapsed
        }
    
    def format_pnl(self, current_price: float) -> str:
        """Format P&L for display."""
        stats = self.calculate_pnl(current_price)
        
        pnl_symbol = "+" if stats['pnl'] >= 0 else ""
        color = "🟢" if stats['pnl'] >= 0 else "🔴"
        
        return (f"{color} P&L: {pnl_symbol}${stats['pnl']:.2f} ({pnl_symbol}{stats['pnl_percent']:.2f}%) | "
                f"Peak: ${stats['peak_profit']:.2f} @ ${stats['peak_price']:.2f} | "
                f"DD: ${stats['drawdown']:.2f} ({stats['drawdown_percent']:.1f}%)")


class FastPriceCache:
    """Lock-free price cache optimized for low latency."""
    
    def __init__(self):
        self.prices = {}  # symbol -> {'bid': float, 'ask': float, 'mid': float, 'ts': int}
        self.price_history = {}  # symbol -> deque of recent prices (for algo)
        
    def update(self, symbol: str, bid: float, ask: float):
        """Update price - called from async context."""
        mid = (bid + ask) / 2
        ts = time.time_ns()  # Nanosecond precision
        
        self.prices[symbol] = {
            'bid': bid,
            'ask': ask,
            'mid': mid,
            'ts': ts
        }
        
        # Keep recent price history (for trend analysis)
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=100)
        self.price_history[symbol].append(mid)
    
    def get(self, symbol: str):
        """Get latest price."""
        return self.prices.get(symbol)
    
    def get_spread(self, symbol: str):
        """Get bid-ask spread in ticks."""
        price = self.prices.get(symbol)
        if price:
            return price['ask'] - price['bid']
        return None


class AutoBreakevenHFT:
    """High-frequency auto breakeven manager with trailing stop.
    
    Optimized for speed:
    - Pre-calculated trigger levels
    - Minimal conditionals
    - Direct API calls
    - Optional trailing stop after breakeven
    """
    
    def __init__(self, client, account_id: str, order_id: str,
                 entry_price: float, side: str, symbol: str,
                 trigger_ticks: list = [20, 40, 60],
                 sl_offset_ticks: list = [10, 30, 50],
                 trailing_stop: bool = True,
                 trailing_distance: float = 15):
        
        self.client = client
        self.account_id = account_id
        self.order_id = order_id
        self.entry_price = entry_price
        self.side = side.upper()
        self.symbol = symbol
        self.quantity = 1
        
        # Trailing stop settings
        self.trailing_stop = trailing_stop
        self.trailing_distance = trailing_distance
        self.trailing_active = False
        self.highest_price = entry_price if side == "BUY" else entry_price
        
        # Pre-calculate all trigger levels (avoid runtime calculations)
        if self.side == "BUY":
            self.trigger_prices = [entry_price + t for t in trigger_ticks]
            self.sl_prices = [entry_price + s for s in sl_offset_ticks]
        else:  # SELL
            self.trigger_prices = [entry_price - t for t in trigger_ticks]
            self.sl_prices = [entry_price - s for s in sl_offset_ticks]
        
        self.current_level = 0  # Which breakeven level we're at (0-2)
        self.max_levels = len(trigger_ticks)
        self.current_sl = None
        self.last_update_time = 0  # Rate limiting
        
        logger.info(f"AutoBreakeven initialized: Entry=${entry_price:.2f}")
        for i, (trigger, sl) in enumerate(zip(self.trigger_prices, self.sl_prices)):
            logger.info(f"  Level {i+1}: Trigger=${trigger:.2f} → SL=${sl:.2f}")
        if trailing_stop:
            logger.info(f"  Trailing Stop: ${trailing_distance:.2f} distance (activates after all levels)")
    
    def check_and_update(self, current_price: float) -> bool:
        """Check if we should move stop loss. Returns True if updated.
        
        Optimized:
        - Single comparison per level
        - Early exit when no action needed
        - Direct API call (no validation overhead)
        - Optional trailing stop after breakeven levels
        """
        # Rate limit updates (max once per second)
        now = time.time()
        if now - self.last_update_time < 1.0:
            return False
        
        # Update peak price for trailing
        if self.side == "BUY":
            if current_price > self.highest_price:
                self.highest_price = current_price
        else:
            if current_price < self.highest_price:
                self.highest_price = current_price
        
        # Check breakeven levels first
        if self.current_level < self.max_levels:
            trigger = self.trigger_prices[self.current_level]
            triggered = (current_price >= trigger) if self.side == "BUY" else (current_price <= trigger)
            
            if triggered:
                new_sl = self.sl_prices[self.current_level]
                if self._update_stop_loss(new_sl, f"BREAKEVEN LEVEL {self.current_level + 1}"):
                    self.current_level += 1
                    self.last_update_time = now
                    play_notification("breakeven")
                    return True
        
        # Trailing stop (only after all breakeven levels complete)
        elif self.trailing_stop and self.current_level >= self.max_levels:
            if not self.trailing_active:
                self.trailing_active = True
                logger.info("🔄 TRAILING STOP ACTIVATED")
            
            # Calculate new trailing stop
            if self.side == "BUY":
                new_sl = self.highest_price - self.trailing_distance
                # Only move SL up (never down)
                if self.current_sl is None or new_sl > self.current_sl:
                    if self._update_stop_loss(new_sl, "TRAILING STOP"):
                        self.last_update_time = now
                        return True
            else:  # SELL
                new_sl = self.highest_price + self.trailing_distance
                # Only move SL down (never up)
                if self.current_sl is None or new_sl < self.current_sl:
                    if self._update_stop_loss(new_sl, "TRAILING STOP"):
                        self.last_update_time = now
                        return True
        
        return False
    
    def _update_stop_loss(self, new_sl: float, reason: str) -> bool:
        """Internal method to update stop loss."""
        try:
            # FAST: Direct order update using SDK model
            update = OrderUpdateRequest(
                order_id=self.order_id,
                stop_price=new_sl  # Correct field name per SDK
            )

            # Time the API call
            t0 = time.perf_counter()
            self.client.update_order(self.account_id, self.order_id, update)
            latency_ms = (time.perf_counter() - t0) * 1000

            self.current_sl = new_sl

            logger.info(f"✅ {reason}: SL→${new_sl:.2f} ({latency_ms:.2f}ms)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update SL: {e}")
            return False


class HFTBracketTrader:
    """High-frequency bracket order trader with auto breakeven."""
    
    def __init__(self, api_key: str, username: str, password: str):
        self.client = IronBeam(api_key, username, password)
        self.client.authenticate()
        
        # Get account
        trader_info = self.client.get_trader_info()
        self.account_id = trader_info.accounts[0] if hasattr(trader_info, 'accounts') else trader_info['accounts'][0]
        
        # Fast price cache
        self.price_cache = FastPriceCache()
        
        # Streaming
        self.stream = None
        self.order_id = None
        self.sl_order_id = None
        self.tp_order_id = None
        self.breakeven_manager = None
        self.pnl_tracker = None
        
        # Position tracking
        self.position_filled = False
        self.entry_symbol = None
        self.entry_price = None
        self.entry_side = None
        self.entry_quantity = None
        self.planned_sl = None
        self.planned_tp = None
        
        # Performance metrics
        self.msg_count = 0
        self.start_time = None
        self.last_pnl_display = 0  # Rate limit P&L display
        
    async def on_market_data(self, msg):
        """Handle market data - OPTIMIZED FOR SPEED."""
        try:
            self.msg_count += 1
            
            # DEBUG: Log first few callbacks to understand message types
            if self.msg_count <= 10:
                logger.info(f"📨 Message {self.msg_count}: keys={list(msg.keys())[:5]}")
            
            # Handle position updates (key: 'ps' = positions)
            if 'ps' in msg and msg['ps'] and not self.position_filled:
                positions = msg['ps']
                for pos in positions:
                    symbol = pos.get('s')
                    qty = pos.get('q', 0)
                    
                    # Check if our order filled
                    if symbol == self.entry_symbol and qty != 0:
                        self.position_filled = True
                        
                        # Try multiple field names for fill price
                        fill_price = (pos.get('p') or pos.get('ap') or pos.get('avgPrice') or 
                                    pos.get('price') or pos.get('entryPrice') or self.entry_price)
                        
                        logger.info(f"\n🎉 ORDER FILLED!")
                        logger.info(f"Symbol: {symbol}")
                        logger.info(f"Quantity: {qty}")
                        if fill_price:
                            logger.info(f"Fill Price: ${fill_price:.2f}")
                        else:
                            logger.warning("⚠️  Fill price not found in position data")
                            fill_price = self.entry_price
                            logger.info(f"Using entry price: ${fill_price:.2f}")
                        
                        play_notification("fill")
                        
                        # Find the SL order ID from the bracket strategy
                        await self.find_sl_order_id()
                        
                        # Activate auto-breakeven (will modify the SL order)
                        self.activate_auto_breakeven_after_fill(symbol, fill_price, self.entry_side, abs(qty))
                        
                        break
            
            # Messages use abbreviated keys: 'q' = quotes, 'd' = depth, 'b' = balance
            
            # Handle quote messages (key: 'q')
            if 'q' in msg and msg['q']:
                for quote in msg['q']:
                    symbol = quote.get('s')  # symbol
                    bid = quote.get('b')     # bid
                    ask = quote.get('a')     # ask
                    last = quote.get('l')    # last price
                    
                    if symbol and bid and ask:
                        # Update cache (fast)
                        self.price_cache.update(symbol, bid, ask)
                        
                        # Log first price update
                        if self.msg_count <= 5:
                            logger.info(f"📊 {symbol}: Bid=${bid:.2f} Ask=${ask:.2f}")
                        
                        # Check breakeven and display P&L (if position exists)
                        if self.breakeven_manager and symbol == self.breakeven_manager.symbol:
                            mid = (bid + ask) / 2
                            
                            # Update breakeven
                            updated = self.breakeven_manager.check_and_update(mid)
                            
                            # Display P&L (rate limited to every 5 seconds or on breakeven update)
                            now = time.time()
                            if updated or (now - self.last_pnl_display >= 5.0):
                                if self.pnl_tracker:
                                    pnl_display = self.pnl_tracker.format_pnl(mid)
                                    logger.info(f"💰 {pnl_display}")
                                    self.last_pnl_display = now
            
            # Handle depth messages (key: 'd')
            elif 'd' in msg and msg['d']:
                for depth in msg['d']:
                    symbol = depth.get('s')  # symbol
                    bids = depth.get('b', [])  # bid levels
                    asks = depth.get('a', [])  # ask levels
                    
                    if symbol and bids and asks:
                        # Get best bid/ask from depth
                        best_bid = bids[0]['p'] if bids else None  # 'p' = price
                        best_ask = asks[0]['p'] if asks else None
                        
                        if best_bid and best_ask:
                            self.price_cache.update(symbol, best_bid, best_ask)
                            
                            # Check breakeven and P&L from depth too
                            if self.breakeven_manager and symbol == self.breakeven_manager.symbol:
                                mid = (best_bid + best_ask) / 2
                                updated = self.breakeven_manager.check_and_update(mid)
                                
                                # Display P&L on update
                                if updated and self.pnl_tracker:
                                    pnl_display = self.pnl_tracker.format_pnl(mid)
                                    logger.info(f"💰 {pnl_display}")
        
        except Exception as e:
            logger.error(f"Error in on_market_data: {e}")
            import traceback
            traceback.print_exc()
    
    async def subscribe_symbols(self, symbols: list):
        """Subscribe to market data for symbols."""
        logger.info(f"📊 Subscribing to {len(symbols)} symbols...")
        
        for symbol in symbols:
            # Subscribe one at a time (avoid 400 errors)
            self.stream.subscribe_quotes([symbol])
            await asyncio.sleep(0.3)
            self.stream.subscribe_depths([symbol])
            await asyncio.sleep(0.3)
            logger.info(f"  ✓ {symbol}")
        
        # Wait for initial data
        logger.info("⏳ Waiting for market data...")
        await asyncio.sleep(3)
        
        # Show prices
        logger.info(f"\n💹 Current Prices:")
        for symbol in symbols:
            price = self.price_cache.get(symbol)
            if price:
                logger.info(f"  {symbol}: ${price['mid']:.2f} (spread: ${price['ask']-price['bid']:.2f})")
            else:
                logger.info(f"  {symbol}: Waiting for data...")
    
    def place_bracket_order(self, symbol: str, side: str, quantity: int,
                           entry_price: float, stop_loss: float, take_profit: float):
        """Place TRUE bracket order with SL/TP attached."""
        
        logger.info(f"\n🎯 PLACING BRACKET ORDER (Entry + SL + TP)")
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Side: {side}")
        logger.info(f"Entry: ${entry_price:.2f}")
        logger.info(f"Stop Loss: ${stop_loss:.2f} (Risk: ${abs(entry_price-stop_loss):.2f})")
        logger.info(f"Take Profit: ${take_profit:.2f} (Reward: ${abs(take_profit-entry_price):.2f})")
        
        # Store for position monitoring
        self.entry_symbol = symbol
        self.entry_side = side
        self.entry_quantity = quantity
        self.planned_sl = stop_loss
        self.planned_tp = take_profit
        
        # TRUE BRACKET ORDER - Use SDK OrderRequest model
        order = OrderRequest(
            account_id=self.account_id,
            exch_sym=symbol,
            side=OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            limit_price=entry_price,
            stop_loss=stop_loss,      # Bracket SL
            take_profit=take_profit,  # Bracket TP
            duration=DurationType.DAY  # Must be DAY for brackets
        )

        logger.info(f"\n📝 Bracket order payload: {order}")
        
        # Time the order placement
        t0 = time.perf_counter()
        response = self.client.place_order(self.account_id, order)
        latency_ms = (time.perf_counter() - t0) * 1000
        
        logger.info(f"\n📬 API Response: {response}")

        # Handle both dict and object responses
        if response:
            # Try dict access first
            order_id = response.get('orderId') if isinstance(response, dict) else getattr(response, 'order_id', None)
            strategy_id = response.get('strategyId') if isinstance(response, dict) else getattr(response, 'strategy_id', None)

            if order_id:
                self.order_id = order_id
                logger.info(f"✅ Bracket order placed in {latency_ms:.2f}ms")
                logger.info(f"Order ID: {self.order_id}")
                if strategy_id:
                    logger.info(f"Strategy ID: {strategy_id} (SL/TP are part of this bracket strategy)")
                logger.info(f"\n⏳ Waiting for order to fill...")
                return response

        logger.error(f"❌ Order failed: {response}")
        raise Exception("Order placement failed")
    
    async def place_stop_loss_take_profit(self, symbol: str, quantity: int, fill_price: float):
        """Place SL and TP orders after position is established."""
        
        logger.info(f"\n🛡️  PLACING STOP LOSS & TAKE PROFIT")

        # Determine opposite side for closing orders
        close_side = OrderSide.SELL if self.entry_side == "BUY" else OrderSide.BUY

        try:
            # Place Stop Loss order
            sl_order = OrderRequest(
                account_id=self.account_id,
                exch_sym=symbol,
                side=close_side,
                order_type=OrderType.STOP,
                quantity=abs(quantity),
                stop_price=self.planned_sl,
                duration=DurationType.DAY
            )
            
            t0 = time.perf_counter()
            sl_response = self.client.place_order(self.account_id, sl_order)
            sl_latency = (time.perf_counter() - t0) * 1000

            # Handle both dict and object responses
            sl_order_id = sl_response.get('orderId') if isinstance(sl_response, dict) else getattr(sl_response, 'order_id', None)
            if sl_order_id:
                self.sl_order_id = sl_order_id
                logger.info(f"✅ Stop Loss placed: ${self.planned_sl:.2f} ({sl_latency:.2f}ms)")
                play_notification("success")
            else:
                logger.error(f"❌ SL order failed: {sl_response}")

            # Place Take Profit order
            tp_order = OrderRequest(
                account_id=self.account_id,
                exch_sym=symbol,
                side=close_side,
                order_type=OrderType.LIMIT,
                quantity=abs(quantity),
                limit_price=self.planned_tp,
                duration=DurationType.DAY
            )

            t0 = time.perf_counter()
            tp_response = self.client.place_order(self.account_id, tp_order)
            tp_latency = (time.perf_counter() - t0) * 1000

            # Handle both dict and object responses
            tp_order_id = tp_response.get('orderId') if isinstance(tp_response, dict) else getattr(tp_response, 'order_id', None)
            if tp_order_id:
                self.tp_order_id = tp_order_id
                logger.info(f"✅ Take Profit placed: ${self.planned_tp:.2f} ({tp_latency:.2f}ms)")
                play_notification("success")
            else:
                logger.error(f"❌ TP order failed: {tp_response}")
                
        except Exception as e:
            logger.error(f"❌ Error placing SL/TP: {e}")
    
    async def find_sl_order_id(self):
        """Find the stop loss order ID from the bracket strategy."""
        try:
            logger.info("\n🔍 Finding SL order from bracket strategy...")
            
            # Get all orders for this account (ANY status includes all active orders)
            response = self.client.get_orders(self.account_id, order_status="ANY")
            
            # DEBUG: Show what we actually got
            logger.info(f"📋 Response type: {type(response)}")
            logger.info(f"📋 Response value: {response}")
            
            # Try multiple ways to extract orders
            orders = None
            if isinstance(response, dict):
                orders = response.get('orders', [])
            elif isinstance(response, list):
                orders = response
            elif hasattr(response, 'orders'):
                orders = response.orders
            elif hasattr(response, '__dict__'):
                logger.info(f"📋 Response __dict__: {response.__dict__}")
                orders = response.__dict__.get('orders', [])
            else:
                # Last resort - try to parse as JSON string
                try:
                    import json
                    parsed = json.loads(str(response))
                    orders = parsed.get('orders', [])
                except:
                    logger.error(f"❌ Cannot parse response: {response}")
                    return
            
            if not orders:
                logger.warning(f"⚠️  No orders found in response")
                return
                
            logger.info(f"📋 Found {len(orders)} total orders")
            
            # Look for STOP order for our symbol
            for i, order in enumerate(orders):
                # DEBUG each order
                logger.info(f"   Order {i}: type={type(order)}")
                
                # Handle string orders (shouldn't happen but...)
                if isinstance(order, str):
                    logger.warning(f"⚠️  Order is string: {order[:100]}")
                    continue
                
                # Convert to dict
                if isinstance(order, dict):
                    order_dict = order
                elif hasattr(order, '__dict__'):
                    order_dict = order.__dict__
                else:
                    logger.warning(f"⚠️  Cannot parse order type: {type(order)}")
                    continue
                
                order_type = order_dict.get('orderType', '')
                order_symbol = order_dict.get('exchSym', '')
                order_status = order_dict.get('status', '')
                order_id = order_dict.get('orderId', '')
                
                logger.info(f"      → {order_type} {order_symbol} {order_status} [{order_id}]")
                
                if (order_symbol == self.entry_symbol and 
                    order_type == 'STOP' and
                    order_status in ['WORKING', 'PENDING', 'ACCEPTED', 'NEW', 'SUBMITTED']):
                    
                    self.sl_order_id = order_id
                    sl_price = order_dict.get('stopPrice') or order_dict.get('price')
                    logger.info(f"✅ Found SL order: {self.sl_order_id} @ ${sl_price:.2f if sl_price else 'N/A'}")
                    return
            
            logger.warning("⚠️  Could not find SL order - auto-breakeven may not work")
            logger.warning(f"   Searched for: STOP order on {self.entry_symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error finding SL order: {e}")
            import traceback
            traceback.print_exc()
    
    def activate_auto_breakeven_after_fill(self, symbol: str, entry_price: float, side: str, quantity: int):
        """Activate auto breakeven manager and P&L tracker AFTER fill."""
        
        if not self.sl_order_id:
            logger.warning("⚠️  No SL order - skipping auto breakeven")
            return
        
        # Initialize auto breakeven with trailing stop (will modify the SL order)
        self.breakeven_manager = AutoBreakevenHFT(
            client=self.client,
            account_id=self.account_id,
            order_id=self.sl_order_id,  # Modify the SL order, not the entry order
            entry_price=entry_price,
            side=side,
            symbol=symbol,
            trigger_ticks=[20, 40, 60],
            sl_offset_ticks=[10, 30, 50],
            trailing_stop=True,
            trailing_distance=15
        )
        
        # Initialize P&L tracker
        self.pnl_tracker = PLTracker(
            entry_price=entry_price,
            quantity=quantity,
            side=side
        )
        
        play_notification("success")
        logger.info("\n🎯 AUTO BREAKEVEN & P&L TRACKING ACTIVATED")
        logger.info("📊 Monitoring price for breakeven triggers...")
    
    async def run(self, symbols: list, trading_symbol: str, 
                  side: str, entry_offset: float = -10):
        """Main trading loop."""
        
        try:
            # Connect to streaming
            logger.info("🌐 Connecting to market data...")
            self.stream = IronBeamStream(self.client)
            
            # Register callback BEFORE connecting
            self.stream.on_message(self.on_market_data)
            
            await self.stream.connect()
            logger.info("✅ Connected")
            
            # Start listen() as background task BEFORE subscriptions
            logger.info("👂 Starting message listener...")
            listen_task = asyncio.create_task(self.stream.listen())
            
            # Give listener a moment to start
            await asyncio.sleep(0.5)
            
            # Subscribe to symbols AFTER listener is running
            await self.subscribe_symbols(symbols)
            
            # Get current price for trading symbol
            price_data = self.price_cache.get(trading_symbol)
            if not price_data:
                logger.error(f"No price data for {trading_symbol}")
                return
            
            current_price = price_data['mid']
            logger.info(f"\n📈 Current {trading_symbol} price: ${current_price:.2f}")
            
            # Calculate order prices (entry_offset should be positive distance from market)
            # For BUY: entry above market so it doesn't fill immediately
            # For SELL: entry below market so it doesn't fill immediately
            if side.upper() == "BUY":
                entry_price = round(current_price + abs(entry_offset), 2)  # ABOVE market
                stop_loss = entry_price - 30
                take_profit = entry_price + 90
            else:
                entry_price = round(current_price - abs(entry_offset), 2)  # BELOW market
                stop_loss = entry_price + 30
                take_profit = entry_price - 90
            
            logger.info(f"\n💰 Order Prices:")
            logger.info(f"  Entry: ${entry_price:.2f} ({abs(entry_price-current_price):.2f} from market)")
            logger.info(f"  Stop Loss: ${stop_loss:.2f} (Risk: ${abs(entry_price-stop_loss):.2f})")
            logger.info(f"  Take Profit: ${take_profit:.2f} (Reward: ${abs(take_profit-entry_price):.2f})")
            logger.info(f"  R:R Ratio = 1:{abs(take_profit-entry_price)/abs(entry_price-stop_loss):.1f}")
            
            # Place bracket order
            input(f"\n[!] Press ENTER to place {side} bracket order at ${entry_price:.2f}... ")
            
            self.place_bracket_order(
                symbol=trading_symbol,
                side=side,
                quantity=1,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            # Auto-breakeven will activate automatically when order fills (detected in on_market_data)
            
            # Monitor
            logger.info("\n📊 MONITORING FOR FILL...")
            logger.info("Press Ctrl+C to stop\n")
            
            self.start_time = time.time()
            
            # Wait for listen task to run (it's running in background)
            try:
                await listen_task
            except asyncio.CancelledError:
                pass
            
        except KeyboardInterrupt:
            logger.info("\n⚠️  Stopped by user")
            
            # Cancel listen task
            if 'listen_task' in locals():
                listen_task.cancel()
                try:
                    await listen_task
                except asyncio.CancelledError:
                    pass
            
            # Show performance
            if self.start_time:
                elapsed = time.time() - self.start_time
                msg_rate = self.msg_count / elapsed if elapsed > 0 else 0
                logger.info(f"\n📊 Performance:")
                logger.info(f"  Messages: {self.msg_count}")
                logger.info(f"  Duration: {elapsed:.1f}s")
                logger.info(f"  Rate: {msg_rate:.0f} msg/s")
        
        finally:
            if self.stream:
                await self.stream.close()


async def main():
    """Main entry point."""
    
    # Load credentials
    api_key = os.getenv('Demo_Key')
    username = os.getenv('Demo_Username')
    password = os.getenv('Demo_Password')
    
    if not all([api_key, username, password]):
        raise ValueError("Missing credentials in .env file")
    
    logger.info("="*70)
    logger.info("HFT BRACKET ORDER WITH AUTO BREAKEVEN")
    logger.info("="*70)
    
    # Create trader
    trader = HFTBracketTrader(api_key, username, password)
    
    logger.info(f"✅ Authenticated - Account: {trader.account_id}")
    
    # Get balance
    balance = trader.client.get_account_balance(trader.account_id)
    equity = getattr(balance, 'totalEquity', 0)
    logger.info(f"💰 Equity: ${equity:,.2f}\n")
    
    # Symbols to monitor
    SYMBOLS = [
        "XCME:ES.Z25",  # E-mini S&P 500
        "XCME:NQ.Z25",  # E-mini Nasdaq
        "XCME:YM.Z25",  # E-mini Dow
        "XCEC:GC.Z25",  # Gold
        "XCEC:SI.Z25",  # Silver
    ]
    
    # Trading config
    TRADING_SYMBOL = "XCME:ES.Z25"
    SIDE = "BUY"  # or "SELL"
    
    # Run
    await trader.run(
        symbols=SYMBOLS,
        trading_symbol=TRADING_SYMBOL,
        side=SIDE,
        entry_offset=-10  # Entry 10 ticks from current price
    )


if __name__ == "__main__":
    asyncio.run(main())
