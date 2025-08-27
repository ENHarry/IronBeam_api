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
