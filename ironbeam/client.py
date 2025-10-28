import requests
from typing import List, Optional, Union, Dict, Any
from .exceptions import AuthenticationError, InvalidRequestError
from .models import (
    # Authentication
    AuthenticationRequest, Token, LogoutResponse,
    # Account
    AccountBalanceRequest, AccountBalance, TraderInfo, UserInfo,
    AccountPositions, AccountRisk, AccountFills,
    # Orders
    OrderRequest, OrderUpdateRequest, OrderResponse, OrdersRequest, OrdersResponse,
    CancelOrderResponse, CancelMultipleRequest, CancelMultipleResponse,
    OrdersFillsResponse,
    # Market Data
    QuotesRequest, QuotesResponse, DepthRequest, DepthResponse,
    TradesRequest, TradesResponse,
    SecurityDefinitionsRequest, SecurityDefinitionsResponse,
    SecurityMarginResponse, SecurityStatusResponse,
    # Symbols
    SymbolSearchRequest, SymbolsResponse, ExchangeSourcesResponse,
    ComplexRequest, ComplexesResponse,
    FuturesSearchRequest, OptionsSearchRequest,
    StrategyIdRequest, StrategyIdResponse, OrderIdResponse, StrategyIdMappingResponse,
    # Streaming
    StreamResponse, SubscriptionResponse, UnsubscriptionResponse,
    IndicatorSubscriptionRequest, IndicatorSubscriptionResponse,
    IndicatorUnsubscriptionResponse,
    # Simulated
    SimulatedTraderRequest, SimulatedAccountRequest, SimulatedAccountResponse,
    SimulatedAccountCashRequest, SimulatedAccountCashResponse,
    SimulatedAccountResetResponse, SimulatedAccountExpireResponse,
    CashReportResponse,
    # Utility
    TradableAssetsResponse, PopularSymbolsResponse, KeywordSearchResponse,
    # Enums
    BalanceType, OrderStatus
)

