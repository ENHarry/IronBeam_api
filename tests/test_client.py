import unittest
from unittest.mock import patch, Mock
from ironbeam.client import IronBeam

class TestIronBeamAPI(unittest.TestCase):

    def setUp(self):
        self.api = IronBeam(api_key="test_api_key", username="test_username")

    @patch('requests.post')
    def test_authenticate(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "test_token"}
        mock_post.return_value = mock_response

        token = self.api.authenticate()
        self.assertEqual(token, "test_token")
        self.assertEqual(self.api.token, "test_token")

    @patch('requests.get')
    def test_get_trader_info(self, mock_get):
        self.api.token = "test_token"  # Simulate authenticated state
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"traderId": "test_trader"}
        mock_get.return_value = mock_response

        trader_info = self.api.get_trader_info()
        self.assertEqual(trader_info, {"traderId": "test_trader"})

    @patch('requests.get')
    def test_get_account_balance(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"balance": 10000}
        mock_get.return_value = mock_response

        balance = self.api.get_account_balance("test_account_id")
        self.assertEqual(balance, {"balance": 10000})

    @patch('requests.get')
    def test_get_positions(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"symbol": "AAPL", "quantity": 10}]
        mock_get.return_value = mock_response

        positions = self.api.get_positions("test_account_id")
        self.assertEqual(positions, [{"symbol": "AAPL", "quantity": 10}])

    @patch('requests.get')
    def test_get_risk(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"risk_level": "low"}
        mock_get.return_value = mock_response

        risk = self.api.get_risk("test_account_id")
        self.assertEqual(risk, {"risk_level": "low"})

    @patch('requests.get')
    def test_get_fills(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"symbol": "AAPL", "price": 150}]
        mock_get.return_value = mock_response

        fills = self.api.get_fills("test_account_id")
        self.assertEqual(fills, [{"symbol": "AAPL", "price": 150}])

    @patch('requests.get')
    def test_get_quotes(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Quotes": []}
        mock_get.return_value = mock_response

        quotes = self.api.get_quotes(["AAPL", "GOOG"])
        self.assertEqual(quotes, {"Quotes": []})

    @patch('requests.get')
    def test_get_depth(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Depths": []}
        mock_get.return_value = mock_response

        depth = self.api.get_depth(["AAPL"])
        self.assertEqual(depth, {"Depths": []})

    @patch('requests.get')
    def test_get_trades(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"trades": []}
        mock_get.return_value = mock_response

        trades = self.api.get_trades("AAPL", 1609459200000, 1609545600000)
        self.assertEqual(trades, {"trades": []})

    @patch('requests.post')
    def test_place_order(self, mock_post):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"orderId": "123"}
        mock_post.return_value = mock_response

        order_details = {"symbol": "AAPL", "quantity": 10, "side": "BUY", "orderType": "MARKET", "duration": "DAY"}
        order_response = self.api.place_order("test_account_id", order_details)
        self.assertEqual(order_response, {"orderId": "123"})

    @patch('requests.put')
    def test_update_order(self, mock_put):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_put.return_value = mock_response

        update_details = {"quantity": 15}
        update_response = self.api.update_order("test_account_id", "123", update_details)
        self.assertEqual(update_response, {"status": "OK"})

    @patch('requests.delete')
    def test_cancel_order(self, mock_delete):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_delete.return_value = mock_response

        cancel_response = self.api.cancel_order("test_account_id", "123")
        self.assertEqual(cancel_response, {"status": "OK"})

    @patch('requests.get')
    def test_get_orders(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"orders": []}
        mock_get.return_value = mock_response

        orders = self.api.get_orders("test_account_id")
        self.assertEqual(orders, {"orders": []})

    @patch('requests.get')
    def test_get_order_fills(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"fills": []}
        mock_get.return_value = mock_response

        fills = self.api.get_order_fills("test_account_id")
        self.assertEqual(fills, {"fills": []})

    @patch('requests.get')
    def test_get_security_definitions(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"securityDefinitions": []}
        mock_get.return_value = mock_response

        definitions = self.api.get_security_definitions(["AAPL"])
        self.assertEqual(definitions, {"securityDefinitions": []})

    @patch('requests.get')
    def test_get_symbols(self, mock_get):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"symbols": []}
        mock_get.return_value = mock_response

        symbols = self.api.get_symbols("AAP")
        self.assertEqual(symbols, {"symbols": []})

    @patch('requests.post')
    def test_create_simulated_trader(self, mock_post):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"TraderId": "sim_trader_1"}
        mock_post.return_value = mock_response

        trader_details = {
            "FirstName": "Test", "LastName": "User", "Email": "test@example.com", 
            "Password": "password", "TemplateId": "EVAL50", "Address1": "123 Main St",
            "City": "Anytown", "State": "CA", "Country": "USA", "ZipCode": "12345", "Phone": "555-555-5555"
        }
        response = self.api.create_simulated_trader(trader_details)
        self.assertEqual(response, {"TraderId": "sim_trader_1"})

    @patch('requests.post')
    def test_add_simulated_account(self, mock_post):
        self.api.token = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"AccountId": "sim_account_1"}
        mock_post.return_value = mock_response

        account_details = {"TraderId": "sim_trader_1", "Password": "password", "TemplateId": "EVAL50"}
        response = self.api.add_simulated_account(account_details)
        self.assertEqual(response, {"AccountId": "sim_account_1"})

if __name__ == '__main__':
    unittest.main()
