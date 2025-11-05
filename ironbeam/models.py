from binascii import Error
from pydantic import BaseModel, Field, field_validator, AliasChoices
from typing import List, Optional, Union, Literal
from enum import Enum
import re

# ==================== Enums ====================

class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"
    INVALID = "INVALID"

class OrderType(str, Enum):
    """Order type enumeration.

    Note: API returns text strings in responses but MAY accept both formats in requests.
    """
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class DurationType(str, Enum):
    """Duration type enumeration.

    Note: API returns text strings in responses.
    """
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"

class OrderStatus(str, Enum):
    """Order status enumeration - complete list per OpenAPI spec."""
    PENDING = "PENDING"
    WORKING = "WORKING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ANY = "ANY"
    # Additional statuses from OpenAPI spec
    SUBMITTED = "SUBMITTED"
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    DONE_FOR_DAY = "DONE_FOR_DAY"
    REPLACED = "REPLACED"
    PENDING_CANCEL = "PENDING_CANCEL"
    STOPPED = "STOPPED"
    SUSPENDED = "SUSPENDED"
    PENDING_NEW = "PENDING_NEW"
    CALCULATED = "CALCULATED"
    ACCEPTED_FOR_BIDDING = "ACCEPTED_FOR_BIDDING"
    PENDING_REPLACE = "PENDING_REPLACE"
    CANCEL_REJECTED = "CANCEL_REJECTED"
    ORDER_NOT_FOUND = "ORDER_NOT_FOUND"
    QUEUED_NEW = "QUEUED_NEW"
    QUEUED_CANCEL = "QUEUED_CANCEL"
    COMPLETE = "COMPLETE"
    INVALID = "INVALID"

class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class BalanceType(str, Enum):
    """Balance type enumeration - per OpenAPI spec."""
    CURRENT_OPEN = "CURRENT_OPEN"
    START_OF_DAY = "START_OF_DAY"

# ==================== Authentication Models ====================

class Token(BaseModel):
    token: str
    status: str
    message: str

# ==================== Trader/Account Models ====================

class TraderInfo(BaseModel):
    status: str
    message: str
    accounts: List[str]
    is_live: bool = Field(..., alias='isLive')
    trader_id: str = Field(..., alias='traderId')

    class Config:
        populate_by_name = True

class UserInfo(BaseModel):
    status: str
    message: str
    user_id: str = Field(..., alias='userId')
    email: Optional[str] = None
    first_name: Optional[str] = Field(None, alias='firstName')
    last_name: Optional[str] = Field(None, alias='lastName')

    class Config:
        populate_by_name = True

class MarginInfo(BaseModel):
    """Margin information nested in Balance."""
    margin_requirement: Optional[float] = Field(None, alias='marginRequirement')
    buying_power: Optional[float] = Field(None, alias='buyingPower')

    class Config:
        populate_by_name = True

class Balance(BaseModel):
    """Balance model - per OpenAPI spec with all fields."""
    account_id: Optional[str] = Field(None, alias='accountId')
    currency_code: str = Field(..., alias='currencyCode')
    cash_balance: float = Field(..., alias='cashBalance')
    cash_balance_available: Optional[float] = Field(None, alias='cashBalanceAvailable')
    open_trade_equity: float = Field(..., alias='openTradeEquity')
    total_equity: Optional[float] = Field(None, alias='totalEquity')
    unrealized_pl: Optional[float] = Field(None, alias='unrealizedPL')
    net_liquidity: Optional[float] = Field(None, alias='netLiquidity')
    net_liquidity_available: Optional[float] = Field(None, alias='netLiquidityAvailable')
    cash_added_today: Optional[float] = Field(None, alias='cashAddedToday')
    days_on_call: Optional[int] = Field(None, alias='daysOnCall')
    balance_type: Optional[BalanceType] = Field(None, alias='balanceType')
    margin_info: Optional[MarginInfo] = Field(None, alias='marginInfo')
    # Legacy fields for backward compatibility
    margin_balance: Optional[float] = Field(None, alias='marginBalance')
    available_for_trading: Optional[float] = Field(None, alias='availableForTrading')

    class Config:
        populate_by_name = True

class AccountBalance(BaseModel):
    account_id: Optional[str] = Field(None, alias='accountId')
    status: str
    message: str
    balances: List[Balance]

    class Config:
        populate_by_name = True

