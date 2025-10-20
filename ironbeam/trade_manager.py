"""
Trade Management Module for IronBeam API

Provides automated trade and risk management functions:
- Auto Breakeven: Moves stop loss up to 3 times based on profit levels
- Running Take Profit: Dynamically adjusts take profit based on market conditions
"""

import logging
from typing import Optional, List, Literal, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from .models import OrderSide, Position

logger = logging.getLogger(__name__)


# ==================== Configuration Models ====================

@dataclass
class AutoBreakevenConfig:
    """Configuration for auto breakeven stop loss management.

    Example for LONG at 5000:
        trigger_levels = [20, 40, 60]  # Move SL when price hits these
        sl_offsets = [10, 30, 50]      # Move SL to entry + these offsets

        Move 1: Price @ 5020 → SL to 5010
        Move 2: Price @ 5040 → SL to 5030
        Move 3: Price @ 5060 → SL to 5050
    """
    # Trigger mode: "ticks" or "percentage"
    trigger_mode: Literal["ticks", "percentage"] = "ticks"

    # Trigger levels (when to move SL)
    # For ticks: [20, 40, 60] means move at entry+20, entry+40, entry+60
    # For percentage: [2, 4, 6] means move at +2%, +4%, +6% profit
    trigger_levels: List[float] = field(default_factory=lambda: [20, 40, 60])

    # Stop loss offsets (where to place SL after trigger)
    # [10, 30, 50] means move SL to entry+10, entry+30, entry+50
    sl_offsets: List[float] = field(default_factory=lambda: [10, 30, 50])

    # Enable/disable
    enabled: bool = True

    def __post_init__(self):
        if len(self.trigger_levels) != len(self.sl_offsets):
            raise ValueError("trigger_levels and sl_offsets must have same length")
        if len(self.trigger_levels) > 3:
            raise ValueError("Maximum 3 trigger levels allowed")


@dataclass
class RunningTPConfig:
    """Configuration for running take profit management.

    Supports multiple strategies that can run simultaneously:
    1. Trailing extremes: Trail highest high (LONG) / lowest low (SHORT)
    2. Profit level triggers: Move TP at specific profit milestones
    3. Multiple adjustment modes:
       - Mode A: Extend TP by X ticks each trigger
       - Mode B: Set TP to current price + X ticks (trailing)
       - Mode C: Move to next resistance/support level
    """
    # Trigger conditions (can enable both)
    enable_trailing_extremes: bool = True
    enable_profit_levels: bool = False

    # Profit level triggers (in ticks or %)
    profit_level_triggers: List[float] = field(default_factory=lambda: [30, 60, 90])
    profit_trigger_mode: Literal["ticks", "percentage"] = "ticks"

    # TP Adjustment Modes (can use multiple simultaneously)

    # Mode A: Extend TP by fixed ticks on each trigger
    extend_by_ticks: Optional[float] = None  # e.g., 20 ticks

    # Mode B: Trail current price + offset
    trail_offset_ticks: Optional[float] = None  # e.g., 50 ticks from current

    # Mode C: Move to resistance/support levels
    resistance_support_levels: Optional[List[float]] = None  # Price levels

    # Trailing extremes settings
    trailing_lookback_ticks: int = 10  # How far price must retrace before updating

    # Enable/disable
    enabled: bool = True

    def __post_init__(self):
        # At least one adjustment mode must be specified
        if not any([self.extend_by_ticks, self.trail_offset_ticks, self.resistance_support_levels]):
            raise ValueError("At least one TP adjustment mode must be specified")


# ==================== Position State Tracking ====================

class BreakevenState(Enum):
    """State tracking for auto breakeven."""
    NOT_STARTED = "NOT_STARTED"
    MOVE_1_PENDING = "MOVE_1_PENDING"
    MOVE_1_DONE = "MOVE_1_DONE"
    MOVE_2_PENDING = "MOVE_2_PENDING"
    MOVE_2_DONE = "MOVE_2_DONE"
    MOVE_3_PENDING = "MOVE_3_PENDING"
    MOVE_3_DONE = "MOVE_3_DONE"
    COMPLETED = "COMPLETED"


@dataclass
class PositionState:
    """Tracks state for a managed position."""
    order_id: str
    account_id: str
    symbol: str
    side: OrderSide
    entry_price: float
    quantity: int

    # Breakeven state
    breakeven_state: BreakevenState = BreakevenState.NOT_STARTED
    breakeven_moves_completed: int = 0
    current_stop_loss: Optional[float] = None

    # Running TP state
    current_take_profit: Optional[float] = None
    tp_moves_completed: int = 0
    highest_price: Optional[float] = None  # For trailing
    lowest_price: Optional[float] = None   # For trailing
    tp_profit_levels_triggered: List[int] = field(default_factory=list)

    def update_price_extremes(self, current_price: float):
        """Update highest/lowest price for trailing."""
        if self.highest_price is None or current_price > self.highest_price:
            self.highest_price = current_price
        if self.lowest_price is None or current_price < self.lowest_price:
            self.lowest_price = current_price


