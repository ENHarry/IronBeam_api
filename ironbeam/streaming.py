import asyncio
import websockets
import json
import logging
from typing import Callable, Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class ConnectionState(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"
    CLOSED = "CLOSED"


class IronBeamStream:
    """Enhanced WebSocket streaming client for IronBeam API.

    Features:
    - Automatic reconnection with exponential backoff
    - Subscription management
    - Event-driven message handling
    - Connection state management
    """

    def __init__(self, client, mode="demo", base_url: Optional[str] = None):
        """Initialize the streaming client.

        Args:
            client: IronBeam client instance (for API calls and token)
            base_url: WebSocket base URL
        """
        self.client = client

        if base_url is None:
            if mode == "demo":
                base_url = "wss://demo.ironbeamapi.com/v2"
            if mode == "live":
                base_url = "wss://live.ironbeamapi.com/v2"
        self.base_url = base_url
        self.stream_id = None
        self.websocket = None
        self.state = ConnectionState.DISCONNECTED

        # Callbacks
        self.on_message_callback: Optional[Callable] = None
        self.on_quote_callback: Optional[Callable] = None
        self.on_depth_callback: Optional[Callable] = None
        self.on_trade_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None

        # Reconnection settings
        self.auto_reconnect = True
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0  # seconds
        self.reconnect_attempt = 0

        # Keep track of subscriptions for reconnection
        self.subscriptions = {
            'quotes': set(),
            'depths': set(),
            'trades': set(),
            'indicators': {}
        }

    async def connect(self):
        """Create a stream and connect to the websocket."""
        try:
            self.state = ConnectionState.CONNECTING

            # Create stream ID via REST API
            self.stream_id = self.client.create_stream()
            logger.info(f"Created stream ID: {self.stream_id}")

            # Build WebSocket URI
            uri = f"{self.base_url}/stream/{self.stream_id}?token={self.client.token}"

            # Connect to WebSocket
            self.websocket = await websockets.connect(uri)
            self.state = ConnectionState.CONNECTED
            self.reconnect_attempt = 0

            logger.info(f"Connected to WebSocket stream: {self.stream_id}")

            # Fire connect callback
            if self.on_connect_callback:
                await self.on_connect_callback(self.stream_id)

            return self.websocket

        except Exception as e:
            self.state = ConnectionState.DISCONNECTED
            logger.error(f"Failed to connect: {e}")
            if self.on_error_callback:
                await self.on_error_callback(e)
            raise

    async def listen(self):
        """Listen for messages from the stream with auto-reconnect."""
        while True:
            try:
                if self.state != ConnectionState.CONNECTED:
                    await self.connect()

                    # Resubscribe after reconnection
                    if self.reconnect_attempt > 0:
                        await self._resubscribe()

                async for message in self.websocket:
                    try:
                        data = json.loads(message)
                        await self._handle_message(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message: {e}")
                        if self.on_error_callback:
                            await self.on_error_callback(e)

            except websockets.exceptions.ConnectionClosed:
                self.state = ConnectionState.DISCONNECTED
                logger.warning("WebSocket connection closed")

                if self.on_disconnect_callback:
                    await self.on_disconnect_callback()

                if self.auto_reconnect and self.reconnect_attempt < self.max_reconnect_attempts:
                    await self._reconnect()
                else:
                    logger.error("Max reconnection attempts reached")
                    break

            except Exception as e:
                logger.error(f"Error in listen loop: {e}")
                if self.on_error_callback:
                    await self.on_error_callback(e)

                if self.auto_reconnect:
                    await self._reconnect()
                else:
                    break

    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming messages and route to appropriate callbacks."""
        # Generic message callback
        if self.on_message_callback:
            await self.on_message_callback(data)

        # Route to specific callbacks based on message type
        message_type = data.get('type') or data.get('messageType')

        if message_type == 'quote' and self.on_quote_callback:
            await self.on_quote_callback(data)
        elif message_type == 'depth' and self.on_depth_callback:
            await self.on_depth_callback(data)
        elif message_type == 'trade' and self.on_trade_callback:
            await self.on_trade_callback(data)

    async def _reconnect(self):
        """Attempt to reconnect with exponential backoff."""
        self.state = ConnectionState.RECONNECTING
        self.reconnect_attempt += 1

        delay = self.reconnect_delay * (2 ** (self.reconnect_attempt - 1))
        logger.info(f"Reconnecting in {delay} seconds (attempt {self.reconnect_attempt}/{self.max_reconnect_attempts})")

        await asyncio.sleep(delay)

    async def _resubscribe(self):
        """Resubscribe to all previous subscriptions after reconnection."""
        logger.info("Resubscribing to previous subscriptions...")

        # Resubscribe to quotes
        if self.subscriptions['quotes']:
            symbols = list(self.subscriptions['quotes'])
            self.client.subscribe_quotes(self.stream_id, symbols)
            logger.info(f"Resubscribed to quotes: {symbols}")

        # Resubscribe to depths
        if self.subscriptions['depths']:
            symbols = list(self.subscriptions['depths'])
            self.client.subscribe_depths(self.stream_id, symbols)
            logger.info(f"Resubscribed to depths: {symbols}")

        # Resubscribe to trades
        if self.subscriptions['trades']:
            symbols = list(self.subscriptions['trades'])
            self.client.subscribe_trades(self.stream_id, symbols)
            logger.info(f"Resubscribed to trades: {symbols}")

        # Resubscribe to indicators
        for indicator_type, params in self.subscriptions['indicators'].items():
            # Resubscribe to indicators (implementation depends on API)
            pass

    def subscribe_quotes(self, symbols: List[str]):
        """Subscribe to quote updates.

        Args:
            symbols: List of symbols to subscribe
        """
        if not self.stream_id:
            raise RuntimeError("Not connected. Call connect() first.")

        self.client.subscribe_quotes(self.stream_id, symbols)
        self.subscriptions['quotes'].update(symbols)
        logger.info(f"Subscribed to quotes: {symbols}")

    def subscribe_depths(self, symbols: List[str]):
        """Subscribe to market depth updates.

        Args:
            symbols: List of symbols to subscribe
        """
        if not self.stream_id:
            raise RuntimeError("Not connected. Call connect() first.")

        self.client.subscribe_depths(self.stream_id, symbols)
        self.subscriptions['depths'].update(symbols)
        logger.info(f"Subscribed to depths: {symbols}")

    def subscribe_trades(self, symbols: List[str]):
        """Subscribe to trade updates.

        Args:
            symbols: List of symbols to subscribe
        """
        if not self.stream_id:
            raise RuntimeError("Not connected. Call connect() first.")

        self.client.subscribe_trades(self.stream_id, symbols)
        self.subscriptions['trades'].update(symbols)
        logger.info(f"Subscribed to trades: {symbols}")

    def unsubscribe_quotes(self, symbols: List[str]):
        """Unsubscribe from quote updates."""
        if not self.stream_id:
            raise RuntimeError("Not connected.")

        self.client.unsubscribe_quotes(self.stream_id, symbols)
        self.subscriptions['quotes'].difference_update(symbols)
        logger.info(f"Unsubscribed from quotes: {symbols}")

    def unsubscribe_depths(self, symbols: List[str]):
        """Unsubscribe from depth updates."""
        if not self.stream_id:
            raise RuntimeError("Not connected.")

        self.client.unsubscribe_depths(self.stream_id, symbols)
        self.subscriptions['depths'].difference_update(symbols)
        logger.info(f"Unsubscribed from depths: {symbols}")

    def unsubscribe_trades(self, symbols: List[str]):
        """Unsubscribe from trade updates."""
        if not self.stream_id:
            raise RuntimeError("Not connected.")

        self.client.unsubscribe_trades(self.stream_id, symbols)
        self.subscriptions['trades'].difference_update(symbols)
        logger.info(f"Unsubscribed from trades: {symbols}")

    def on_message(self, callback: Callable):
        """Register callback for all messages."""
        self.on_message_callback = callback

    def on_quote(self, callback: Callable):
        """Register callback for quote updates."""
        self.on_quote_callback = callback

    def on_depth(self, callback: Callable):
        """Register callback for depth updates."""
        self.on_depth_callback = callback

    def on_trade(self, callback: Callable):
        """Register callback for trade updates."""
        self.on_trade_callback = callback

    def on_error(self, callback: Callable):
        """Register callback for errors."""
        self.on_error_callback = callback

    def on_connect(self, callback: Callable):
        """Register callback for connection events."""
        self.on_connect_callback = callback

    def on_disconnect(self, callback: Callable):
        """Register callback for disconnection events."""
        self.on_disconnect_callback = callback

    async def close(self):
        """Close the websocket connection."""
        self.state = ConnectionState.CLOSED
        self.auto_reconnect = False

        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket connection closed")

        self.websocket = None
        self.stream_id = None