class Position(BaseModel):
    account_id: str = Field(..., validation_alias=AliasChoices('accountId', 'account_id'))
    exch_sym: str = Field(..., validation_alias=AliasChoices('exchSym', 'exch_sym'))
    position_id: Optional[str] = Field(None, validation_alias=AliasChoices('positionId', 'position_id'))
    quantity: int
    price: float
    side: PositionSide
    unrealized_pl: Optional[float] = Field(None, validation_alias=AliasChoices('unrealizedPL', 'unrealized_pl'))
    date_opened: Optional[str] = Field(None, validation_alias=AliasChoices('dateOpened', 'date_opened'))
    currency_code: Optional[str] = Field(None, validation_alias=AliasChoices('currencyCode', 'currency_code'))

    @field_validator('exch_sym')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z0-9]{1,10}:[A-Z0-9.]{1,20}$', v):
            raise ValueError('Symbol must be in format EXCHANGE:SYMBOL')
        return v

    class Config:
        populate_by_name = True

class AccountPositions(BaseModel):
    status: str
    message: str
    positions: List[Position]

class Risk(BaseModel):
    account_id: str = Field(..., alias='accountId')
    margin_requirement: Optional[float] = Field(None, alias='marginRequirement')
    buying_power: Optional[float] = Field(None, alias='buyingPower')
    reg_code: Optional[str] = Field(None, alias='regCode')
    currency_code: Optional[str] = Field(None, alias='currencyCode')
    liquidation_value: Optional[float] = Field(None, alias='liquidationValue')

    class Config:
        populate_by_name = True

class AccountRisk(BaseModel):
    status: str
    message: str
    risks: List[Risk]  # API returns array, not single object
    risk: Optional[Risk] = None  # For backward compatibility

    def __init__(self, **data):
        super().__init__(**data)
        # Set single risk from array for convenience
        if self.risks and not self.risk:
            object.__setattr__(self, 'risk', self.risks[0])

class Fill(BaseModel):
    """Order fill model - matches actual API responses."""
    fill_id: Optional[str] = Field(None, validation_alias=AliasChoices('fillId', 'fill_id'))
    order_id: str = Field(..., validation_alias=AliasChoices('orderId', 'order_id'))
    strategy_id: Optional[Union[str, int]] = Field(None, validation_alias=AliasChoices('strategyId', 'strategy_id'))  # API returns int!
    account_id: Optional[str] = Field(None, validation_alias=AliasChoices('accountId', 'account_id'))
    exch_sym: str = Field(..., validation_alias=AliasChoices('exchSym', 'exch_sym'))
    side: OrderSide
    status: Optional[OrderStatus] = None
    quantity: int
    fill_quantity: Optional[float] = Field(None, validation_alias=AliasChoices('fillQuantity', 'fill_quantity'))
    fill_total_quantity: Optional[float] = Field(None, validation_alias=AliasChoices('fillTotalQuantity', 'fill_total_quantity'))
    price: Optional[float] = None
    fill_price: Optional[float] = Field(None, validation_alias=AliasChoices('fillPrice', 'fill_price'))
    avg_fill_price: Optional[float] = Field(None, validation_alias=AliasChoices('avgFillPrice', 'avg_fill_price'))
    fill_time: Optional[str] = Field(None, validation_alias=AliasChoices('fillTime', 'fill_time'))
    fill_date: Optional[str] = Field(None, validation_alias=AliasChoices('fillDate', 'fill_date'))
    time_order_event: Optional[Union[str, int]] = Field(None, validation_alias=AliasChoices('timeOrderEvent', 'time_order_event'))  # API returns int!
    order_update_id: Optional[Union[str, int]] = Field(None, validation_alias=AliasChoices('orderUpdateId', 'order_update_id'))  # API returns int!

    class Config:
        populate_by_name = True

class AccountFills(BaseModel):
    status: str
    message: str
    fills: List[Fill]

# ==================== Order Models ====================

class OrderRequest(BaseModel):
    """Order placement request - per OpenAPI spec."""
    account_id: str = Field(..., alias='accountId')
    exch_sym: str = Field(..., alias='exchSym')
    side: OrderSide
    quantity: int
    order_type: OrderType = Field(..., alias='orderType')
    duration: DurationType
    limit_price: Optional[float] = Field(None, alias='limitPrice')
    stop_price: Optional[float] = Field(None, alias='stopPrice')
    stop_loss: Optional[float] = Field(None, alias='stopLoss')
    take_profit: Optional[float] = Field(None, alias='takeProfit')
    stop_loss_offset: Optional[float] = Field(None, alias='stopLossOffset')
    take_profit_offset: Optional[float] = Field(None, alias='takeProfitOffset')
    trailing_stop: Optional[float] = Field(None, alias='trailingStop')
    wait_for_order_id: bool = Field(True, alias='waitForOrderId')

    @field_validator('account_id')
    def validate_account_id(cls, v):
        if not re.match(r'^[0-9]{5,10}$', v):
            raise ValueError('Account ID must be 5-10 digits')
        return v

    @field_validator('exch_sym')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z0-9]{1,10}:[A-Z0-9.]{1,20}$', v):
            raise ValueError('Symbol must be in format EXCHANGE:SYMBOL')
        return v

    class Config:
        populate_by_name = True
        use_enum_values = True

