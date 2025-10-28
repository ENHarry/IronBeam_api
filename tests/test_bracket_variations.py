"""
Test bracket order variations to find what works
"""
from ironbeam import IronBeam
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Demo credentials
DEMO_USERNAME = os.getenv('Demo_Username')
DEMO_PASSWORD = os.getenv('Demo_Password')
DEMO_KEY = os.getenv('Demo_Key')

def test_bracket_variations():
    print("="*70)
    print("TESTING BRACKET ORDER VARIATIONS")
    print("="*70)
    
    # Initialize and authenticate
    client = IronBeam(
        api_key=DEMO_KEY,
        username=DEMO_USERNAME,
        password=DEMO_PASSWORD
    )
    
    client.authenticate()
    print("✓ Authenticated\n")
    
    # Get account info
    trader_info = client.get_trader_info()
    account_id = trader_info['accounts'][0]
    print(f"✓ Account: {account_id}\n")
    
    symbol = "XCME:ES.Z25"
    
    # Test variations
    variations = [
        {
            "name": "Variation 1: stopLossPrice + takeProfitPrice",
            "order": {
                "accountId": account_id,
                "exchSym": symbol,
                "side": "BUY",
                "orderType": "LIMIT",
                "quantity": 1,
                "limitPrice": 6790.0,
                "stopLossPrice": 6760.0,
                "takeProfitPrice": 6880.0,
                "duration": "DAY"
            }
        },
        {
            "name": "Variation 2: stopLoss + takeProfit (no Price suffix)",
            "order": {
                "accountId": account_id,
                "exchSym": symbol,
                "side": "BUY",
                "orderType": "LIMIT",
                "quantity": 1,
                "limitPrice": 6790.0,
                "stopLoss": 6760.0,
                "takeProfit": 6880.0,
                "duration": "DAY"
            }
        },
        {
            "name": "Variation 3: Basic order (no SL/TP)",
            "order": {
                "accountId": account_id,
                "exchSym": symbol,
                "side": "BUY",
                "orderType": "LIMIT",
                "quantity": 1,
                "limitPrice": 6790.0,
                "duration": "DAY"
            }
        },
        {
            "name": "Variation 4: GTC duration with stopLossPrice",
            "order": {
                "accountId": account_id,
                "exchSym": symbol,
                "side": "BUY",
                "orderType": "LIMIT",
                "quantity": 1,
                "limitPrice": 6790.0,
                "stopLossPrice": 6760.0,
                "duration": "GTC"
            }
        }
    ]
    
    placed_orders = []
    
    for var in variations:
        print("\n" + "="*70)
        print(var["name"])
        print("="*70)
        print("Order payload:")
        print(json.dumps(var["order"], indent=2))
        print()
        
        try:
            response = client.place_order(account_id, var["order"])
            print("✅ SUCCESS!")
            print("Response:")
            print(json.dumps(response, indent=2))
            
            if 'orderId' in response:
                placed_orders.append(response['orderId'])
                
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    # Cleanup: Cancel all test orders
    if placed_orders:
        print("\n" + "="*70)
        print(f"CLEANUP: Cancelling {len(placed_orders)} test orders")
        print("="*70)
        
        for order_id in placed_orders:
            try:
                client.cancel_order(account_id, order_id)
                print(f"✓ Cancelled {order_id}")
            except Exception as e:
                print(f"✗ Failed to cancel {order_id}: {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_bracket_variations()
