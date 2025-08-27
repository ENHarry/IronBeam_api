from pydantic import BaseModel, Field
from typing import List, Optional

class Token(BaseModel):
    token: str
    status: str
    message: str

class TraderInfo(BaseModel):
    status: str
    message: str
    accounts: List[str]
    is_live: bool = Field(..., alias='isLive')
    trader_id: str = Field(..., alias='traderId')

class AccountBalance(BaseModel):
    account_id: str = Field(..., alias='accountId')
    currency_code: str = Field(..., alias='currencyCode')
    cash_balance: float = Field(..., alias='cashBalance')
    # Add other fields as needed