class OrderUpdateRequest(BaseModel):
    """Order update request - per OpenAPI spec."""
    order_id: str = Field(..., alias='orderId')
    quantity: Optional[float] = None  # Optional per actual OpenAPI spec, changed to float
    limit_price: Optional[float] = Field(None, alias='limitPrice')
    stop_price: Optional[float] = Field(None, alias='stopPrice')  # For STOP/STOP_LIMIT order updates
    stop_loss: Optional[float] = Field(None, alias='stopLoss')  # For bracket SL updates
    take_profit: Optional[float] = Field(None, alias='takeProfit')  # For bracket TP updates
    stop_loss_offset: Optional[float] = Field(None, alias='stopLossOffset')
    take_profit_offset: Optional[float] = Field(None, alias='takeProfitOffset')
    trailing_stop: Optional[float] = Field(None, alias='trailingStop')

    class Config:
        populate_by_name = True

class OrderError(BaseModel):
    """Order error information."""
    error_code: Optional[str] = Field(None, alias='errorCode')
    error_text: Optional[str] = Field(None, alias='errorText')

    class Config:
        populate_by_name = True

class OrderStatusResponse(BaseModel):
    message: Optional[str] = None
    order_id: str = Field("", alias='orderId')
    strategy_id: Optional[Union[str, int]] = Field(None, alias='strategyId')
    parent_order_id: Optional[Union[str, int]] = Field(None, alias='parentOrderId')
    account_id: str = Field(..., alias='accountId')
    exch_sym: str = Field(..., alias='exchSym')
    status: str
    side: str
    quantity: float
    limit_price: Optional[float] = Field(None, alias='limitPrice')
    stop_price: Optional[float] = Field(None, alias='stopPrice')
    order_type: str = Field(..., alias='orderType')
    duration: str
    fill_quantity: Optional[float] = Field(None, alias='fillQuantity')
    fill_price: Optional[float] = Field(None, alias='fillPrice')
    fill_date: Optional[str] = Field(None, alias='fillDate')
    child_orders: Optional[List[str]] = Field(None, alias='childOrders')
    order_error: Optional[OrderError] = Field(None, alias='orderError')
    error_code: Optional[int] = Field(None, alias='errorCode')
    error_text: Optional[str] = Field(None, alias='errorText')
  
    class Config:
        populate_by_name = True


class Order(BaseModel):
    """Order model - matches actual API responses."""
    order_id: str = Field(..., validation_alias=AliasChoices('orderId', 'order_id'))
    account_id: str = Field(..., validation_alias=AliasChoices('accountId', 'account_id'))
    exch_sym: str = Field(..., validation_alias=AliasChoices('exchSym', 'exch_sym'))
    side: OrderSide
    quantity: float  # Changed from int to float
    order_type: OrderType = Field(..., validation_alias=AliasChoices('orderType', 'order_type'))
    status: OrderStatus
    duration: DurationType
    strategy_id: Optional[Union[str, int]] = Field(None, validation_alias=AliasChoices('strategyId', 'strategy_id'))  # API returns int!
    parent_order_id: Optional[Union[str, int]] = Field(None, validation_alias=AliasChoices('parentOrderId', 'parent_order_id'))
    child_orders: Optional[List[Union[str, int]]] = Field(None, validation_alias=AliasChoices('childOrders', 'child_orders'))
    limit_price: Optional[float] = Field(None, validation_alias=AliasChoices('limitPrice', 'limit_price'))
    stop_price: Optional[float] = Field(None, validation_alias=AliasChoices('stopPrice', 'stop_price'))
    filled_quantity: Optional[float] = Field(None, validation_alias=AliasChoices('filledQuantity', 'filled_quantity'))  # Changed to float
    fill_quantity: Optional[float] = Field(None, validation_alias=AliasChoices('fillQuantity', 'fill_quantity'))  # Alternative name per OpenAPI
    average_fill_price: Optional[float] = Field(None, validation_alias=AliasChoices('averageFillPrice', 'average_fill_price'))
    fill_price: Optional[float] = Field(None, validation_alias=AliasChoices('fillPrice', 'fill_price'))  # Alternative name per OpenAPI
    fill_date: Optional[str] = Field(None, validation_alias=AliasChoices('fillDate', 'fill_date'))
    time_submitted: Optional[str] = Field(None, validation_alias=AliasChoices('timeSubmitted', 'time_submitted'))
    order_error: Optional[OrderError] = Field(None, validation_alias=AliasChoices('orderError', 'order_error'))

    class Config:
        populate_by_name = True

