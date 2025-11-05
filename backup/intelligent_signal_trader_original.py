#!/usr/bin/env python3
"""
Intelligent Signal-Based Trading Bot

This bot combines multiple technical indicators with advanced risk management:
- Uses OptimizedSignalGenerator for signal generation
- Integrates IronBeam SDK's trade_manager.py for position management
- Runs continuously during market hours (6pm-4:30pm, pauses weekends)
- Implements time-based, profit-based, and SDK-based position closing
- Handles bracket orders with dynamic stop-loss and take-profit management

Author: IronBeam API Enhanced Bot
Date: November 2025
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta, time
from typing import Optional, Dict, List
import pandas as pd
from dotenv import load_dotenv

# Add the import fix for running from project directory
current_dir = os.getcwd()
if current_dir in sys.path:
    sys.path.remove(current_dir)

# Force removal of any local ironbeam imports
modules_to_remove = [mod for mod in sys.modules if mod.startswith('ironbeam')]
for mod in modules_to_remove:
    del sys.modules[mod]

# Now import ironbeam - it will use the installed package with fixes
import ironbeam
from ironbeam import (
    IronBeam, IronBeamStream, OrderRequest, OrderType, OrderSide, 
    DurationType, OrderStatus, ConnectionState, ThreadedExecutor,
    AutoBreakevenConfig, RunningTPConfig, PositionState, BreakevenState
)

from indicators_optimized import OptimizedSignalGenerator

# Load environment variables
load_dotenv()

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class IntelligentSignalTrader:
    """
    Advanced signal-based trading bot with intelligent risk management.
    
    Features:
    - Multi-indicator signal generation with voting system
    - SDK-integrated trade management (auto-breakeven, running TP)
    - Time-based and profit-based position closing
    - Market hours awareness with weekend pause
    - Real-time WebSocket streaming for low-latency execution
    - Comprehensive position monitoring and risk management
    """
    
    def __init__(
        self,
        client: IronBeam,
        account_id: str,
        symbol: str,
        quantity: int = 1,
        risk_per_trade: float = 10.0,
        profit_target_multiplier: float = 2.0,
        max_hold_minutes: int = 300,  # 5 hours max hold
        profit_close_percentage: float = 20.0,  # Close at 20% of risk as profit
        # Signal generator parameters
        atr_period: int = 10,
        atr_multiplier: float = 3.0,
        overbought_oversold_length: int = 5,
        swing_period: int = 15,
        ma_period: int = 20,
        adx_period: int = 14,
        # Trade management parameters
        auto_breakeven_enabled: bool = True,
        running_tp_enabled: bool = True,
        min_bars_for_signals: int = 50
    ):
        """Initialize the intelligent trading bot."""
        self.client = client
        self.account_id = account_id
        self.symbol = symbol
        self.quantity = quantity
        self.risk_per_trade = risk_per_trade
        self.profit_target_multiplier = profit_target_multiplier
        self.max_hold_minutes = max_hold_minutes
        self.profit_close_percentage = profit_close_percentage
        self.min_bars_for_signals = min_bars_for_signals
        
        # Initialize signal generator
        self.signal_generator = OptimizedSignalGenerator(
            atr_period=atr_period,
            atr_multiplier=atr_multiplier,
            overbought_oversold_length=overbought_oversold_length,
            swing_period=swing_period,
            ma_period=ma_period,
            adx_period=adx_period
        )
        
        # Trading state
        self.is_running = False
        self.current_position: Optional[Dict] = None
        self.position_entry_time: Optional[datetime] = None
        self.bars_data: List[Dict] = []
        
        # Position management state
        self.bracket_child_orders: Dict[str, bool] = {}  # Track SL/TP child order success
        self.last_signal_direction: Optional[str] = None  # Track signal changes for reversal detection
        self.position_monitoring_active = False
        
        # WebSocket streaming
        self.stream: Optional[IronBeamStream] = None
        self.streaming_active = False
        
        # Trade management integration
        self.trade_executor: Optional[ThreadedExecutor] = None
        self.auto_breakeven_enabled = auto_breakeven_enabled
        self.running_tp_enabled = running_tp_enabled
        
        # Performance tracking
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.total_trades = 0
        
        logger.info("🤖 Intelligent Signal Trader initialized")
        logger.info(f"   Symbol: {symbol}, Quantity: {quantity}")
        logger.info(f"   Risk per trade: ${risk_per_trade}")
        logger.info(f"   Max hold time: {max_hold_minutes} minutes")
        logger.info(f"   Auto-breakeven: {'✅' if auto_breakeven_enabled else '❌'}")
        logger.info(f"   Running TP: {'✅' if running_tp_enabled else '❌'}")

    def is_market_hours(self) -> bool:
        """
        Check if we're in trading hours (6pm-4:30pm next day, Mon-Fri).
        Pauses Friday 4:30pm to Sunday 6pm.
        """
        now = datetime.now()
        current_time = now.time()
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Friday after 4:30pm - pause until Sunday 6pm
        if weekday == 4 and current_time >= time(16, 30):  # Friday 4:30pm+
            return False
        
        # Saturday - no trading
        if weekday == 5:
            return False
        
        # Sunday before 6pm - no trading
        if weekday == 6 and current_time < time(18, 0):
            return False
        
        # Monday-Thursday: 6pm-4:30pm next day
        # Friday: 6pm-4:30pm (then pause)
        # Sunday: 6pm+ (resume)
        
        # Between 6pm and midnight
        if current_time >= time(18, 0):
            return True
        
        # Between midnight and 4:30pm
        if current_time <= time(16, 30):
            return True
        
        # Between 4:30pm and 6pm - no trading
        return False

    async def start_streaming(self):
        """Initialize and start WebSocket streaming."""
        try:
            logger.info("🔄 Starting WebSocket stream...")
            
            # Create WebSocket stream
            self.stream = IronBeamStream(self.client)
            
            # Register message callback
            self.stream.on_message(self.on_market_data)
            
            # Connect to WebSocket
            await self.stream.connect()
            logger.info("🌐 WebSocket connected")
            
            # Start listener task
            listen_task = asyncio.create_task(self.stream.listen())
            
            # Subscribe to symbol
            self.stream.subscribe_quotes([self.symbol])
            logger.info(f"📊 Subscribed to quotes for {self.symbol}")
            
            self.streaming_active = True
            logger.info("✅ Streaming started")
            
            # Wait for listener task (runs forever)
            await listen_task
            
        except Exception as e:
            logger.error(f"❌ Error in streaming: {e}")
            self.streaming_active = False

    async def on_market_data(self, msg):
        """Handle incoming WebSocket messages."""
        try:
            if 'q' in msg and msg['q']:
                for quote in msg['q']:
                    symbol = quote.get('s')
                    bid = quote.get('b')
                    ask = quote.get('a')
                    last = quote.get('l')
                    
                    if symbol == self.symbol and bid and ask:
                        # Calculate OHLC bar data (simplified 1-minute bars)
                        current_time = datetime.now()
                        current_minute = current_time.replace(second=0, microsecond=0)
                        
                        price = (bid + ask) / 2
                        
                        # Update or create current bar
                        if (not self.bars_data or 
                            self.bars_data[-1]['timestamp'] < current_minute):
                            # New bar
                            new_bar = {
                                'timestamp': current_minute,
                                'open': price,
                                'high': price,
                                'low': price,
                                'close': price,
                                'volume': 0
                            }
                            self.bars_data.append(new_bar)
                            logger.debug(f"📊 New bar: {current_minute} O:{price:.2f}")
                        else:
                            # Update current bar
                            current_bar = self.bars_data[-1]
                            current_bar['high'] = max(current_bar['high'], price)
                            current_bar['low'] = min(current_bar['low'], price)
                            current_bar['close'] = price
                        
                        # Limit bars to last 200 for memory efficiency
                        if len(self.bars_data) > 200:
                            self.bars_data = self.bars_data[-200:]
                        
                        # Check if we have enough data for signals
                        if len(self.bars_data) >= self.min_bars_for_signals:
                            await self.process_signals()
                        
                        # Monitor existing position
                        if self.current_position:
                            await self.monitor_position(price)
                        
        except Exception as e:
            logger.error(f"❌ Error processing market data: {e}")

    async def process_signals(self):
        """Process trading signals and execute trades."""
        try:
            if not self.is_market_hours():
                return
            
            # Convert bars to DataFrame
            df = pd.DataFrame(self.bars_data)
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            # Generate signals
            signal_details = self.signal_generator.get_signal_details(df)
            
            current_signal = signal_details['final_signal']
            adx_strength = signal_details['adx_trend_strength']
            adx_value = signal_details['adx']
            
            # Log signal status every 5 minutes
            now = datetime.now()
            if now.minute % 5 == 0 and now.second < 5:
                position_status = f" | Position: {self.current_position['side']} {self.symbol}" if self.current_position else " | No Position"
                logger.info(f"📡 Signal: {current_signal} | ST:{signal_details['supertrend']} "
                           f"OB/OS:{signal_details['overbought_oversold']} TR:{signal_details['trending']} | "
                           f"Votes: Buy={signal_details['buy_votes']}/3, Sell={signal_details['sell_votes']}/3 | "
                           f"ADX: {adx_value:.1f} ({adx_strength}){position_status}")
            
            # If we have an open position, check for reversal signals
            if self.current_position and self.current_position['filled']:
                await self.check_signal_reversal(current_signal, signal_details)
                # Update last signal for trend monitoring
                self.last_signal_direction = current_signal
                return
            
            # No position - check if we can open new trades
            # Only trade on strong signals with good ADX
            if current_signal in ['BUY', 'SELL'] and adx_value >= 25:
                # Check if we have at least 2 out of 3 indicator agreement
                required_votes = 2
                if current_signal == 'BUY' and signal_details['buy_votes'] >= required_votes:
                    await self.place_trade('BUY', signal_details)
                elif current_signal == 'SELL' and signal_details['sell_votes'] >= required_votes:
                    await self.place_trade('SELL', signal_details)
            
            # Update last signal
            self.last_signal_direction = current_signal
                
        except Exception as e:
            logger.error(f"❌ Error processing signals: {e}")

    async def check_signal_reversal(self, current_signal: str, signal_details: Dict):
        """Check if current signals indicate a reversal and close position if needed."""
        try:
            if not self.current_position or not self.current_position['filled']:
                return
            
            position_side = self.current_position['side']
            adx_value = signal_details['adx']
            
            # Determine if this is a strong reversal signal
            is_reversal = False
            reversal_strength = 0
            
            # Check for signal direction change with strong ADX
            if current_signal in ['BUY', 'SELL']:
                # Strong reversal: opposite signal with 2+ votes and ADX >= 30
                if ((position_side == 'BUY' and current_signal == 'SELL' and signal_details['sell_votes'] >= 2) or
                    (position_side == 'SELL' and current_signal == 'BUY' and signal_details['buy_votes'] >= 2)):
                    
                    if adx_value >= 30:  # Strong ADX confirmation
                        is_reversal = True
                        reversal_strength = 3
                        logger.info(f"🔄 STRONG REVERSAL detected: {position_side} position vs {current_signal} signal (ADX: {adx_value:.1f})")
                    elif adx_value >= 25:  # Moderate ADX confirmation
                        is_reversal = True
                        reversal_strength = 2
                        logger.info(f"🔄 MODERATE REVERSAL detected: {position_side} position vs {current_signal} signal (ADX: {adx_value:.1f})")
            
            # Check for trend weakening (ADX declining below 20)
            elif adx_value < 20 and self.last_signal_direction != current_signal:
                is_reversal = True
                reversal_strength = 1
                logger.info(f"📉 TREND WEAKENING detected: ADX {adx_value:.1f} < 20 with signal change")
            
            # Close position on reversal
            if is_reversal:
                logger.info(f"⚡ Closing position due to signal reversal (strength: {reversal_strength}/3)")
                await self.close_position(f"SIGNAL_REVERSAL_STRENGTH_{reversal_strength}")
                
        except Exception as e:
            logger.error(f"❌ Error checking signal reversal: {e}")

    async def place_trade(self, direction: str, signal_details: Dict):
        """Place a new trade with intelligent risk management."""
        try:
            # Get current market price
            quotes = self.client.get_quotes([self.symbol])
            if not quotes or not quotes.quotes:
                logger.error(f"❌ Could not get quote for {self.symbol}")
                return
            
            quote = quotes.quotes[0]
            bid = quote.bid_price or 0
            ask = quote.ask_price or 0
            mid_price = (bid + ask) / 2
            
            # Determine order side
            side = OrderSide.BUY if direction == 'BUY' else OrderSide.SELL
            
            # Calculate stop loss and take profit
            if direction == 'BUY':
                stop_loss_price = mid_price - self.risk_per_trade
                take_profit_price = mid_price + (self.risk_per_trade * self.profit_target_multiplier)
            else:
                stop_loss_price = mid_price + self.risk_per_trade
                take_profit_price = mid_price - (self.risk_per_trade * self.profit_target_multiplier)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"🟢 {direction} SIGNAL TRIGGERED")
            logger.info(f"{'='*60}")
            logger.info(f"📊 Signal Details:")
            logger.info(f"   Final Signal: {signal_details['final_signal']}")
            logger.info(f"   Supertrend: {signal_details['supertrend']}")
            logger.info(f"   OB/OS: {signal_details['overbought_oversold']}")
            logger.info(f"   Trending: {signal_details['trending']}")
            logger.info(f"   Votes: Buy={signal_details['buy_votes']}, Sell={signal_details['sell_votes']}")
            logger.info(f"   ADX: {signal_details['adx']:.1f} ({signal_details['adx_trend_strength']})")
            logger.info(f"")
            logger.info(f"💰 Trade Setup:")
            logger.info(f"   Symbol: {self.symbol}")
            logger.info(f"   Side: {direction}")
            logger.info(f"   Quantity: {self.quantity}")
            logger.info(f"   Entry: ~{mid_price:.2f}")
            logger.info(f"   Stop Loss: {stop_loss_price:.2f}")
            logger.info(f"   Take Profit: {take_profit_price:.2f}")
            logger.info(f"   Risk: ${self.risk_per_trade}")
            logger.info(f"   Reward: ${self.risk_per_trade * self.profit_target_multiplier}")
            logger.info(f"{'='*60}\n")
            
            # Create bracket order with trade management features
            order = OrderRequest(
                accountId=self.account_id,
                exchSym=self.symbol,
                side=side,
                quantity=self.quantity,
                orderType=OrderType.LIMIT,
                limitPrice=mid_price,
                duration=DurationType.DAY,
                stopPrice=None,
                stopLoss=stop_loss_price,
                takeProfit=take_profit_price,
                stopLossOffset=None,
                takeProfitOffset=None,
                trailingStop=None,
                waitForOrderId=True
            )
            
            # Place the order
            response = self.client.place_order(self.account_id, order)
            
            if response and hasattr(response, 'order_id'):
                order_id = response.order_id
                logger.info(f"✅ {direction} order placed successfully!")
                logger.info(f"   Order ID: {order_id}")
                
                # Track position
                self.current_position = {
                    'order_id': order_id,
                    'side': direction,
                    'entry_price': mid_price,
                    'stop_loss': stop_loss_price,
                    'take_profit': take_profit_price,
                    'quantity': self.quantity,
                    'filled': False,
                    'fill_time': None,
                    'has_stop_loss_order': False,
                    'has_take_profit_order': False
                }
                self.position_entry_time = datetime.now()
                self.bracket_child_orders = {'stop_loss': False, 'take_profit': False}
                self.position_monitoring_active = True
                
                # Start monitoring for fill
                if order_id:  # Type guard
                    asyncio.create_task(self.monitor_order_fill(order_id))
                
            else:
                logger.error(f"❌ Order placement failed: {response}")
                
        except Exception as e:
            logger.error(f"❌ Error placing trade: {e}")

    async def monitor_order_fill(self, order_id: str):
        """Monitor order until filled, then set up trade management."""
        try:
            logger.info("⏳ Monitoring for order fill...")
            
            while self.current_position and not self.current_position['filled']:
                await asyncio.sleep(2)
                
                # Check order status and child orders
                orders_response = self.client.get_orders(self.account_id)
                
                if orders_response and hasattr(orders_response, 'orders'):
                    parent_filled = False
                    
                    for order in orders_response.orders:
                        # Check parent order
                        if order.order_id == order_id and order.status == OrderStatus.FILLED:
                            parent_filled = True
                            
                            # Order filled!
                            self.current_position['filled'] = True
                            self.current_position['fill_time'] = datetime.now()
                            
                            # Get actual fill price
                            fills = self.client.get_fills(self.account_id)
                            if fills and hasattr(fills, 'fills'):
                                for fill in fills.fills:
                                    if fill.order_id == order_id:
                                        self.current_position['entry_price'] = fill.price
                                        break
                            
                            logger.info(f"✅ Order filled! Entry: {self.current_position['entry_price']:.2f}")
                            
                            # Set up SDK trade management
                            await self.setup_trade_management(order_id)
                            
                            self.trades_today += 1
                            self.total_trades += 1
                        
                        # Check for child orders (SL/TP) if parent is filled
                        elif parent_filled and hasattr(order, 'parent_order_id') and str(order.parent_order_id) == str(order_id):
                            # This is a child order of our bracket
                            if 'STOP' in str(order.order_type) or order.stop_price:
                                self.current_position['has_stop_loss_order'] = True
                                self.bracket_child_orders['stop_loss'] = True
                                logger.info(f"✅ Stop-loss child order detected: {order.order_id}")
                            elif order.limit_price and order.limit_price != self.current_position['entry_price']:
                                self.current_position['has_take_profit_order'] = True
                                self.bracket_child_orders['take_profit'] = True
                                logger.info(f"✅ Take-profit child order detected: {order.order_id}")
                    
                    # If parent is filled, check if we need to create missing child orders
                    if parent_filled:
                        await self.check_and_create_missing_orders(order_id)
                        break
                        
        except Exception as e:
            logger.error(f"❌ Error monitoring order fill: {e}")

    async def check_and_create_missing_orders(self, parent_order_id: str):
        """Create stop-loss or take-profit orders if bracket child orders weren't successful."""
        try:
            if not self.current_position or not self.current_position['filled']:
                return
            
            # Wait a moment for child orders to appear
            await asyncio.sleep(3)
            
            missing_orders = []
            
            # Check if stop-loss order is missing
            if not self.bracket_child_orders['stop_loss']:
                missing_orders.append('stop_loss')
                logger.warning("⚠️  Stop-loss child order missing from bracket - will create manually")
            
            # Check if take-profit order is missing  
            if not self.bracket_child_orders['take_profit']:
                missing_orders.append('take_profit')
                logger.warning("⚠️  Take-profit child order missing from bracket - will create manually")
            
            # Create missing orders
            for order_type in missing_orders:
                await self.create_protective_order(order_type, parent_order_id)
                
        except Exception as e:
            logger.error(f"❌ Error checking missing orders: {e}")

    async def create_protective_order(self, order_type: str, parent_order_id: str):
        """Create a stop-loss or take-profit order manually."""
        try:
            if not self.current_position:
                return
            
            position = self.current_position
            
            if order_type == 'stop_loss':
                # Create stop-loss order
                stop_side = OrderSide.SELL if position['side'] == 'BUY' else OrderSide.BUY
                
                logger.info(f"🛡️  Creating manual stop-loss order at {position['stop_loss']:.2f}")
                
                stop_order = OrderRequest(
                    accountId=self.account_id,
                    exchSym=self.symbol,
                    side=stop_side,
                    quantity=self.quantity,
                    orderType=OrderType.STOP,
                    duration=DurationType.DAY,
                    limitPrice=None,
                    stopPrice=position['stop_loss'],
                    stopLoss=None,
                    takeProfit=None,
                    stopLossOffset=None,
                    takeProfitOffset=None,
                    trailingStop=None,
                    waitForOrderId=True
                )
                
                response = self.client.place_order(self.account_id, stop_order)
                
                if response and hasattr(response, 'order_id'):
                    self.current_position['has_stop_loss_order'] = True
                    self.bracket_child_orders['stop_loss'] = True
                    logger.info(f"✅ Manual stop-loss created: {response.order_id}")
                else:
                    logger.error(f"❌ Failed to create stop-loss: {response}")
            
            elif order_type == 'take_profit':
                # Create take-profit order
                tp_side = OrderSide.SELL if position['side'] == 'BUY' else OrderSide.BUY
                
                logger.info(f"🎯 Creating manual take-profit order at {position['take_profit']:.2f}")
                
                tp_order = OrderRequest(
                    accountId=self.account_id,
                    exchSym=self.symbol,
                    side=tp_side,
                    quantity=self.quantity,
                    orderType=OrderType.LIMIT,
                    duration=DurationType.DAY,
                    limitPrice=position['take_profit'],
                    stopPrice=None,
                    stopLoss=None,
                    takeProfit=None,
                    stopLossOffset=None,
                    takeProfitOffset=None,
                    trailingStop=None,
                    waitForOrderId=True
                )
                
                response = self.client.place_order(self.account_id, tp_order)
                
                if response and hasattr(response, 'order_id'):
                    self.current_position['has_take_profit_order'] = True
                    self.bracket_child_orders['take_profit'] = True
                    logger.info(f"✅ Manual take-profit created: {response.order_id}")
                else:
                    logger.error(f"❌ Failed to create take-profit: {response}")
                    
        except Exception as e:
            logger.error(f"❌ Error creating {order_type} order: {e}")

    async def setup_trade_management(self, order_id: str):
        """Set up SDK-based trade management for filled position."""
        try:
            if not (self.auto_breakeven_enabled or self.running_tp_enabled):
                logger.info("⚠️  SDK trade management disabled - using basic monitoring only")
                return
            
            if not self.current_position:
                logger.error("❌ No current position to set up trade management for")
                return
            
            # Create position state for SDK trade manager
            position_side = OrderSide.BUY if self.current_position['side'] == 'BUY' else OrderSide.SELL
            
            position_state = PositionState(
                order_id=order_id,
                account_id=self.account_id,
                symbol=self.symbol,
                side=position_side,
                entry_price=self.current_position['entry_price'],
                quantity=self.current_position['quantity'],
                current_stop_loss=self.current_position['stop_loss'],
                current_take_profit=self.current_position['take_profit']
            )
            
            # Initialize trade executor if not already done
            if not self.trade_executor:
                self.trade_executor = ThreadedExecutor(self.client, self.account_id)
                self.trade_executor.start()
                logger.info("🔧 Trade executor started")
            
            # Configure auto-breakeven
            if self.auto_breakeven_enabled:
                breakeven_config = AutoBreakevenConfig(
                    trigger_mode="ticks",
                    trigger_levels=[15, 30, 45],  # Move SL at 15, 30, 45 ticks profit
                    sl_offsets=[5, 15, 25],       # Move SL to +5, +15, +25 ticks from entry
                    enabled=True
                )
                
                self.trade_executor.add_auto_breakeven(order_id, position_state, breakeven_config)
                logger.info("🛡️  Auto-breakeven activated: [15→+5, 30→+15, 45→+25 ticks]")
                logger.info("    💡 Auto-breakeven will update stop-loss orders automatically")
            
            # Configure running take profit
            if self.running_tp_enabled:
                tp_config = RunningTPConfig(
                    enable_trailing_extremes=True,
                    enable_profit_levels=False,  # Keep it simple
                    trail_offset_ticks=20,       # Trail TP 20 ticks behind high/low
                    enabled=True
                )
                
                self.trade_executor.add_running_tp(order_id, position_state, tp_config)
                logger.info("📈 Running take-profit activated: trailing 20 ticks behind extremes")
                logger.info("    💡 Running TP will update take-profit orders automatically")
            
            logger.info("✅ SDK trade management fully configured")
            logger.info("    🔧 The SDK will now automatically manage stop-loss and take-profit levels")
            
        except Exception as e:
            logger.error(f"❌ Error setting up trade management: {e}")

    async def monitor_position(self, current_price: float):
        """Monitor existing position for time-based and profit-based exits."""
        try:
            if not self.current_position or not self.current_position['filled']:
                return
            
            position = self.current_position
            entry_price = position['entry_price']
            is_long = position['side'] == 'BUY'
            
            # Calculate current profit/loss
            if is_long:
                pnl = (current_price - entry_price) * self.quantity
            else:
                pnl = (entry_price - current_price) * self.quantity
            
            # Calculate time held
            time_held = datetime.now() - position['fill_time']
            minutes_held = time_held.total_seconds() / 60
            
            # Check time-based exit (max hold time)
            if minutes_held >= self.max_hold_minutes:
                logger.info(f"⏰ Max hold time reached ({self.max_hold_minutes} min) - closing position")
                await self.close_position("TIME_LIMIT")
                return
            
            # Check profit-based exit (20% of risk)
            profit_target = self.risk_per_trade * (self.profit_close_percentage / 100)
            if pnl >= profit_target:
                logger.info(f"💰 Profit target reached (${pnl:.2f} >= ${profit_target:.2f}) - closing position")
                await self.close_position("PROFIT_TARGET")
                return
            
            # Log position status every 10 minutes
            if int(minutes_held) % 10 == 0 and int(time_held.total_seconds()) % 600 < 5:
                profit_pct = (pnl / self.risk_per_trade) * 100
                sl_status = "✅" if self.current_position.get('has_stop_loss_order', False) else "❌"
                tp_status = "✅" if self.current_position.get('has_take_profit_order', False) else "❌"
                
                logger.info(f"📊 Position status: {position['side']} {self.symbol} | "
                           f"P&L: ${pnl:.2f} ({profit_pct:+.1f}%) | "
                           f"Time: {int(minutes_held)}m/{self.max_hold_minutes}m | "
                           f"SL: {sl_status} TP: {tp_status}")
                
                # Check if we need to create missing protective orders
                if not self.current_position.get('has_stop_loss_order', False) or not self.current_position.get('has_take_profit_order', False):
                    await self.check_and_create_missing_orders(position['order_id'])
                
        except Exception as e:
            logger.error(f"❌ Error monitoring position: {e}")

    async def close_position(self, reason: str):
        """Close the current position."""
        try:
            if not self.current_position:
                return
            
            position = self.current_position
            close_side = OrderSide.SELL if position['side'] == 'BUY' else OrderSide.BUY
            
            logger.info(f"\n{'='*60}")
            logger.info(f"🔴 CLOSING POSITION - {reason}")
            logger.info(f"{'='*60}")
            logger.info(f"Position: {position['side']} {self.quantity} {self.symbol}")
            logger.info(f"Entry: {position['entry_price']:.2f}")
            logger.info(f"Closing with: {close_side.value} MARKET order")
            
            # Place market close order
            close_order = OrderRequest(
                accountId=self.account_id,
                exchSym=self.symbol,
                side=close_side,
                quantity=self.quantity,
                orderType=OrderType.MARKET,
                duration=DurationType.DAY,
                limitPrice=None,
                stopPrice=None,
                stopLoss=None,
                takeProfit=None,
                stopLossOffset=None,
                takeProfitOffset=None,
                trailingStop=None,
                waitForOrderId=True
            )
            
            response = self.client.place_order(self.account_id, close_order)
            
            if response and hasattr(response, 'order_id'):
                logger.info(f"✅ Close order placed - Order ID: {response.order_id}")
                
                # Stop SDK trade management for this position
                if self.trade_executor and position['order_id']:
                    self.trade_executor.remove_position(position['order_id'])
                    logger.info("🛡️  SDK trade management stopped for position")
                
                # Clear position tracking
                self.current_position = None
                self.position_entry_time = None
                self.bracket_child_orders = {}
                self.position_monitoring_active = False
                
                # Brief pause to let the order fill
                await asyncio.sleep(3)
                logger.info(f"✅ Position closed - Reason: {reason}\n")
                
            else:
                logger.error(f"❌ Failed to close position: {response}")
                
        except Exception as e:
            logger.error(f"❌ Error closing position: {e}")

    async def cleanup_and_exit(self):
        """Clean up resources and exit gracefully."""
        try:
            logger.info("\n🛑 Shutting down bot...")
            
            # Close any open positions
            if self.current_position:
                await self.close_position("SHUTDOWN")
            
            # Stop trade executor
            if self.trade_executor:
                self.trade_executor.stop()
                logger.info("🔧 Trade executor stopped")
            
            # Close WebSocket
            if self.stream:
                await self.stream.close()
                logger.info("🌐 WebSocket closed")
            
            # Final statistics
            logger.info(f"\n📊 Session Summary:")
            logger.info(f"   Trades today: {self.trades_today}")
            logger.info(f"   Total trades: {self.total_trades}")
            logger.info(f"   Daily P&L: ${self.daily_pnl:.2f}")
            
            logger.info("✅ Bot shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

    async def run(self):
        """Main bot execution loop."""
        try:
            logger.info("\n" + "="*60)
            logger.info("🤖 INTELLIGENT SIGNAL TRADER STARTING")
            logger.info("="*60)
            logger.info(f"🚀 Starting streaming and execution tasks...")
            logger.info(f"📊 Minimum bars required: {self.min_bars_for_signals}")
            logger.info(f"⏱️  Will accumulate data before generating signals...")
            logger.info("")
            
            self.is_running = True
            
            # Start WebSocket streaming
            streaming_task = asyncio.create_task(self.start_streaming())
            
            # Main monitoring loop
            while self.is_running:
                try:
                    # Check market hours
                    if not self.is_market_hours():
                        # Market closed - log status and wait
                        now = datetime.now()
                        if now.minute % 30 == 0:  # Log every 30 minutes during off-hours
                            logger.info("😴 Market closed - bot paused (Fri 4:30pm - Sun 6pm)")
                        await asyncio.sleep(60)  # Check every minute
                        continue
                    
                    # Market open - normal operation
                    await asyncio.sleep(5)  # Main loop delay
                    
                except KeyboardInterrupt:
                    logger.info("\n⚠️  Shutdown requested by user")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in main loop: {e}")
                    await asyncio.sleep(10)
            
        except Exception as e:
            logger.error(f"❌ Fatal error in bot: {e}")
        finally:
            self.is_running = False
            await self.cleanup_and_exit()


async def main():
    """Main entry point for the intelligent trading bot."""
    try:
        # Load credentials
        api_key = os.getenv('Demo_Key')
        username = os.getenv('Demo_Username')
        password = os.getenv('Demo_Password')
        
        if not all([api_key, username, password]):
            raise ValueError("Missing credentials in .env file")
        
        # Trading parameters
        SYMBOL = "XCEC:MGC.Z25"  # Micro Gold December 2025
        QUANTITY = 1
        RISK_PER_TRADE = 10.0    # Risk $10 per trade
        PROFIT_TARGET_MULT = 2.0  # 2:1 reward:risk ratio
        MAX_HOLD_MINUTES = 300   # 5 hours max hold
        PROFIT_CLOSE_PCT = 20.0  # Close at 20% of risk as profit
        
        logger.info("🔗 Initializing IronBeam client...")
        client = IronBeam(api_key=api_key, username=username, password=password, mode="demo")
        
        logger.info("🔐 Authenticating...")
        client.authenticate()
        
        # Get account info
        trader_info = client.get_trader_info()
        account_id = trader_info.accounts[0]
        logger.info(f"✅ Authenticated - Account: {account_id}")
        
        # Get balance
        balance = client.get_account_balance(account_id)
        equity = getattr(balance.balances[0], 'cashBalance', 0)
        logger.info(f"💰 Account Equity: ${equity:,.2f}")
        
        # Create and run the intelligent trader
        bot = IntelligentSignalTrader(
            client=client,
            account_id=account_id,
            symbol=SYMBOL,
            quantity=QUANTITY,
            risk_per_trade=RISK_PER_TRADE,
            profit_target_multiplier=PROFIT_TARGET_MULT,
            max_hold_minutes=MAX_HOLD_MINUTES,
            profit_close_percentage=PROFIT_CLOSE_PCT,
            auto_breakeven_enabled=True,
            running_tp_enabled=True
        )
        
        # Run the bot
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Bot interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """
    Intelligent Signal Trading Bot
    
    This bot:
    - Uses multiple technical indicators for signal generation
    - Integrates with IronBeam SDK's trade management system
    - Runs during market hours (6pm-4:30pm, pauses weekends)
    - Implements comprehensive risk management
    - Provides real-time monitoring and position management
    
    To run:
    1. Ensure .env file has Demo_Key, Demo_Username, Demo_Password
    2. Run: python intelligent_signal_trader.py
    3. Press Ctrl+C to stop gracefully
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  Script interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
