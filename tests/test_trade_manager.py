"""
Unit tests for trade management functionality.

Tests auto breakeven and running TP managers.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ironbeam.trade_manager import (
    AutoBreakevenManager,
    RunningTPManager,
    AutoBreakevenConfig,
    RunningTPConfig,
    PositionState,
    BreakevenState
)
from ironbeam.models import OrderSide


class TestAutoBreakevenConfig(unittest.TestCase):
    """Test auto breakeven configuration."""

    def test_valid_config(self):
        config = AutoBreakevenConfig(
            trigger_mode="ticks",
            trigger_levels=[20, 40, 60],
            sl_offsets=[10, 30, 50]
        )
        self.assertEqual(len(config.trigger_levels), 3)
        self.assertEqual(len(config.sl_offsets), 3)

    def test_mismatched_lengths(self):
        with self.assertRaises(ValueError):
            AutoBreakevenConfig(
                trigger_levels=[20, 40],
                sl_offsets=[10, 30, 50]  # Different length
            )

    def test_max_three_levels(self):
        with self.assertRaises(ValueError):
            AutoBreakevenConfig(
                trigger_levels=[10, 20, 30, 40],
                sl_offsets=[5, 15, 25, 35]
            )


class TestRunningTPConfig(unittest.TestCase):
    """Test running TP configuration."""

    def test_valid_config_with_extend(self):
        config = RunningTPConfig(
            enable_trailing_extremes=True,
            extend_by_ticks=20
        )
        self.assertTrue(config.enable_trailing_extremes)
        self.assertEqual(config.extend_by_ticks, 20)

    def test_valid_config_with_trail(self):
        config = RunningTPConfig(
            enable_profit_levels=True,
            trail_offset_ticks=50
        )
        self.assertTrue(config.enable_profit_levels)
        self.assertEqual(config.trail_offset_ticks, 50)

    def test_no_adjustment_mode_raises_error(self):
        with self.assertRaises(ValueError):
            RunningTPConfig(
                enable_trailing_extremes=True
                # No adjustment mode specified
            )


class TestAutoBreakevenManager(unittest.TestCase):
    """Test auto breakeven manager."""

    def setUp(self):
        self.mock_client = Mock()
        self.account_id = "12345"
        self.manager = AutoBreakevenManager(self.mock_client, self.account_id)

        self.config = AutoBreakevenConfig(
            trigger_mode="ticks",
            trigger_levels=[20, 40, 60],
            sl_offsets=[10, 30, 50]
        )

        self.position = PositionState(
            order_id="order1",
            account_id=self.account_id,
            symbol="XCME:ES.Z24",
            side=OrderSide.BUY,
            entry_price=5000.0,
            quantity=1,
            current_stop_loss=4980.0
        )

    def test_start_monitoring(self):
        self.manager.start_monitoring("order1", self.position, self.config)
        self.assertIn("order1", self.manager.managed_positions)

    def test_stop_monitoring(self):
        self.manager.start_monitoring("order1", self.position, self.config)
        self.manager.stop_monitoring("order1")
        self.assertNotIn("order1", self.manager.managed_positions)

    def test_no_trigger_below_level(self):
        self.manager.start_monitoring("order1", self.position, self.config)

        # Price at 5010 - below first trigger (5020)
        result = self.manager.check_and_update("order1", 5010.0)

        self.assertFalse(result)
        self.assertEqual(self.position.breakeven_moves_completed, 0)

    def test_first_move_trigger(self):
        self.manager.start_monitoring("order1", self.position, self.config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # Price at 5020 - hits first trigger
        result = self.manager.check_and_update("order1", 5020.0)

        self.assertTrue(result)
        self.assertEqual(self.position.breakeven_moves_completed, 1)
        self.assertEqual(self.position.current_stop_loss, 5010.0)  # entry + 10

        # Verify API call
        self.mock_client.update_order.assert_called_once()
        call_args = self.mock_client.update_order.call_args
        self.assertEqual(call_args[0][2]['stopLoss'], 5010.0)

    def test_second_move_trigger(self):
        self.manager.start_monitoring("order1", self.position, self.config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # First move
        self.manager.check_and_update("order1", 5020.0)
        self.assertEqual(self.position.breakeven_moves_completed, 1)

        # Second move
        result = self.manager.check_and_update("order1", 5040.0)

        self.assertTrue(result)
        self.assertEqual(self.position.breakeven_moves_completed, 2)
        self.assertEqual(self.position.current_stop_loss, 5030.0)  # entry + 30

    def test_all_three_moves(self):
        self.manager.start_monitoring("order1", self.position, self.config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # Move 1
        self.manager.check_and_update("order1", 5020.0)
        self.assertEqual(self.position.breakeven_moves_completed, 1)

        # Move 2
        self.manager.check_and_update("order1", 5040.0)
        self.assertEqual(self.position.breakeven_moves_completed, 2)

        # Move 3
        result = self.manager.check_and_update("order1", 5060.0)
        self.assertTrue(result)
        self.assertEqual(self.position.breakeven_moves_completed, 3)
        self.assertEqual(self.position.current_stop_loss, 5050.0)  # entry + 50

        # No more moves after 3
        result = self.manager.check_and_update("order1", 5100.0)
        self.assertFalse(result)
        self.assertEqual(self.position.breakeven_moves_completed, 3)

    def test_short_position(self):
        """Test auto breakeven for SHORT positions."""
        short_position = PositionState(
            order_id="order2",
            account_id=self.account_id,
            symbol="XCME:ES.Z24",
            side=OrderSide.SELL,
            entry_price=5000.0,
            quantity=1,
            current_stop_loss=5020.0
        )

        self.manager.start_monitoring("order2", short_position, self.config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # Price down to 4980 - profit of 20 ticks for SHORT
        result = self.manager.check_and_update("order2", 4980.0)

        self.assertTrue(result)
        self.assertEqual(short_position.current_stop_loss, 4990.0)  # entry - 10

    def test_percentage_mode(self):
        """Test percentage-based triggers."""
        config = AutoBreakevenConfig(
            trigger_mode="percentage",
            trigger_levels=[2, 4, 6],  # 2%, 4%, 6%
            sl_offsets=[10, 30, 50]
        )

        self.manager.start_monitoring("order1", self.position, config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # 2% profit on 5000 = 100 ticks, so price at 5100
        result = self.manager.check_and_update("order1", 5100.0)

        self.assertTrue(result)
        self.assertEqual(self.position.breakeven_moves_completed, 1)


class TestRunningTPManager(unittest.TestCase):
    """Test running take profit manager."""

    def setUp(self):
        self.mock_client = Mock()
        self.account_id = "12345"
        self.manager = RunningTPManager(self.mock_client, self.account_id)

        self.position = PositionState(
            order_id="order1",
            account_id=self.account_id,
            symbol="XCME:ES.Z24",
            side=OrderSide.BUY,
            entry_price=5000.0,
            quantity=1,
            current_take_profit=5050.0
        )

    def test_trailing_with_extend(self):
        """Test trailing extremes with extend mode."""
        config = RunningTPConfig(
            enable_trailing_extremes=True,
            extend_by_ticks=20
        )

        self.manager.start_monitoring("order1", self.position, config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # Price moves up - new high
        result = self.manager.check_and_update("order1", 5060.0)

        self.assertTrue(result)
        self.assertEqual(self.position.current_take_profit, 5070.0)  # 5050 + 20

    def test_trailing_with_offset(self):
        """Test trailing with offset mode."""
        config = RunningTPConfig(
            enable_trailing_extremes=True,
            trail_offset_ticks=50
        )

        self.manager.start_monitoring("order1", self.position, config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # Price at 5100
        result = self.manager.check_and_update("order1", 5100.0)

        # TP should be current price + 50
        self.assertTrue(result)
        self.assertEqual(self.position.current_take_profit, 5150.0)

    def test_profit_level_trigger(self):
        """Test profit level triggers."""
        config = RunningTPConfig(
            enable_profit_levels=True,
            profit_level_triggers=[30, 60, 90],
            extend_by_ticks=25
        )

        self.manager.start_monitoring("order1", self.position, config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # Price at 5030 - profit of 30 ticks
        result = self.manager.check_and_update("order1", 5030.0)

        self.assertTrue(result)
        self.assertEqual(self.position.current_take_profit, 5075.0)  # 5050 + 25
        self.assertIn(0, self.position.tp_profit_levels_triggered)

    def test_resistance_levels(self):
        """Test resistance/support level mode."""
        config = RunningTPConfig(
            enable_trailing_extremes=True,
            resistance_support_levels=[5100, 5150, 5200]
        )

        self.manager.start_monitoring("order1", self.position, config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # Price moves up
        self.position.highest_price = 5080.0
        result = self.manager.check_and_update("order1", 5080.0)

        # Should target next resistance at 5100
        if result:
            self.assertEqual(self.position.current_take_profit, 5100.0)

    def test_short_position_trailing(self):
        """Test trailing for SHORT positions."""
        short_position = PositionState(
            order_id="order2",
            account_id=self.account_id,
            symbol="XCME:ES.Z24",
            side=OrderSide.SELL,
            entry_price=5000.0,
            quantity=1,
            current_take_profit=4950.0
        )

        config = RunningTPConfig(
            enable_trailing_extremes=True,
            trail_offset_ticks=50
        )

        self.manager.start_monitoring("order2", short_position, config)
        self.mock_client.update_order.return_value = {"status": "OK"}

        # Price drops to 4900 - new low
        result = self.manager.check_and_update("order2", 4900.0)

        # TP should trail down: current price - 50
        self.assertTrue(result)
        self.assertEqual(short_position.current_take_profit, 4850.0)


class TestPositionState(unittest.TestCase):
    """Test position state tracking."""

    def test_update_price_extremes_long(self):
        position = PositionState(
            order_id="order1",
            account_id="12345",
            symbol="XCME:ES.Z24",
            side=OrderSide.BUY,
            entry_price=5000.0,
            quantity=1
        )

        position.update_price_extremes(5010.0)
        self.assertEqual(position.highest_price, 5010.0)
        self.assertEqual(position.lowest_price, 5010.0)

        position.update_price_extremes(5020.0)
        self.assertEqual(position.highest_price, 5020.0)
        self.assertEqual(position.lowest_price, 5010.0)

        position.update_price_extremes(5005.0)
        self.assertEqual(position.highest_price, 5020.0)
        self.assertEqual(position.lowest_price, 5005.0)


if __name__ == '__main__':
    unittest.main()
