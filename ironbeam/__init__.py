"""
IronBeam Python SDK

A comprehensive Python SDK for the IronBeam API with automated trade management.
"""

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
    # Models
    Token,
    TraderInfo,
    UserInfo,
    Balance,
    AccountBalance,
    Position,
    AccountPositions,
    Risk,
    AccountRisk,
    Fill,
    AccountFills,
    OrderRequest,
    OrderUpdateRequest,
    Order,
    OrderResponse,
    OrdersResponse,
    OrdersFillsResponse,
    CancelMultipleRequest,
    Quote,
    QuotesResponse,
    Depth,
    DepthResponse,
    Trade,
    TradesResponse,
    SecurityDefinition,
    SecurityDefinitionsResponse,
    Symbol,
    SymbolsResponse,
    ExchangeSource,
    ExchangeSourcesResponse,
    Complex,
    ComplexesResponse,
    SimulatedTraderRequest,
    SimulatedAccountRequest,
    SimulatedAccountResponse,
    StreamResponse,
    SubscriptionRequest,
    IndicatorSubscriptionRequest
)
from .exceptions import APIError, AuthenticationError, InvalidRequestError

__version__ = "0.1.0"

__all__ = [
    # Client
    "IronBeam",
    # Streaming
    "IronBeamStream",
    "ConnectionState",
    # Trade Management
    "AutoBreakevenManager",
    "RunningTPManager",
    "AutoBreakevenConfig",
    "RunningTPConfig",
    "PositionState",
    "BreakevenState",
    # Execution
    "ThreadedExecutor",
    "AsyncExecutor",
    # Enums
    "OrderSide",
    "OrderType",
    "DurationType",
    "OrderStatus",
    "PositionSide",
    "BalanceType",
    # Models
    "Token",
    "TraderInfo",
    "UserInfo",
    "Balance",
    "AccountBalance",
    "Position",
    "AccountPositions",
    "Risk",
    "AccountRisk",
    "Fill",
    "AccountFills",
    "OrderRequest",
    "OrderUpdateRequest",
    "Order",
    "OrderResponse",
    "OrdersResponse",
    "OrdersFillsResponse",
    "CancelMultipleRequest",
    "Quote",
    "QuotesResponse",
    "Depth",
    "DepthResponse",
    "Trade",
    "TradesResponse",
    "SecurityDefinition",
    "SecurityDefinitionsResponse",
    "Symbol",
    "SymbolsResponse",
    "ExchangeSource",
    "ExchangeSourcesResponse",
    "Complex",
    "ComplexesResponse",
    "SimulatedTraderRequest",
    "SimulatedAccountRequest",
    "SimulatedAccountResponse",
    "StreamResponse",
    "SubscriptionRequest",
    "IndicatorSubscriptionRequest",
    # Exceptions
    "APIError",
    "AuthenticationError",
    "InvalidRequestError",
]
