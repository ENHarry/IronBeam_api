"""
Execution Engine for Trade Management

Provides two execution models:
1. ThreadedExecutor: Polls positions via REST API at intervals
2. AsyncExecutor: Real-time execution using WebSocket price updates
"""

import threading
import time
import asyncio
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from .trade_manager import (
    AutoBreakevenManager,
    RunningTPManager,
    PositionState,
    AutoBreakevenConfig,
    RunningTPConfig
)
from .streaming import IronBeamStream
from .models import OrderSide

logger = logging.getLogger(__name__)


# ==================== Threaded Executor ====================

class ThreadedExecutor:
    """
    Background thread execution model.

    Polls positions and market data via REST API at regular intervals.
    Good for lower-frequency updates and simpler deployment.
    """

    def __init__(self, client, account_id: str, poll_interval: float = 1.0):
        """Initialize threaded executor.

        Args:
            client: IronBeam client instance
            account_id: Account ID to manage
            poll_interval: Polling interval in seconds (default: 1.0)
        """
        self.client = client
        self.account_id = account_id
        self.poll_interval = poll_interval

        # Trade managers
        self.breakeven_manager = AutoBreakevenManager(client, account_id)
        self.tp_manager = RunningTPManager(client, account_id)

        # Thread control
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

        # Rate limiting
        self._last_update_time: Dict[str, float] = {}
        self._min_update_interval = 0.5  # Minimum 0.5s between updates per order

    def add_auto_breakeven(
        self,
        order_id: str,
        position: PositionState,
        config: AutoBreakevenConfig
    ):
        """Add a position for auto breakeven management.

        Args:
            order_id: Order ID to manage
            position: Position state
            config: Breakeven configuration
        """
        with self._lock:
            self.breakeven_manager.start_monitoring(order_id, position, config)

    def add_running_tp(
        self,
        order_id: str,
        position: PositionState,
        config: RunningTPConfig
    ):
        """Add a position for running TP management.

        Args:
            order_id: Order ID to manage
            position: Position state
            config: Running TP configuration
        """
        with self._lock:
            self.tp_manager.start_monitoring(order_id, position, config)

    def remove_position(self, order_id: str):
        """Remove a position from management.

        Args:
            order_id: Order ID to remove
        """
        with self._lock:
            self.breakeven_manager.stop_monitoring(order_id)
            self.tp_manager.stop_monitoring(order_id)

    def start(self):
        """Start the background execution thread."""
        if self._running:
            logger.warning("Executor already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info(f"ThreadedExecutor started (poll_interval={self.poll_interval}s)")

    def stop(self):
        """Stop the background execution thread."""
        if not self._running:
            return

        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("ThreadedExecutor stopped")

    def _run_loop(self):
        """Main execution loop running in background thread."""
        while self._running:
            try:
                self._process_positions()
                time.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in execution loop: {e}", exc_info=True)

    def _process_positions(self):
        """Process all managed positions."""
        with self._lock:
            # Get all managed order IDs
            breakeven_orders = set(self.breakeven_manager.managed_positions.keys())
            tp_orders = set(self.tp_manager.managed_positions.keys())
            all_orders = breakeven_orders | tp_orders

            if not all_orders:
                return

            # Fetch current quotes for all positions
            symbols = set()
            for order_id in all_orders:
                if order_id in self.breakeven_manager.managed_positions:
                    position, _ = self.breakeven_manager.managed_positions[order_id]
                    symbols.add(position.symbol)
                elif order_id in self.tp_manager.managed_positions:
                    position, _ = self.tp_manager.managed_positions[order_id]
                    symbols.add(position.symbol)

            try:
                # Fetch quotes
                quotes_response = self.client.get_quotes(list(symbols))
                quotes_dict = {}

                if 'quotes' in quotes_response:
                    for quote in quotes_response['quotes']:
                        symbol = quote.get('exchSym')
                        # Use last price, or midpoint of bid/ask
                        price = quote.get('lastPrice')
                        if not price:
                            bid = quote.get('bidPrice')
                            ask = quote.get('askPrice')
                            if bid and ask:
                                price = (bid + ask) / 2
                        if price:
                            quotes_dict[symbol] = price

                # Process each position
                current_time = time.time()

                for order_id in all_orders:
                    # Rate limiting check
                    last_update = self._last_update_time.get(order_id, 0)
                    if current_time - last_update < self._min_update_interval:
                        continue

                    # Get position and current price
                    position = None
                    if order_id in self.breakeven_manager.managed_positions:
                        position, _ = self.breakeven_manager.managed_positions[order_id]
                    elif order_id in self.tp_manager.managed_positions:
                        position, _ = self.tp_manager.managed_positions[order_id]

                    if not position or position.symbol not in quotes_dict:
                        continue

                    current_price = quotes_dict[position.symbol]

                    # Check auto breakeven
                    if order_id in breakeven_orders:
                        updated = self.breakeven_manager.check_and_update(order_id, current_price)
                        if updated:
                            self._last_update_time[order_id] = current_time

                    # Check running TP
                    if order_id in tp_orders:
                        updated = self.tp_manager.check_and_update(order_id, current_price)
                        if updated:
                            self._last_update_time[order_id] = current_time

            except Exception as e:
                logger.error(f"Error processing positions: {e}", exc_info=True)


# ==================== Async Executor ====================

class AsyncExecutor:
    """
    Real-time async execution model using WebSocket.

    Reacts to price updates via WebSocket streaming for immediate execution.
    Best for low-latency requirements and high-frequency updates.
    """

    def __init__(self, client, account_id: str, stream: Optional[IronBeamStream] = None):
        """Initialize async executor.

        Args:
            client: IronBeam client instance
            account_id: Account ID to manage
            stream: Optional IronBeamStream instance (will create if not provided)
        """
        self.client = client
        self.account_id = account_id
        self.stream = stream or IronBeamStream(client)

        # Trade managers
        self.breakeven_manager = AutoBreakevenManager(client, account_id)
        self.tp_manager = RunningTPManager(client, account_id)

        # Task control
        self._running = False
        self._listen_task: Optional[asyncio.Task] = None

        # Tracked symbols for streaming
        self._tracked_symbols: set = set()

        # Current prices cache
        self._current_prices: Dict[str, float] = {}

        # Rate limiting
        self._last_update_time: Dict[str, float] = {}
        self._min_update_interval = 0.1  # 100ms minimum between updates

    async def add_auto_breakeven(
        self,
        order_id: str,
        position: PositionState,
        config: AutoBreakevenConfig
    ):
        """Add a position for auto breakeven management.

        Args:
            order_id: Order ID to manage
            position: Position state
            config: Breakeven configuration
        """
        self.breakeven_manager.start_monitoring(order_id, position, config)

        # Subscribe to symbol if not already subscribed
        await self._ensure_subscribed(position.symbol)

    async def add_running_tp(
        self,
        order_id: str,
        position: PositionState,
        config: RunningTPConfig
    ):
        """Add a position for running TP management.

        Args:
            order_id: Order ID to manage
            position: Position state
            config: Running TP configuration
        """
        self.tp_manager.start_monitoring(order_id, position, config)

        # Subscribe to symbol if not already subscribed
        await self._ensure_subscribed(position.symbol)

    async def remove_position(self, order_id: str):
        """Remove a position from management.

        Args:
            order_id: Order ID to remove
        """
        self.breakeven_manager.stop_monitoring(order_id)
        self.tp_manager.stop_monitoring(order_id)

        # Check if we can unsubscribe from symbols
        await self._cleanup_subscriptions()

    async def _ensure_subscribed(self, symbol: str):
        """Ensure we're subscribed to a symbol's quotes.

        Args:
            symbol: Symbol to subscribe to
        """
        if symbol not in self._tracked_symbols:
            if self.stream.state.value in ["CONNECTED"]:
                self.stream.subscribe_quotes([symbol])
                self._tracked_symbols.add(symbol)
                logger.info(f"Subscribed to quotes for {symbol}")

    async def _cleanup_subscriptions(self):
        """Unsubscribe from symbols no longer needed."""
        # Get all currently needed symbols
        needed_symbols = set()
        for position, _ in self.breakeven_manager.managed_positions.values():
            needed_symbols.add(position.symbol)
        for position, _ in self.tp_manager.managed_positions.values():
            needed_symbols.add(position.symbol)

        # Unsubscribe from symbols no longer needed
        symbols_to_remove = self._tracked_symbols - needed_symbols
        if symbols_to_remove:
            self.stream.unsubscribe_quotes(list(symbols_to_remove))
            self._tracked_symbols -= symbols_to_remove
            logger.info(f"Unsubscribed from {len(symbols_to_remove)} symbols")

    async def start(self):
        """Start the async executor and WebSocket connection."""
        if self._running:
            logger.warning("Executor already running")
            return

        self._running = True

        # Set up WebSocket callbacks
        self.stream.on_quote(self._handle_quote)
        self.stream.on_error(self._handle_error)

        # Connect and start listening
        await self.stream.connect()

        # Subscribe to all symbols
        all_symbols = set()
        for position, _ in self.breakeven_manager.managed_positions.values():
            all_symbols.add(position.symbol)
        for position, _ in self.tp_manager.managed_positions.values():
            all_symbols.add(position.symbol)

        if all_symbols:
            self.stream.subscribe_quotes(list(all_symbols))
            self._tracked_symbols.update(all_symbols)

        # Start listening
        self._listen_task = asyncio.create_task(self.stream.listen())

        logger.info("AsyncExecutor started with WebSocket streaming")

    async def stop(self):
        """Stop the async executor and close WebSocket connection."""
        if not self._running:
            return

        self._running = False

        # Cancel listen task
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        # Close stream
        await self.stream.close()

        logger.info("AsyncExecutor stopped")

    async def _handle_quote(self, quote_data: dict):
        """Handle incoming quote data from WebSocket.

        Args:
            quote_data: Quote data from WebSocket
        """
        try:
            symbol = quote_data.get('exchSym')
            if not symbol:
                return

            # Extract price
            price = quote_data.get('lastPrice')
            if not price:
                bid = quote_data.get('bidPrice')
                ask = quote_data.get('askPrice')
                if bid and ask:
                    price = (bid + ask) / 2

            if not price:
                return

            # Update price cache
            self._current_prices[symbol] = price

            # Process all positions for this symbol
            current_time = asyncio.get_event_loop().time()

            # Check breakeven positions
            for order_id, (position, _) in list(self.breakeven_manager.managed_positions.items()):
                if position.symbol == symbol:
                    # Rate limiting check
                    last_update = self._last_update_time.get(order_id, 0)
                    if current_time - last_update < self._min_update_interval:
                        continue

                    updated = self.breakeven_manager.check_and_update(order_id, price)
                    if updated:
                        self._last_update_time[order_id] = current_time

            # Check running TP positions
            for order_id, (position, _) in list(self.tp_manager.managed_positions.items()):
                if position.symbol == symbol:
                    # Rate limiting check
                    last_update = self._last_update_time.get(order_id, 0)
                    if current_time - last_update < self._min_update_interval:
                        continue

                    updated = self.tp_manager.check_and_update(order_id, price)
                    if updated:
                        self._last_update_time[order_id] = current_time

        except Exception as e:
            logger.error(f"Error handling quote: {e}", exc_info=True)

    async def _handle_error(self, error: Exception):
        """Handle WebSocket errors.

        Args:
            error: Exception that occurred
        """
        logger.error(f"WebSocket error: {error}")
