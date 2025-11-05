"""
IronBeam Python SDK - Trading API with Automated Risk Management

QUICK START:
-----------
from ironbeam import IronBeam, AutoBreakevenManager, RunningTPManager

# 1. Connect & Authenticate
client = IronBeam(api_key="key", username="user", password="pass")
client.authenticate()

# 2. Get Market Data
quotes = client.get_quotes(["XCME:ES.Z24"])
balance = client.get_account_balance("account_id")

# 3. Place Orders
order = {"accountId": "acc", "exchSym": "XCME:ES.Z24", "side": "BUY", 
         "quantity": 1, "orderType": "MARKET", "duration": "DAY"}
client.place_order("account_id", order)

# 4. Auto Risk Management
from ironbeam import ThreadedExecutor, AutoBreakevenConfig
config = AutoBreakevenConfig(trigger_levels=[20,40,60], sl_offsets=[10,30,50])
executor = ThreadedExecutor(client, "account_id")
executor.add_auto_breakeven(order_id, position, config)

CORE MODULES:
------------
• IronBeam: REST API client (49 endpoints)
• IronBeamStream: WebSocket streaming  
• AutoBreakevenManager: Move stop-loss up automatically
• RunningTPManager: Dynamic take-profit adjustments
• ThreadedExecutor/AsyncExecutor: Strategy execution engines

MAIN FEATURES:
-------------
✓ Full API Coverage (Auth, Orders, Market Data, Streaming)
✓ Auto Breakeven (3 levels, ticks/percentage modes)  
✓ Running Take Profit (trailing, profit levels, resistance/support)
✓ Real-time WebSocket streaming with auto-reconnect
✓ Robust field compatibility (handles API format variations)
✓ Production-ready error handling & validation

For full documentation: help(ironbeam.IronBeam) or see README.md
"""

# Hide all the Pydantic model details from help() by not importing them at module level
# and using __all__ to control what's shown

from .client import IronBeam
from .streaming import IronBeamStream, ConnectionState
from .trade_manager import (
    AutoBreakevenManager,
    RunningTPManager,
    AutoBreakevenConfig,
    RunningTPConfig,
    PositionState,
    BreakevenState
)
from .execution_engine import ThreadedExecutor, AsyncExecutor
from .models import (
    # Enums
    OrderSide,
    OrderType,
    DurationType,
    OrderStatus,
    PositionSide,
    BalanceType,
    # Authentication Models
    Token,
    AuthenticationRequest,
    LogoutResponse,
    # Account Models
    TraderInfo,
    UserInfo,
    Balance,
    AccountBalance,
    AccountBalanceRequest,
    Position,
    AccountPositions,
    Risk,
    AccountRisk,
    Fill,
    AccountFills,
    # Order Models
    OrderRequest,
    OrderUpdateRequest,
    Order,
    OrderResponse,
    OrdersRequest,
    OrdersResponse,
    OrdersFillsResponse,
    CancelOrderResponse,
    CancelMultipleRequest,
    CancelMultipleResponse,
    # Market Data Models
    Quote,
    QuotesRequest,
    QuotesResponse,
    Depth,
    DepthRequest,
    DepthResponse,
    Trade,
    TradesRequest,
    TradesResponse,
    # Security Models
    SecurityDefinition,
    SecurityDefinitionsRequest,
    SecurityDefinitionsResponse,
    SecurityMarginResponse,
    SecurityStatusResponse,
    # Symbol Search Models
    Symbol,
    SymbolsResponse,
    SymbolSearchRequest,
    ExchangeSource,
    ExchangeSourcesResponse,
    Complex,
    ComplexRequest,
    ComplexesResponse,
    FuturesSearchRequest,
    OptionsSearchRequest,
    StrategyIdRequest,
    StrategyIdResponse,
    OrderIdResponse,
    StrategyIdMappingResponse,
    # Streaming Models
    StreamResponse,
    SubscriptionRequest,
    SubscriptionResponse,
    UnsubscriptionResponse,
    IndicatorSubscriptionRequest,
    IndicatorSubscriptionResponse,
    IndicatorUnsubscriptionResponse,
    QuoteStreamMessage,
    DepthStreamMessage,
    TradeStreamMessage,
    OrderBookLevel,
    IndicatorBarData,
    IndicatorBarResponse,
    # Simulated Account Models
    SimulatedTraderRequest,
    SimulatedAccountRequest,
    SimulatedAccountResponse,
    SimulatedAccountCashRequest,
    SimulatedAccountCashResponse,
    SimulatedAccountResetResponse,
    SimulatedAccountExpireResponse,
    CashOperation,
    CashReportResponse,
    # Utility Models
    TradableAssetsResponse,
    TradableAssetsSummary,
    PopularSymbolsResponse,
    PopularSymbolCategory,
    KeywordSearchResponse,
    FuturesSearchResponse,
    OptionsSearchResponse,
    OptionGroupsResponse,
    OptionSpreadsResponse,
    CancelResult,
    SecurityMargin,
    SecurityStatus,
    DepthLevel
)
from .exceptions import (
    APIError, AuthenticationError, InvalidRequestError,
    RateLimitError, ServerError, ConnectionError, TimeoutError,
    StreamingError, OrderError, PositionError
)

__version__ = "0.1.0"

__all__ = [
    # === CORE CLASSES (main functionality) ===
    "IronBeam",
    "IronBeamStream", 
    "ConnectionState",
    
    # === TRADE MANAGEMENT ===
    "AutoBreakevenManager",
    "RunningTPManager", 
    "AutoBreakevenConfig",
    "RunningTPConfig",
    "PositionState",
    "BreakevenState",
    
    # === EXECUTION ENGINES ===
    "ThreadedExecutor",
    "AsyncExecutor",
    
    # === ESSENTIAL ENUMS ===
    "OrderSide",
    "OrderType", 
    "DurationType",
    "OrderStatus",
    "PositionSide",
    
    # === EXCEPTIONS ===
    "APIError",
    "AuthenticationError", 
    "InvalidRequestError",
    "OrderError",
    "PositionError",
    
    # Models available via direct import but not cluttering help()
    # Use: from ironbeam.models import Quote, Order, etc.
]