class OrderResponse(BaseModel):
    status: str
    message: str
    order_id: Optional[str] = Field(None, validation_alias=AliasChoices('orderId', 'order_id'))
    strategy_id: Optional[Union[str, int]] = Field(None, validation_alias=AliasChoices('strategyId', 'strategy_id'))  # API returns int!

    class Config:
        populate_by_name = True

class OrdersResponse(BaseModel):
    status: str
    message: str
    orders: List[Order]

class OrdersFillsResponse(BaseModel):
    status: str
    message: str
    fills: List[Fill]

class CancelMultipleRequest(BaseModel):
    order_ids: List[str] = Field(..., alias='orderIds')

    class Config:
        populate_by_name = True

# ==================== Market Data Models ====================

class Quote(BaseModel):
    exch_sym: str = Field(..., validation_alias=AliasChoices('exchSym', 's'))
    bid_price: Optional[float] = Field(None, validation_alias=AliasChoices('bidPrice', 'b'))
    ask_price: Optional[float] = Field(None, validation_alias=AliasChoices('askPrice', 'a'))
    bid_size: Optional[int] = Field(None, validation_alias=AliasChoices('bidSize', 'bs'))
    ask_size: Optional[int] = Field(None, validation_alias=AliasChoices('askSize', 'as'))
    last_price: Optional[float] = Field(None, validation_alias=AliasChoices('lastPrice', 'l'))
    last_size: Optional[int] = Field(None, validation_alias=AliasChoices('lastSize', 'ls'))
    timestamp: Optional[str] = Field(None, validation_alias=AliasChoices('timestamp', 't'))

    class Config:
        populate_by_name = True

class QuotesResponse(BaseModel):
    status: Optional[str] = None
    message: Optional[str] = None
    quotes: List[Quote] = Field(default_factory=list)

    class Config:
        populate_by_name = True

class DepthLevel(BaseModel):
    """Market depth level per OpenAPI spec.

    Used in REST API depth responses. May contain abbreviated or full field names
    depending on the API response format.
    """
    # Core fields (using abbreviated aliases per OpenAPI spec)
    level: Optional[int] = Field(None, alias='l')  # 0-based level number
    timestamp: Optional[int] = Field(None, alias='t')  # Time in milliseconds
    side: Optional[str] = Field(None, alias='s')  # B (bid) or A (ask)
    price: float = Field(..., alias='p')  # Price at this level
    order_count: Optional[int] = Field(None, alias='o')  # Number of orders
    size: float = Field(..., alias='sz')  # Total size at this level
    implied_order_count: Optional[int] = Field(None, alias='ioc')  # Implied orders
    implied_size: Optional[float] = Field(None, alias='is')  # Implied size

    class Config:
        populate_by_name = True

class Depth(BaseModel):
    """Market depth data per OpenAPI spec.

    Depth data uses abbreviated field names per spec:
    - 's' for symbol
    - 'b' for bids array
    - 'a' for asks array
    """
    exch_sym: str = Field(..., alias='s')  # Symbol (abbreviated per OpenAPI spec)
    bids: List[DepthLevel] = Field(..., alias='b')  # Bid levels
    asks: List[DepthLevel] = Field(..., alias='a')  # Ask levels
    timestamp: Optional[str] = None

    class Config:
        populate_by_name = True  # Also accept 'exchSym', 'bids', 'asks' for compatibility

class DepthResponse(BaseModel):
    """Depth response from REST API.

    Note: OpenAPI spec shows 'Depths' (capital D) but actual API may use 'depths'.
    Using populate_by_name to accept both formats.
    """
    status: str
    message: str
    depths: List[Depth] = Field(..., alias='Depths')

    class Config:
        populate_by_name = True  # Accept both 'depths' and 'Depths'

class Trade(BaseModel):
    price: float
    size: int
    timestamp: str
    aggressor_side: Optional[str] = Field(None, alias='aggressorSide')

    class Config:
        populate_by_name = True

class TradesResponse(BaseModel):
    status: str
    message: str
    trades: List[Trade]

# ==================== Symbol Search Models ====================

class SecurityDefinition(BaseModel):
    exch_sym: str = Field(..., alias='exchSym')
    description: Optional[str] = None
    exchange: Optional[str] = None
    security_type: Optional[str] = Field(None, alias='securityType')
    currency: Optional[str] = None
    tick_size: Optional[float] = Field(None, alias='tickSize')
    point_value: Optional[float] = Field(None, alias='pointValue')

    class Config:
        populate_by_name = True

class SecurityDefinitionsResponse(BaseModel):
    status: str
    message: str
    definitions: List[SecurityDefinition]