# ==================== Auto Breakeven Manager ====================

class AutoBreakevenManager:
    """Manages automated breakeven stop loss adjustments.

    Monitors positions and automatically moves stop loss up to 3 times
    based on configured trigger levels and offsets.
    """

    def __init__(self, client, account_id: str):
        """Initialize the breakeven manager.

        Args:
            client: IronBeam client instance
            account_id: Account ID to manage
        """
        self.client = client
        self.account_id = account_id
        self.managed_positions: Dict[str, tuple[PositionState, AutoBreakevenConfig]] = {}

    def start_monitoring(self, order_id: str, position: PositionState, config: AutoBreakevenConfig):
        """Start monitoring a position for auto breakeven.

        Args:
            order_id: Order ID to monitor
            position: Position state
            config: Breakeven configuration
        """
        if not config.enabled:
            logger.warning(f"Auto breakeven disabled for {order_id}")
            return

        self.managed_positions[order_id] = (position, config)
        logger.info(f"Started auto breakeven monitoring for {order_id}")

    def stop_monitoring(self, order_id: str):
        """Stop monitoring a position.

        Args:
            order_id: Order ID to stop monitoring
        """
        if order_id in self.managed_positions:
            del self.managed_positions[order_id]
            logger.info(f"Stopped auto breakeven monitoring for {order_id}")

    def check_and_update(self, order_id: str, current_price: float) -> bool:
        """Check if breakeven should trigger and update stop loss.

        Args:
            order_id: Order ID to check
            current_price: Current market price

        Returns:
            True if stop loss was updated, False otherwise
        """
        if order_id not in self.managed_positions:
            return False

        position, config = self.managed_positions[order_id]

        # Calculate profit in ticks or percentage
        if position.side == OrderSide.BUY:
            profit_ticks = current_price - position.entry_price
        else:
            profit_ticks = position.entry_price - current_price

        if config.trigger_mode == "percentage":
            profit_pct = (profit_ticks / position.entry_price) * 100
            profit_value = profit_pct
        else:
            profit_value = profit_ticks

        # Check which level should trigger
        move_index = position.breakeven_moves_completed

        if move_index >= len(config.trigger_levels):
            # All moves completed
            position.breakeven_state = BreakevenState.COMPLETED
            return False

        trigger_level = config.trigger_levels[move_index]

        # Check if trigger level reached
        if profit_value >= trigger_level:
            # Calculate new stop loss
            sl_offset = config.sl_offsets[move_index]

            if position.side == OrderSide.BUY:
                new_stop_loss = position.entry_price + sl_offset
            else:
                new_stop_loss = position.entry_price - sl_offset

            # Update stop loss via API
            try:
                update_request = {
                    "orderId": order_id,
                    "quantity": position.quantity,
                    "stopLoss": new_stop_loss
                }

                response = self.client.update_order(
                    self.account_id,
                    order_id,
                    update_request
                )

                # Update state
                position.current_stop_loss = new_stop_loss
                position.breakeven_moves_completed += 1

                logger.info(
                    f"Auto breakeven move {move_index + 1} executed for {order_id}: "
                    f"SL moved to {new_stop_loss} (trigger: {trigger_level}, offset: {sl_offset})"
                )

                return True

            except Exception as e:
                logger.error(f"Failed to update stop loss for {order_id}: {e}")
                return False

        return False


# ==================== Running Take Profit Manager ====================