class IronBeam:
    def __init__(self, api_key, username, password=None):
        self.api_key = api_key
        self.username = username
        self.password = password
        self.base_url = "https://demo.ironbeamapi.com/v2"
        self.token = None

    def authenticate(self, request: Optional[AuthenticationRequest] = None) -> Token:
        """Authenticate and get a token.

        Args:
            request: Authentication request (optional, will use init params if not provided)

        Returns:
            Token response with authentication token

        Raises:
            AuthenticationError: If authentication fails
            InvalidRequestError: If request is invalid
        """
        if request:
            # Use Pydantic v2 method
            payload = request.model_dump(by_alias=True, exclude_none=True)
        else:
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

        token_data = response.json()
        self.token = token_data.get("token")
        return Token(**token_data)

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for authenticated requests."""
        if not self.token:
            raise Exception("Authentication token not available. Please authenticate first.")
        return {"Authorization": f"Bearer {self.token}"}

    def get_trader_info(self) -> TraderInfo:
        """Get trader information.

        Returns:
            TraderInfo with account details
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/info/trader", headers=headers)
        response.raise_for_status()
        return TraderInfo(**response.json())

    def get_account_balance(
        self,
        request: Union[AccountBalanceRequest, str],
        balance_type: Optional[BalanceType] = None
    ) -> AccountBalance:
        """Get account balance.

        Args:
            request: AccountBalanceRequest or account_id string
            balance_type: Balance type (if request is string)

        Returns:
            AccountBalance with balance details
        """
        headers = self._get_headers()

        if isinstance(request, str):
            # Backward compatibility: accept account_id as string
            account_id = request
            balance_type_val = balance_type or BalanceType.CURRENT_OPEN
            params = {"balanceType": balance_type_val.value}
        else:
            account_id = request.account_id
            # Handle both enum and string values (Pydantic may convert enums to strings)
            bt = request.balance_type
            params = {"balanceType": bt.value if isinstance(bt, BalanceType) else bt}

        response = requests.get(f"{self.base_url}/account/{account_id}/balance", headers=headers, params=params)
        response.raise_for_status()
        return AccountBalance(**response.json())

    def get_positions(self, account_id: str) -> AccountPositions:
        """Get account positions.

        Args:
            account_id: Account ID

        Returns:
            AccountPositions with position list
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/account/{account_id}/positions", headers=headers)
        response.raise_for_status()
        return AccountPositions(**response.json())

    def get_risk(self, account_id: str) -> AccountRisk:
        """Get account risk information.

        Args:
            account_id: Account ID

        Returns:
            AccountRisk with risk metrics
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/account/{account_id}/risk", headers=headers)
        response.raise_for_status()
        return AccountRisk(**response.json())

    def get_fills(self, account_id: str) -> AccountFills:
        """Get account fills.

        Args:
            account_id: Account ID

        Returns:
            AccountFills with fill history
        """
        headers = self._get_headers()
        response = requests.get(f"{self.base_url}/account/{account_id}/fills", headers=headers)
        response.raise_for_status()
        return AccountFills(**response.json())

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
        # Convert Pydantic model to dict if necessary
        if hasattr(order, 'model_dump'):
            order = order.model_dump(by_alias=True, exclude_none=True)
        response = requests.post(f"{self.base_url}/order/{account_id}/place", headers=headers, json=order)
        response.raise_for_status()
        return response.json()

    def update_order(self, account_id, order_id, order_update):
        """Update an existing order."""
        headers = self._get_headers()
        # Convert Pydantic model to dict if necessary
        if hasattr(order_update, 'model_dump'):
            order_update = order_update.model_dump(by_alias=True, exclude_none=True)
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

    # ==================== Utility Methods ====================

    def get_all_tradable_assets(self, asset_types=None, exchanges=None, limit_per_type=100):
        """Get a comprehensive list of all tradable assets.

        This is a convenience method that queries multiple asset types and exchanges
        to build a comprehensive list of available trading instruments.

        Args:
            asset_types: List of asset types to query (default: ['futures'])
                        Options: 'futures', 'options', 'spreads'
            exchanges: List of exchanges to query (default: all available)
            limit_per_type: Maximum results per asset type/exchange combination

        Returns:
            Dictionary with categorized assets:
            {
                'futures': {
                    'CME': {'ES': [...], 'NQ': [...], ...},
                    'COMEX': {'GC': [...], 'MGC': [...], ...},
                    ...
                },
                'options': {...},
                'summary': {
                    'total_assets': int,
                    'by_exchange': {...},
                    'by_type': {...}
                }
            }
        """
        # Default asset types
        if asset_types is None:
            asset_types = ['futures']

        # Get available exchanges if not specified
        if exchanges is None:
            try:
                exchanges_response = self.get_exchange_sources()
                exchanges = [ex['exchange'] for ex in exchanges_response.get('exchanges', [])]
            except:
                # Fallback to common exchanges
                exchanges = ['CME', 'CBOT', 'COMEX', 'NYMEX', 'ICE']

        results = {
            'futures': {},
            'options': {},
            'spreads': {},
            'summary': {
                'total_assets': 0,
                'by_exchange': {},
                'by_type': {}
            }
        }

        # Query futures
        if 'futures' in asset_types:
            for exchange in exchanges:
                try:
                    # Get complexes (market groups) for this exchange
                    complexes_response = self.get_complexes(exchange)
                    complexes = complexes_response.get('complexes', [])

                    results['futures'][exchange] = {}

                    for complex_item in complexes:
                        complex_code = complex_item.get('complex', '')

                        try:
                            # Search futures for this complex
                            futures_response = self.search_futures(exchange, complex_code)
                            symbols = futures_response.get('symbols', [])

                            if symbols:
                                # Group by base symbol
                                base_symbols = {}
                                for symbol in symbols:
                                    sym = symbol.get('symbol', '')
                                    # Extract base symbol (e.g., ES from ES.Z25)
                                    base = sym.split('.')[0] if '.' in sym else sym
                                    if base not in base_symbols:
                                        base_symbols[base] = []
                                    base_symbols[base].append(symbol)

                                results['futures'][exchange][complex_code] = base_symbols
                                results['summary']['total_assets'] += len(symbols)

                        except Exception as e:
                            # Skip if complex fails
                            continue

                    # Update summary
                    exchange_count = sum(
                        sum(len(contracts) for contracts in group.values())
                        for group in results['futures'].get(exchange, {}).values()
                    )
                    results['summary']['by_exchange'][exchange] = exchange_count

                except Exception as e:
                    # Skip if exchange fails
                    continue

        # Query options
        if 'options' in asset_types:
            # Options require underlying symbols, which is more complex
            # This is a simplified version - can be expanded
            pass

        # Update type summary
        results['summary']['by_type']['futures'] = sum(
            count for count in results['summary']['by_exchange'].values()
        )

        return results

    def get_popular_symbols(self):
        """Get a curated list of popular/commonly traded symbols.

        Returns:
            Dictionary with popular symbols by category
        """
        popular = {
            'equity_indices': [
                {'symbol': 'XCME:ES.Z25', 'name': 'E-mini S&P 500', 'exchange': 'CME'},
                {'symbol': 'XCME:NQ.Z25', 'name': 'E-mini NASDAQ-100', 'exchange': 'CME'},
                {'symbol': 'XCME:YM.Z25', 'name': 'E-mini Dow', 'exchange': 'CME'},
                {'symbol': 'XCME:RTY.Z25', 'name': 'E-mini Russell 2000', 'exchange': 'CME'},
                {'symbol': 'XCME:MES.Z25', 'name': 'Micro E-mini S&P 500', 'exchange': 'CME'},
                {'symbol': 'XCME:MNQ.Z25', 'name': 'Micro E-mini NASDAQ-100', 'exchange': 'CME'},
            ],
            'commodities': {
                'precious_metals': [
                    {'symbol': 'XCEC:GC.Z25', 'name': 'Gold Futures', 'exchange': 'COMEX'},
                    {'symbol': 'XCEC:SI.Z25', 'name': 'Silver Futures', 'exchange': 'COMEX'},
                    {'symbol': 'XCEC:MGC.Z25', 'name': 'Micro Gold Futures', 'exchange': 'COMEX'},
                    {'symbol': 'XCEC:SIL.Z25', 'name': 'Micro Silver Futures', 'exchange': 'COMEX'},
                ],
                'energy': [
                    {'symbol': 'XNYM:CL.Z25', 'name': 'Crude Oil', 'exchange': 'NYMEX'},
                    {'symbol': 'XNYM:NG.Z25', 'name': 'Natural Gas', 'exchange': 'NYMEX'},
                    {'symbol': 'XNYM:RB.Z25', 'name': 'Gasoline', 'exchange': 'NYMEX'},
                ],
                'agriculture': [
                    {'symbol': 'XCBT:ZC.Z25', 'name': 'Corn', 'exchange': 'CBOT'},
                    {'symbol': 'XCBT:ZS.Z25', 'name': 'Soybeans', 'exchange': 'CBOT'},
                    {'symbol': 'XCBT:ZW.Z25', 'name': 'Wheat', 'exchange': 'CBOT'},
                ]
            },
            'currencies': [
                {'symbol': 'XCME:6E.Z25', 'name': 'Euro FX', 'exchange': 'CME'},
                {'symbol': 'XCME:6B.Z25', 'name': 'British Pound', 'exchange': 'CME'},
                {'symbol': 'XCME:6J.Z25', 'name': 'Japanese Yen', 'exchange': 'CME'},
            ],
            'rates': [
                {'symbol': 'XCBT:ZN.Z25', 'name': '10-Year T-Note', 'exchange': 'CBOT'},
                {'symbol': 'XCBT:ZB.Z25', 'name': '30-Year T-Bond', 'exchange': 'CBOT'},
            ]
        }

        return popular

    def search_symbols_by_keyword(self, keyword, limit=50):
        """Search for symbols by keyword across all exchanges.

        Args:
            keyword: Search term (e.g., 'gold', 'oil', 'euro')
            limit: Maximum number of results

        Returns:
            List of matching symbols with details
        """
        try:
            result = self.get_symbols(keyword, limit=limit, prefer_active=True)
            symbols = result.get('symbols', [])

            # Enhance with categorization
            categorized = {
                'symbols': symbols,
                'count': len(symbols),
                'keyword': keyword
            }

            return categorized
        except Exception as e:
            return {
                'symbols': [],
                'count': 0,
                'keyword': keyword,
                'error': str(e)
            }