class Symbol(BaseModel):
    exch_sym: str = Field(..., alias='exchSym')
    description: Optional[str] = None
    exchange: Optional[str] = None

    class Config:
        populate_by_name = True

class SymbolsResponse(BaseModel):
    status: str
    message: str
    symbols: List[Symbol]

class ExchangeSource(BaseModel):
    exchange: str
    name: str

class ExchangeSourcesResponse(BaseModel):
    status: str
    message: str
    exchanges: List[ExchangeSource]

class Complex(BaseModel):
    complex: str
    description: str

class ComplexesResponse(BaseModel):
    status: str
    message: str
    complexes: List[Complex]

# ==================== Simulated Account Models ====================

class SimulatedTraderRequest(BaseModel):
    """Simulated trader creation request - uses PascalCase per OpenAPI spec."""
    first_name: str = Field(..., alias='FirstName')  # PascalCase per OpenAPI!
    last_name: str = Field(..., alias='LastName')
    email: str = Field(..., alias='Email')
    password: str = Field(..., alias='Password')
    template_id: str = Field(..., alias='TemplateId')
    address1: str = Field(..., alias='Address1')
    city: str = Field(..., alias='City')
    state: str = Field(..., alias='State')
    country: str = Field(..., alias='Country')
    zip_code: str = Field(..., alias='ZipCode')
    phone: str = Field(..., alias='Phone')

    class Config:
        populate_by_name = True

class SimulatedAccountRequest(BaseModel):
    """Simulated account creation request - uses PascalCase per OpenAPI spec."""
    trader_id: str = Field(..., alias='TraderId')  # PascalCase per OpenAPI!
    password: str = Field(..., alias='Password')
    template_id: str = Field(..., alias='TemplateId')

    class Config:
        populate_by_name = True

class SimulatedAccountResponse(BaseModel):
    status: str
    message: str
    account_id: Optional[str] = Field(None, alias='accountId')
    trader_id: Optional[str] = Field(None, alias='traderId')

    class Config:
        populate_by_name = True

# ==================== Streaming Models ====================

class StreamResponse(BaseModel):
    status: str
    message: str
    stream_id: str = Field(..., alias='streamId')

    class Config:
        populate_by_name = True

class SubscriptionRequest(BaseModel):
    symbols: List[str]

class IndicatorSubscriptionRequest(BaseModel):
    exch_sym: str = Field(..., alias='exchSym')
    bar_size: int = Field(..., alias='barSize')

    class Config:
        populate_by_name = True

# ==================== Security Information Models ====================

class SecurityMargin(BaseModel):
    exch_sym: str = Field(..., alias='exchSym')
    initial_margin: Optional[float] = Field(None, alias='initialMargin')
    maintenance_margin: Optional[float] = Field(None, alias='maintenanceMargin')
    currency: Optional[str] = None
    point_value: Optional[float] = Field(None, alias='pointValue')

    class Config:
        populate_by_name = True

class SecurityMarginResponse(BaseModel):
    status: str
    message: str
    margins: List[SecurityMargin]

class SecurityStatus(BaseModel):
    exch_sym: str = Field(..., alias='exchSym')
    trading_status: Optional[str] = Field(None, alias='tradingStatus')
    halt_reason: Optional[str] = Field(None, alias='haltReason')
    is_tradable: Optional[bool] = Field(None, alias='isTradable')

    class Config:
        populate_by_name = True

class SecurityStatusResponse(BaseModel):
    status: str
    message: str
    securities: List[SecurityStatus]

# ==================== Strategy/Order ID Mapping Models ====================

class StrategyIdResponse(BaseModel):
    status: str
    message: str
    strategy_id: Optional[Union[str, int]] = Field(None, alias='strategyId')  # API returns int!

    class Config:
        populate_by_name = True

class OrderIdResponse(BaseModel):
    status: str
    message: str
    order_id: Optional[str] = Field(None, alias='orderId')
    order_ids: Optional[List[str]] = Field(None, alias='orderIds')

    class Config:
        populate_by_name = True

class StrategyIdMappingResponse(BaseModel):
    status: str
    message: str
    strategy_id: Optional[Union[str, int]] = Field(None, alias='strategyId')  # API returns int!
    mapping: Optional[dict] = None

    class Config:
        populate_by_name = True

# ==================== Batch Operations Models ====================

class CancelResult(BaseModel):
    order_id: str = Field(..., alias='orderId')
    success: bool
    message: Optional[str] = None

    class Config:
        populate_by_name = True

class CancelMultipleResponse(BaseModel):
    status: str
    message: str
    results: Optional[List[CancelResult]] = None
    cancelled_count: Optional[int] = Field(None, alias='cancelledCount')
    failed_count: Optional[int] = Field(None, alias='failedCount')

    class Config:
        populate_by_name = True

