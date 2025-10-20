import requests
from .exceptions import AuthenticationError, InvalidRequestError

class IronBeam:
    def __init__(self, api_key, username, password=None):
        self.api_key = api_key
        self.username = username
        self.password = password
        self.base_url = "https://demo.ironbeamapi.com/v2"
        self.token = None

    def authenticate(self):
        """Authenticate and get a token."""
        payload = {
            "username": self.username,
            "apiKey": self.api_key
        }
        if self.password:
            payload["password"] = self.password
        
        response = requests.post(f"{self.base_url}/auth", json=payload)
        if response.status_code == 401:
            raise AuthenticationError("Unauthorized: Invalid API key or credentials.")
        if response.status_code == 400:
            raise InvalidRequestError(f"Invalid request: {response.text}")
        response.raise_for_status()
        self.token = response.json().get("token")
        return self.token

    def _get_headers(self):
        if not self.token:
            raise Exception("Authentication token not available. Please authenticate first.")
        return {"Authorization": f"Bearer {self.token}"}

    def get_trader_info(self):
        """Get trader information."""
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/info/trader", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_account_balance(self, account_id, balance_type="CURRENT_OPEN"):
        """Get account balance."""
        headers = self._get_headers()
        params = {"balanceType": balance_type}
        response = requests.get(f"{self.base_url}/account/{account_id}/balance", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_positions(self, account_id):
        """Get account positions."""
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/account/{account_id}/positions", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_risk(self, account_id):
        """Get account risk information."""
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/account/{account_id}/risk", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_fills(self, account_id):
        """Get account fills."""
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/account/{account_id}/fills", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_quotes(self, symbols):
        """Get quotes for a list of symbols."""
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/market/quotes", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_depth(self, symbols):
        """Get market depth for a list of symbols."""
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/market/depth", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_trades(self, symbol, from_time, to_time, max_records=100, earlier=True):
        """Get historical trades for a symbol."""
        headers = self._get_headers()
        url = f"{self.base_url}/market/trades/{symbol}/{from_time}/{to_time}/{max_records}/{earlier}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def place_order(self, account_id, order):
        """Place a new order."""
        headers = self._get_headers()
        response = requests.post(f"{self.base_url}/order/{account_id}/place", headers=headers, json=order)
        response.raise_for_status()
        return response.json()

    def update_order(self, account_id, order_id, order_update):
        """Update an existing order."""
        headers = self._get_headers()
        response = requests.put(f"{self.base_url}/order/{account_id}/update/{order_id}", headers=headers, json=order_update)
        response.raise_for_status()
        return response.json()

    def cancel_order(self, account_id, order_id):
        """Cancel an order."""
        headers = self._get_headers()
        response = requests.delete(f"{self.base_url}/order/{account_id}/cancel/{order_id}", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_orders(self, account_id, order_status="ANY"):
        """Get orders for an account."""
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/order/{account_id}/{order_status}", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_order_fills(self, account_id):
        """Get order fills for an account."""
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/order/{account_id}/fills", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_security_definitions(self, symbols):
        """Get security definitions for a list of symbols."""
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/info/security/definitions", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_symbols(self, text, limit=100, prefer_active=True):
        """Search for symbols."""
        headers = self._get_headers()
        params = {"text": text, "limit": limit, "preferActive": prefer_active}
        response = requests.get(f"{self.base_url}/info/symbols", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def create_simulated_trader(self, trader_details):
        """Create a simulated trader."""
        headers = self._get_headers()
        response = requests.post(f"{self.base_url}/simulatedTraderCreate", headers=headers, json=trader_details)
        response.raise_for_status()
        return response.json()

    def add_simulated_account(self, account_details):
        """Add a simulated account to a trader."""
        headers = self._get_headers()
        response = requests.post(f"{self.base_url}/simulatedAccountAdd", headers=headers, json=account_details)
        response.raise_for_status()
        return response.json()

    def create_stream(self):
        """Create a new stream for websocket communication."""
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/stream/create", headers=headers)
        response.raise_for_status()
        stream_id = response.json().get("streamId")
        return stream_id

    # ==================== Authentication Endpoints ====================

    def logout(self):
        """Logout and invalidate the current token."""
        headers = self._get_headers()
        response = requests.post(f"{self.base_url}/logout", headers=headers)
        response.raise_for_status()
        self.token = None
        return response.json()

    # ==================== Information Endpoints ====================

    def get_user_info(self):
        """Get user information."""
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/info/user", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_security_margin(self, symbols):
        """Get security margin and value information.

        Args:
            symbols: List of symbols (e.g., ["XCME:ES.Z24", "XCEC:GC.Q24"])
        """
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/info/security/margin", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_security_status(self, symbols):
        """Get security status information.

        Args:
            symbols: List of symbols
        """
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/info/security/status", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_exchange_sources(self):
        """Get list of available exchange sources."""
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/info/exchangeSources", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_complexes(self, exchange):
        """Get market complexes for an exchange.

        Args:
            exchange: Exchange code (e.g., "CME", "CBOT")
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/info/complexes/{exchange}", headers=headers)
        response.raise_for_status()
        return response.json()

    def search_futures(self, exchange, market_group):
        """Search for futures symbols.

        Args:
            exchange: Exchange code
            market_group: Market group
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/info/symbol/search/futures/{exchange}/{market_group}", headers=headers)
        response.raise_for_status()
        return response.json()

    def search_option_groups(self, complex):
        """Search for option symbol groups.

        Args:
            complex: Complex identifier
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/info/symbol/search/groups/{complex}", headers=headers)
        response.raise_for_status()
        return response.json()

    def search_options(self, symbol):
        """Search for option symbols.

        Args:
            symbol: Underlying symbol
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/info/symbol/search/options/{symbol}", headers=headers)
        response.raise_for_status()
        return response.json()

    def search_option_spreads(self, symbol):
        """Search for option spread symbols.

        Args:
            symbol: Underlying symbol
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/info/symbol/search/options/spreads/{symbol}", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_strategy_id(self, account_id, order_ids):
        """Get strategy ID for a list of order IDs.

        Args:
            account_id: Account ID
            order_ids: List of order IDs
        """
        headers = self._get_headers()
        params = {"orderIds": ",".join(order_ids)}
        response = requests.get(f"{self.base_url}/info/strategyId", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    # ==================== Order Management Endpoints ====================

    def cancel_multiple_orders(self, account_id, order_ids):
        """Cancel multiple orders at once.

        Args:
            account_id: Account ID
            order_ids: List of order IDs to cancel
        """
        headers = self._get_headers()
        payload = {"orderIds": order_ids}
        response = requests.delete(f"{self.base_url}/order/{account_id}/cancelMultiple", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def get_to_order_id(self, account_id, strategy_id):
        """Convert strategy ID to order ID.

        Args:
            account_id: Account ID
            strategy_id: Strategy ID
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/order/{account_id}/toorderid/{strategy_id}", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_to_strategy_id(self, account_id, order_id):
        """Convert order ID to strategy ID.

        Args:
            account_id: Account ID
            order_id: Order ID
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/order/{account_id}/tostrategyId/{order_id}", headers=headers)
        response.raise_for_status()
        return response.json()

    # ==================== Simulated Account Management ====================

    def simulated_account_reset(self, account_id, password):
        """Reset a simulated account to initial state.

        Args:
            account_id: Account ID to reset
            password: Account password
        """
        headers = self._get_headers()
        payload = {"accountId": account_id, "password": password}
        response = requests.put(f"{self.base_url}/simulatedAccountReset", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def simulated_account_expire(self, account_id, password):
        """Expire a simulated account.

        Args:
            account_id: Account ID to expire
            password: Account password
        """
        headers = self._get_headers()
        payload = {"accountId": account_id, "password": password}
        response = requests.delete(f"{self.base_url}/simulatedAccountExpire", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def simulated_account_add_cash(self, account_id, password, amount, currency="USD"):
        """Add cash to a simulated account.

        Args:
            account_id: Account ID
            password: Account password
            amount: Amount to add
            currency: Currency code (default: USD)
        """
        headers = self._get_headers()
        payload = {
            "accountId": account_id,
            "password": password,
            "amount": amount,
            "currency": currency
        }
        response = requests.post(f"{self.base_url}/simulatedAccount/addCash", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def simulated_account_get_cash_report(self, account_id):
        """Get cash report for a simulated account.

        Args:
            account_id: Account ID
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/simulatedAccount/getCashReport/{account_id}", headers=headers)
        response.raise_for_status()
        return response.json()

    # ==================== Streaming Subscription Endpoints ====================

    def subscribe_quotes(self, stream_id, symbols):
        """Subscribe to quote updates for symbols.

        Args:
            stream_id: Stream ID from create_stream()
            symbols: List of symbols to subscribe
        """
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/market/quotes/subscribe/{stream_id}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def subscribe_depths(self, stream_id, symbols):
        """Subscribe to market depth updates for symbols.

        Args:
            stream_id: Stream ID from create_stream()
            symbols: List of symbols to subscribe
        """
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/market/depths/subscribe/{stream_id}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def subscribe_trades(self, stream_id, symbols):
        """Subscribe to trade updates for symbols.

        Args:
            stream_id: Stream ID from create_stream()
            symbols: List of symbols to subscribe
        """
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/market/trades/subscribe/{stream_id}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def unsubscribe_quotes(self, stream_id, symbols):
        """Unsubscribe from quote updates.

        Args:
            stream_id: Stream ID
            symbols: List of symbols to unsubscribe
        """
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/market/quotes/unsubscribe/{stream_id}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def unsubscribe_depths(self, stream_id, symbols):
        """Unsubscribe from market depth updates.

        Args:
            stream_id: Stream ID
            symbols: List of symbols to unsubscribe
        """
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/market/depths/unsubscribe/{stream_id}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def unsubscribe_trades(self, stream_id, symbols):
        """Unsubscribe from trade updates.

        Args:
            stream_id: Stream ID
            symbols: List of symbols to unsubscribe
        """
        headers = self._get_headers()
        params = {"symbols": ",".join(symbols)}
        response = requests.get(f"{self.base_url}/market/trades/unsubscribe/{stream_id}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def subscribe_tick_bars(self, stream_id, symbol, bar_size):
        """Subscribe to tick bar indicator.

        Args:
            stream_id: Stream ID
            symbol: Symbol to subscribe
            bar_size: Number of ticks per bar
        """
        headers = self._get_headers()
        payload = {"exchSym": symbol, "barSize": bar_size}
        response = requests.post(f"{self.base_url}/indicator/{stream_id}/tickBars/subscribe", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def subscribe_trade_bars(self, stream_id, symbol, bar_size):
        """Subscribe to trade bar indicator.

        Args:
            stream_id: Stream ID
            symbol: Symbol to subscribe
            bar_size: Number of trades per bar
        """
        headers = self._get_headers()
        payload = {"exchSym": symbol, "barSize": bar_size}
        response = requests.post(f"{self.base_url}/indicator/{stream_id}/tradeBars/subscribe", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def subscribe_time_bars(self, stream_id, symbol, bar_size):
        """Subscribe to time bar indicator.

        Args:
            stream_id: Stream ID
            symbol: Symbol to subscribe
            bar_size: Time period in seconds
        """
        headers = self._get_headers()
        payload = {"exchSym": symbol, "barSize": bar_size}
        response = requests.post(f"{self.base_url}/indicator/{stream_id}/timeBars/subscribe", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def subscribe_volume_bars(self, stream_id, symbol, bar_size):
        """Subscribe to volume bar indicator.

        Args:
            stream_id: Stream ID
            symbol: Symbol to subscribe
            bar_size: Volume per bar
        """
        headers = self._get_headers()
        payload = {"exchSym": symbol, "barSize": bar_size}
        response = requests.post(f"{self.base_url}/indicator/{stream_id}/volumeBars/subscribe", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def unsubscribe_indicator(self, stream_id, indicator_id):
        """Unsubscribe from an indicator.

        Args:
            stream_id: Stream ID
            indicator_id: Indicator ID to unsubscribe
        """
        headers = self._get_headers()
        response = requests.delete(f"{self.base_url}/indicator/{stream_id}/unsubscribe/{indicator_id}", headers=headers)
        response.raise_for_status()
        return response.json()