class RunningTPManager:
    """Manages automated take profit adjustments.

    Supports multiple strategies:
    - Trailing highest high (LONG) / lowest low (SHORT)
    - Profit level triggers
    - Multiple adjustment modes (extend, trail, resistance/support)
    """

    def __init__(self, client, account_id: str):
        """Initialize the running TP manager.

        Args:
            client: IronBeam client instance
            account_id: Account ID to manage
        """
        self.client = client
        self.account_id = account_id
        self.managed_positions: Dict[str, tuple[PositionState, RunningTPConfig]] = {}

    def start_monitoring(self, order_id: str, position: PositionState, config: RunningTPConfig):
        """Start monitoring a position for running TP.

        Args:
            order_id: Order ID to monitor
            position: Position state
            config: Running TP configuration
        """
        if not config.enabled:
            logger.warning(f"Running TP disabled for {order_id}")
            return

        self.managed_positions[order_id] = (position, config)
        logger.info(f"Started running TP monitoring for {order_id}")

    def stop_monitoring(self, order_id: str):
        """Stop monitoring a position.

        Args:
            order_id: Order ID to stop monitoring
        """
        if order_id in self.managed_positions:
            del self.managed_positions[order_id]
            logger.info(f"Stopped running TP monitoring for {order_id}")

    def check_and_update(self, order_id: str, current_price: float) -> bool:
        """Check if TP should be adjusted and update.

        Args:
            order_id: Order ID to check
            current_price: Current market price

        Returns:
            True if TP was updated, False otherwise
        """
        if order_id not in self.managed_positions:
            return False

        position, config = self.managed_positions[order_id]
        position.update_price_extremes(current_price)

        should_update = False
        new_tp = None

        # Check trailing extremes trigger
        if config.enable_trailing_extremes:
            tp_from_trailing = self._calculate_trailing_tp(position, current_price, config)
            if tp_from_trailing and (not new_tp or self._is_better_tp(tp_from_trailing, new_tp, position.side)):
                new_tp = tp_from_trailing
                should_update = True

        # Check profit level triggers
        if config.enable_profit_levels:
            tp_from_profit_levels = self._check_profit_level_trigger(position, current_price, config)
            if tp_from_profit_levels and (not new_tp or self._is_better_tp(tp_from_profit_levels, new_tp, position.side)):
                new_tp = tp_from_profit_levels
                should_update = True

        # Update TP if triggered
        if should_update and new_tp:
            return self._update_take_profit(order_id, position, new_tp)

        return False

    def _calculate_trailing_tp(self, position: PositionState, current_price: float, config: RunningTPConfig) -> Optional[float]:
        """Calculate TP based on trailing highest/lowest."""
        if position.side == OrderSide.BUY:
            # LONG: Trail highest high
            if position.highest_price is None:
                return None

            # Apply adjustment modes
            new_tp = None

            if config.extend_by_ticks:
                # Mode A: Extend from current TP
                if position.current_take_profit:
                    new_tp = position.current_take_profit + config.extend_by_ticks

            if config.trail_offset_ticks:
                # Mode B: Trail current price
                tp_from_trail = current_price + config.trail_offset_ticks
                if not new_tp or tp_from_trail > new_tp:
                    new_tp = tp_from_trail

            if config.resistance_support_levels:
                # Mode C: Next resistance level
                tp_from_levels = self._get_next_level(position.highest_price, config.resistance_support_levels, higher=True)
                if tp_from_levels and (not new_tp or tp_from_levels > new_tp):
                    new_tp = tp_from_levels

            return new_tp

        else:
            # SHORT: Trail lowest low
            if position.lowest_price is None:
                return None

            new_tp = None

            if config.extend_by_ticks:
                if position.current_take_profit:
                    new_tp = position.current_take_profit - config.extend_by_ticks

            if config.trail_offset_ticks:
                tp_from_trail = current_price - config.trail_offset_ticks
                if not new_tp or tp_from_trail < new_tp:
                    new_tp = tp_from_trail

            if config.resistance_support_levels:
                tp_from_levels = self._get_next_level(position.lowest_price, config.resistance_support_levels, higher=False)
                if tp_from_levels and (not new_tp or tp_from_levels < new_tp):
                    new_tp = tp_from_levels

            return new_tp

    def _check_profit_level_trigger(self, position: PositionState, current_price: float, config: RunningTPConfig) -> Optional[float]:
        """Check if profit level triggers should activate."""
        # Calculate current profit
        if position.side == OrderSide.BUY:
            profit_ticks = current_price - position.entry_price
        else:
            profit_ticks = position.entry_price - current_price

        if config.profit_trigger_mode == "percentage":
            profit_value = (profit_ticks / position.entry_price) * 100
        else:
            profit_value = profit_ticks

        # Check which profit levels are triggered
        for i, level in enumerate(config.profit_level_triggers):
            if profit_value >= level and i not in position.tp_profit_levels_triggered:
                # New profit level triggered
                position.tp_profit_levels_triggered.append(i)

                # Calculate new TP using adjustment modes
                new_tp = None

                if config.extend_by_ticks and position.current_take_profit:
                    new_tp = position.current_take_profit + config.extend_by_ticks

                if config.trail_offset_ticks:
                    tp_from_trail = current_price + (config.trail_offset_ticks if position.side == OrderSide.BUY else -config.trail_offset_ticks)
                    if not new_tp or self._is_better_tp(tp_from_trail, new_tp, position.side):
                        new_tp = tp_from_trail

                return new_tp

        return None

    def _get_next_level(self, current_price: float, levels: List[float], higher: bool) -> Optional[float]:
        """Get next resistance (higher=True) or support (higher=False) level."""
        if higher:
            next_levels = [l for l in levels if l > current_price]
            return min(next_levels) if next_levels else None
        else:
            next_levels = [l for l in levels if l < current_price]
            return max(next_levels) if next_levels else None

    def _is_better_tp(self, new_tp: float, current_tp: float, side: OrderSide) -> bool:
        """Check if new TP is better than current TP."""
        if side == OrderSide.BUY:
            return new_tp > current_tp
        else:
            return new_tp < current_tp

    def _update_take_profit(self, order_id: str, position: PositionState, new_tp: float) -> bool:
        """Update take profit via API."""
        try:
            update_request = {
                "orderId": order_id,
                "quantity": position.quantity,
                "takeProfit": new_tp
            }

            response = self.client.update_order(
                self.account_id,
                order_id,
                update_request
            )

            old_tp = position.current_take_profit
            position.current_take_profit = new_tp
            position.tp_moves_completed += 1

            logger.info(
                f"Running TP updated for {order_id}: {old_tp} → {new_tp} "
                f"(move #{position.tp_moves_completed})"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to update take profit for {order_id}: {e}")
            return False