# ==================== Enhanced Streaming Models ====================

class QuoteStreamMessage(BaseModel):
    """Enhanced quote message from WebSocket stream."""
    exch_sym: str = Field(..., alias='s')
    last_price: Optional[float] = Field(None, alias='l')
    last_size: Optional[int] = Field(None, alias='sz')
    bid_price: Optional[float] = Field(None, alias='b')
    ask_price: Optional[float] = Field(None, alias='a')
    bid_size: Optional[int] = Field(None, alias='bs')
    ask_size: Optional[int] = Field(None, alias='as')
    change: Optional[float] = Field(None, alias='ch')
    open_price: Optional[float] = Field(None, alias='op')
    high_price: Optional[float] = Field(None, alias='hi')
    low_price: Optional[float] = Field(None, alias='lo')
    volume: Optional[int] = Field(None, alias='v')
    timestamp: Optional[int] = Field(None, alias='t')

    class Config:
        populate_by_name = True

class OrderBookLevel(BaseModel):
    """Individual order book level per OpenAPI spec.

    Represents a single level in the market depth (order book).
    """
    level: Optional[int] = Field(None, alias='l')  # 0-based level number
    timestamp: Optional[int] = Field(None, alias='t')  # Time in milliseconds
    side: Optional[str] = Field(None, alias='s')  # B (bid) or A (ask)
    price: float = Field(..., alias='p')  # Price at this level
    order_count: Optional[int] = Field(None, alias='o')  # Number of orders
    size: float = Field(..., alias='sz')  # Total size at this level (changed to float per spec)
    implied_order_count: Optional[int] = Field(None, alias='ioc')  # Implied orders
    implied_size: Optional[float] = Field(None, alias='is')  # Implied size

    # MBO-specific fields (optional, may not be in standard depth)
    order_id: Optional[str] = Field(None, alias='orderId')
    position: Optional[int] = None

    class Config:
        populate_by_name = True

class DepthStreamMessage(BaseModel):
    """Depth/order book message from WebSocket stream per OpenAPI spec.

    Depth messages use abbreviated field names in the stream:
    - 's' for symbol (exchSym)
    - 'b' for bids array
    - 'a' for asks array
    - 't' for timestamp
    """
    exch_sym: str = Field(..., alias='s')
    bids: List[Union[OrderBookLevel, dict]] = Field(default_factory=list, alias='b')
    asks: List[Union[OrderBookLevel, dict]] = Field(default_factory=list, alias='a')
    timestamp: Optional[int] = Field(None, alias='t')
    sequence: Optional[int] = Field(None, alias='seq')  # May not be in spec but useful

    class Config:
        populate_by_name = True

class TradeStreamMessage(BaseModel):
    """Enhanced trade message from WebSocket stream."""
    exch_sym: str = Field(..., alias='s')
    price: float = Field(..., alias='p')
    size: int = Field(..., alias='sz')
    timestamp: int = Field(..., alias='t')
    aggressor_side: Optional[str] = Field(None, alias='side')
    trade_id: Optional[str] = Field(None, alias='id')

    class Config:
        populate_by_name = True

class IndicatorBarData(BaseModel):
    """Indicator bar data (tick/trade/time/volume bars)."""
    exch_sym: str = Field(..., alias='exchSym')
    open_price: float = Field(..., alias='open')
    high_price: float = Field(..., alias='high')
    low_price: float = Field(..., alias='low')
    close_price: float = Field(..., alias='close')
    volume: Optional[int] = None
    timestamp: int = Field(..., alias='timestamp')
    bar_type: Optional[str] = Field(None, alias='barType')

    class Config:
        populate_by_name = True

class IndicatorBarResponse(BaseModel):
    status: str
    message: str
    indicator_id: str = Field(..., alias='indicatorId')
    bars: Optional[List[IndicatorBarData]] = None

    class Config:
        populate_by_name = True

# ==================== Simulated Account Cash Models ====================

class CashOperation(BaseModel):
    """Individual cash operation entry."""
    operation_id: Optional[str] = Field(None, alias='operationId')
    timestamp: Optional[str] = None
    operation_type: Optional[str] = Field(None, alias='operationType')
    amount: float
    currency: str
    description: Optional[str] = None

    class Config:
        populate_by_name = True

class CashReportResponse(BaseModel):
    status: str
    message: str
    account_id: str = Field(..., alias='accountId')
    operations: List[CashOperation]
    total_added: Optional[float] = Field(None, alias='totalAdded')
    total_removed: Optional[float] = Field(None, alias='totalRemoved')
    current_balance: Optional[float] = Field(None, alias='currentBalance')

    class Config:
        populate_by_name = True

