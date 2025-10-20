from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Literal
from enum import Enum
import re

# ==================== Enums ====================

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class DurationType(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"
    IMMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL"
    FILL_OR_KILL = "FILL_OR_KILL"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    WORKING = "WORKING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ANY = "ANY"

class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class BalanceType(str, Enum):
    CURRENT_OPEN = "CURRENT_OPEN"
    CURRENT_CLOSE = "CURRENT_CLOSE"
    PREVIOUS_CLOSE = "PREVIOUS_CLOSE"

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

class Balance(BaseModel):
    currency_code: str = Field(..., alias='currencyCode')
    cash_balance: float = Field(..., alias='cashBalance')
    open_trade_equity: float = Field(..., alias='openTradeEquity')
    unrealized_pl: float = Field(..., alias='unrealizedPL')
    margin_balance: float = Field(..., alias='marginBalance')
    available_for_trading: float = Field(..., alias='availableForTrading')

    class Config:
        populate_by_name = True

class AccountBalance(BaseModel):
    account_id: str = Field(..., alias='accountId')
    status: str
    message: str
    balances: List[Balance]

    class Config:
        populate_by_name = True

class Position(BaseModel):
    account_id: str = Field(..., alias='accountId')
    exch_sym: str = Field(..., alias='exchSym')
    position_id: Optional[str] = Field(None, alias='positionId')
    quantity: float
    price: float
    side: PositionSide
    unrealized_pl: Optional[float] = Field(None, alias='unrealizedPL')
    date_opened: Optional[str] = Field(None, alias='dateOpened')
    currency_code: Optional[str] = Field(None, alias='currencyCode')

    @field_validator('exch_sym')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z0-9]{1,10}:[A-Z0-9]{1,10}$', v):
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
    margin_requirement: float = Field(..., alias='marginRequirement')
    buying_power: float = Field(..., alias='buyingPower')

    class Config:
        populate_by_name = True

class AccountRisk(BaseModel):
    status: str
    message: str
    risk: Risk

class Fill(BaseModel):
    fill_id: str = Field(..., alias='fillId')
    order_id: str = Field(..., alias='orderId')
    exch_sym: str = Field(..., alias='exchSym')
    side: OrderSide
    quantity: float
    price: float
    fill_time: str = Field(..., alias='fillTime')

    class Config:
        populate_by_name = True

class AccountFills(BaseModel):
    status: str
    message: str
    fills: List[Fill]

# ==================== Order Models ====================

class OrderRequest(BaseModel):
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
        if not re.match(r'^[A-Z0-9]{1,10}:[A-Z0-9]{1,10}$', v):
            raise ValueError('Symbol must be in format EXCHANGE:SYMBOL')
        return v

    class Config:
        populate_by_name = True
        use_enum_values = True

class OrderUpdateRequest(BaseModel):
    order_id: str = Field(..., alias='orderId')
    quantity: Optional[int] = None
    limit_price: Optional[float] = Field(None, alias='limitPrice')
    stop_price: Optional[float] = Field(None, alias='stopPrice')
    stop_loss: Optional[float] = Field(None, alias='stopLoss')
    take_profit: Optional[float] = Field(None, alias='takeProfit')
    stop_loss_offset: Optional[float] = Field(None, alias='stopLossOffset')
    take_profit_offset: Optional[float] = Field(None, alias='takeProfitOffset')
    trailing_stop: Optional[float] = Field(None, alias='trailingStop')

    class Config:
        populate_by_name = True

class Order(BaseModel):
    order_id: str = Field(..., alias='orderId')
    account_id: str = Field(..., alias='accountId')
    exch_sym: str = Field(..., alias='exchSym')
    side: OrderSide
    quantity: int
    filled_quantity: Optional[int] = Field(None, alias='filledQuantity')
    order_type: OrderType = Field(..., alias='orderType')
    status: OrderStatus
    limit_price: Optional[float] = Field(None, alias='limitPrice')
    stop_price: Optional[float] = Field(None, alias='stopPrice')
    average_fill_price: Optional[float] = Field(None, alias='averageFillPrice')
    time_submitted: Optional[str] = Field(None, alias='timeSubmitted')

    class Config:
        populate_by_name = True

class OrderResponse(BaseModel):
    status: str
    message: str
    order_id: Optional[str] = Field(None, alias='orderId')
    strategy_id: Optional[str] = Field(None, alias='strategyId')

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
    exch_sym: str = Field(..., alias='exchSym')
    bid_price: Optional[float] = Field(None, alias='bidPrice')
    ask_price: Optional[float] = Field(None, alias='askPrice')
    bid_size: Optional[int] = Field(None, alias='bidSize')
    ask_size: Optional[int] = Field(None, alias='askSize')
    last_price: Optional[float] = Field(None, alias='lastPrice')
    last_size: Optional[int] = Field(None, alias='lastSize')
    timestamp: Optional[str] = None

    class Config:
        populate_by_name = True

class QuotesResponse(BaseModel):
    status: str
    message: str
    quotes: List[Quote]

class DepthLevel(BaseModel):
    price: float
    size: int

class Depth(BaseModel):
    exch_sym: str = Field(..., alias='exchSym')
    bids: List[DepthLevel]
    asks: List[DepthLevel]
    timestamp: Optional[str] = None

    class Config:
        populate_by_name = True

class DepthResponse(BaseModel):
    status: str
    message: str
    depths: List[Depth]

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
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    email: str
    password: str
    template_id: str = Field(..., alias='templateId')
    address1: str
    city: str
    state: str
    country: str
    zip_code: str = Field(..., alias='zipCode')
    phone: str

    class Config:
        populate_by_name = True

class SimulatedAccountRequest(BaseModel):
    trader_id: str = Field(..., alias='traderId')
    password: str
    template_id: str = Field(..., alias='templateId')

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