# ==================== Request Models for Consistency ====================

class AuthenticationRequest(BaseModel):
    """Authentication request payload - per OpenAPI spec."""
    username: str
    api_key: str = Field(..., alias='apikey')  # lowercase per OpenAPI spec!
    password: Optional[str] = None

    class Config:
        populate_by_name = True

class AccountBalanceRequest(BaseModel):
    """Request for account balance."""
    account_id: str = Field(..., alias='accountId')
    balance_type: BalanceType = Field(default=BalanceType.CURRENT_OPEN, alias='balanceType')

    @field_validator('account_id')
    def validate_account_id(cls, v):
        if not re.match(r'^[0-9]{5,10}$', v):
            raise ValueError('Account ID must be 5-10 digits')
        return v

    class Config:
        populate_by_name = True
        use_enum_values = True

class QuotesRequest(BaseModel):
    """Request for market quotes."""
    symbols: List[str]

    @field_validator('symbols')
    def validate_symbols(cls, v):
        if not v:
            raise ValueError('At least one symbol required')
        for sym in v:
            if not re.match(r'^[A-Z0-9]{1,10}:[A-Z0-9.]{1,20}$', sym):
                raise ValueError(f'Invalid symbol format: {sym}')
        return v

class DepthRequest(BaseModel):
    """Request for market depth data."""
    symbols: List[str]

    @field_validator('symbols')
    def validate_symbols(cls, v):
        if not v:
            raise ValueError('At least one symbol required')
        for sym in v:
            if not re.match(r'^[A-Z0-9]{1,10}:[A-Z0-9.]{1,20}$', sym):
                raise ValueError(f'Invalid symbol format: {sym}')
        return v

class TradesRequest(BaseModel):
    """Request for historical trades."""
    symbol: str
    from_time: int = Field(..., alias='fromTime')
    to_time: int = Field(..., alias='toTime')
    max_records: int = Field(default=100, alias='maxRecords')
    earlier: bool = True

    @field_validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z0-9]{1,10}:[A-Z0-9.]{1,20}$', v):
            raise ValueError(f'Invalid symbol format: {v}')
        return v

    @field_validator('max_records')
    def validate_max_records(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('max_records must be between 1 and 1000')
        return v

    class Config:
        populate_by_name = True

class OrdersRequest(BaseModel):
    """Request for orders query."""
    account_id: str = Field(..., alias='accountId')
    order_status: OrderStatus = Field(default=OrderStatus.ANY, alias='orderStatus')

    @field_validator('account_id')
    def validate_account_id(cls, v):
        if not re.match(r'^[0-9]{5,10}$', v):
            raise ValueError('Account ID must be 5-10 digits')
        return v

    class Config:
        populate_by_name = True
        use_enum_values = True

class SecurityDefinitionsRequest(BaseModel):
    """Request for security definitions."""
    symbols: List[str]

    @field_validator('symbols')
    def validate_symbols(cls, v):
        if not v:
            raise ValueError('At least one symbol required')
        return v

class SymbolSearchRequest(BaseModel):
    """Request for symbol search."""
    text: str
    limit: int = 100
    prefer_active: bool = Field(default=True, alias='preferActive')

    @field_validator('text')
    def validate_text(cls, v):
        if len(v) < 1:
            raise ValueError('Search text cannot be empty')
        return v

    @field_validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Limit must be between 1 and 1000')
        return v

    class Config:
        populate_by_name = True

class ComplexRequest(BaseModel):
    """Request for market complexes."""
    exchange: str

    @field_validator('exchange')
    def validate_exchange(cls, v):
        if not v or len(v) < 2:
            raise ValueError('Exchange code required')
        return v.upper()

class FuturesSearchRequest(BaseModel):
    """Request for futures search."""
    exchange: str
    market_group: str = Field(..., alias='marketGroup')

    @field_validator('exchange')
    def validate_exchange(cls, v):
        if not v:
            raise ValueError('Exchange required')
        return v.upper()

    class Config:
        populate_by_name = True

class OptionsSearchRequest(BaseModel):
    """Request for options search."""
    symbol: str

    @field_validator('symbol')
    def validate_symbol(cls, v):
        if not v:
            raise ValueError('Symbol required')
        return v

class StrategyIdRequest(BaseModel):
    """Request for strategy ID lookup."""
    account_id: str = Field(..., alias='accountId')
    order_ids: List[str] = Field(..., alias='orderIds')

    @field_validator('account_id')
    def validate_account_id(cls, v):
        if not re.match(r'^[0-9]{5,10}$', v):
            raise ValueError('Account ID must be 5-10 digits')
        return v

    @field_validator('order_ids')
    def validate_order_ids(cls, v):
        if not v:
            raise ValueError('At least one order ID required')
        return v

    class Config:
        populate_by_name = True

class SimulatedAccountCashRequest(BaseModel):
    """Request for simulated account cash operations."""
    account_id: str = Field(..., alias='accountId')
    password: str
    amount: float
    currency: str = "USD"

    @field_validator('account_id')
    def validate_account_id(cls, v):
        if not re.match(r'^[0-9]{5,10}$', v):
            raise ValueError('Account ID must be 5-10 digits')
        return v

    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    class Config:
        populate_by_name = True

# ==================== Response Models for Consistency ====================

class LogoutResponse(BaseModel):
    """Response from logout operation."""
    status: str
    message: str

class CancelOrderResponse(BaseModel):
    """Response from order cancellation."""
    status: str
    message: str
    order_id: Optional[str] = Field(None, alias='orderId')

    class Config:
        populate_by_name = True

class SimulatedAccountResetResponse(BaseModel):
    """Response from simulated account reset."""
    status: str
    message: str
    account_id: Optional[str] = Field(None, alias='accountId')

    class Config:
        populate_by_name = True

class SimulatedAccountExpireResponse(BaseModel):
    """Response from simulated account expiration."""
    status: str
    message: str
    account_id: Optional[str] = Field(None, alias='accountId')

    class Config:
        populate_by_name = True

class SimulatedAccountCashResponse(BaseModel):
    """Response from simulated account cash operation."""
    status: str
    message: str
    account_id: Optional[str] = Field(None, alias='accountId')
    new_balance: Optional[float] = Field(None, alias='newBalance')

    class Config:
        populate_by_name = True

class SubscriptionResponse(BaseModel):
    """Response from market data subscription."""
    status: str
    message: str
    stream_id: Optional[str] = Field(None, alias='streamId')
    symbols: Optional[List[str]] = None

    class Config:
        populate_by_name = True

class UnsubscriptionResponse(BaseModel):
    """Response from market data unsubscription."""
    status: str
    message: str
    stream_id: Optional[str] = Field(None, alias='streamId')
    symbols: Optional[List[str]] = None

    class Config:
        populate_by_name = True

class IndicatorSubscriptionResponse(BaseModel):
    """Response from indicator subscription."""
    status: str
    message: str
    stream_id: Optional[str] = Field(None, alias='streamId')
    indicator_id: Optional[str] = Field(None, alias='indicatorId')
    exch_sym: Optional[str] = Field(None, alias='exchSym')
    bar_size: Optional[int] = Field(None, alias='barSize')

    class Config:
        populate_by_name = True

class IndicatorUnsubscriptionResponse(BaseModel):
    """Response from indicator unsubscription."""
    status: str
    message: str
    indicator_id: Optional[str] = Field(None, alias='indicatorId')

    class Config:
        populate_by_name = True

class TradableAssetsSummary(BaseModel):
    """Summary statistics for tradable assets."""
    total_assets: int = Field(..., alias='totalAssets')
    by_exchange: dict = Field(default_factory=dict, alias='byExchange')
    by_type: dict = Field(default_factory=dict, alias='byType')

    class Config:
        populate_by_name = True

class TradableAssetsResponse(BaseModel):
    """Response from get_all_tradable_assets."""
    futures: dict = Field(default_factory=dict)
    options: dict = Field(default_factory=dict)
    spreads: dict = Field(default_factory=dict)
    summary: TradableAssetsSummary

class PopularSymbolCategory(BaseModel):
    """A single popular symbol entry."""
    symbol: str
    name: str
    exchange: str

class PopularSymbolsResponse(BaseModel):
    """Response from get_popular_symbols."""
    equity_indices: List[PopularSymbolCategory] = Field(..., alias='equityIndices')
    commodities: dict
    currencies: List[PopularSymbolCategory]
    rates: List[PopularSymbolCategory]

    class Config:
        populate_by_name = True

class KeywordSearchResponse(BaseModel):
    """Response from search_symbols_by_keyword."""
    symbols: List[Symbol]
    count: int
    keyword: str
    error: Optional[str] = None

class FuturesSearchResponse(BaseModel):
    """Response from futures search."""
    symbols: List[dict]
    status: str
    message: str
    additional_properties: Optional[dict] = Field(None, alias='additionalProperties')

    class Config:
        populate_by_name = True

class OptionsSearchResponse(BaseModel):
    """Response from options search."""
    symbols: List[Symbol]
    status: str
    message: str

class OptionGroupsResponse(BaseModel):
    """Response from option groups search."""
    groups: List[dict]
    status: str
    message: str

class OptionSpreadsResponse(BaseModel):
    """Response from option spreads search."""
    spreads: List[dict]
    status: str
    message: str
