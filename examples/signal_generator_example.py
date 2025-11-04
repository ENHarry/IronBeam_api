"""
Example: Using the Signal Generator for Trading Bot

This example demonstrates how to use the combined indicator signal generator
to get trading signals based on Supertrend, Overbought/Oversold, and Trending indicators.

The signal generator requires at least 2 out of 3 indicators to agree before
generating a BUY or SELL signal, otherwise it returns HOLD.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from indicators import SignalGenerator


def create_sample_data():
    """Create sample price data for demonstration."""
    # Generate sample OHLC data
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')

    # Simulate price movement with trend
    base_price = 100
    trend = np.linspace(0, 20, 200)  # Upward trend
    noise = np.random.randn(200) * 2

    close = base_price + trend + noise

    # Generate high, low, open from close
    high = close + np.random.rand(200) * 2
    low = close - np.random.rand(200) * 2
    open_price = close + np.random.randn(200) * 0.5

    df = pd.DataFrame({
        'timestamp': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
    })

    return df


def example_basic_usage():
    """Basic usage example."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)

    # Create sample data
    df = create_sample_data()

    # Initialize signal generator with default parameters
    signal_gen = SignalGenerator()

    # Get current signal
    current_signal = signal_gen.get_current_signal(df)
    print(f"\nCurrent Signal: {current_signal}")

    # Get detailed signal information
    details = signal_gen.get_signal_details(df)
    print("\nSignal Details:")
    print(f"  Final Signal: {details['final_signal']}")
    print(f"  Supertrend: {details['supertrend']}")
    print(f"  Overbought/Oversold: {details['overbought_oversold']}")
    print(f"  Trending: {details['trending']}")
    print(f"  Buy Votes: {details['buy_votes']}/3")
    print(f"  Sell Votes: {details['sell_votes']}/3")


def example_custom_parameters():
    """Example with custom indicator parameters."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Parameters")
    print("=" * 60)

    # Create sample data
    df = create_sample_data()

    # Initialize with custom parameters
    signal_gen = SignalGenerator(
        supertrend_params={
            'atr_period': 14,
            'atr_multiplier': 2.5,
            'use_atr': True
        },
        overbought_oversold_params={
            'length': 7
        },
        trending_params={
            'swing_period': 10,
            'ma_period': 30
        }
    )

    # Get signal
    details = signal_gen.get_signal_details(df)
    print(f"\nFinal Signal: {details['final_signal']}")
    print(f"Individual Signals: ST={details['supertrend']}, "
          f"OB/OS={details['overbought_oversold']}, TR={details['trending']}")


def example_full_signal_history():
    """Generate full signal history."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Full Signal History")
    print("=" * 60)

    # Create sample data
    df = create_sample_data()

    # Initialize signal generator
    signal_gen = SignalGenerator()

    # Generate all signals
    signals_df = signal_gen.generate_signals(df)

    # Show recent signals
    print("\nLast 10 signals:")
    print(signals_df[[
        'close', 'supertrend_signal', 'overbought_oversold_signal',
        'trending_signal', 'final_signal', 'buy_votes', 'sell_votes'
    ]].tail(10).to_string())

    # Count signal distribution
    print("\n\nSignal Distribution:")
    print(f"  BUY signals: {(signals_df['final_signal'] == 1).sum()}")
    print(f"  SELL signals: {(signals_df['final_signal'] == -1).sum()}")
    print(f"  HOLD signals: {(signals_df['final_signal'] == 0).sum()}")


def example_trading_bot_integration():
    """Example of how to integrate with a trading bot."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Trading Bot Integration")
    print("=" * 60)

    # Simulate live trading scenario
    df = create_sample_data()

    # Initialize signal generator
    signal_gen = SignalGenerator()

    # Trading bot logic
    position = None  # None, 'LONG', or 'SHORT'
    entry_price = None

    print("\nSimulated Trading:")
    print("-" * 60)

    # Check signals for last 20 bars
    for i in range(len(df) - 20, len(df)):
        # Get data up to current bar
        current_data = df.iloc[:i+1]

        # Get signal
        signal = signal_gen.get_current_signal(current_data)
        current_price = df.iloc[i]['close']
        timestamp = df.iloc[i]['timestamp']

        # Trading logic
        if signal == 'BUY' and position != 'LONG':
            if position == 'SHORT':
                # Close short position
                pnl = entry_price - current_price
                print(f"{timestamp}: CLOSE SHORT at {current_price:.2f} | PnL: {pnl:.2f}")
                position = None

            # Open long position
            print(f"{timestamp}: OPEN LONG at {current_price:.2f}")
            position = 'LONG'
            entry_price = current_price

        elif signal == 'SELL' and position != 'SHORT':
            if position == 'LONG':
                # Close long position
                pnl = current_price - entry_price
                print(f"{timestamp}: CLOSE LONG at {current_price:.2f} | PnL: {pnl:.2f}")
                position = None

            # Open short position
            print(f"{timestamp}: OPEN SHORT at {current_price:.2f}")
            position = 'SHORT'
            entry_price = current_price

    # Close any open position at the end
    if position:
        final_price = df.iloc[-1]['close']
        if position == 'LONG':
            pnl = final_price - entry_price
        else:
            pnl = entry_price - final_price
        print(f"{df.iloc[-1]['timestamp']}: CLOSE {position} at {final_price:.2f} | PnL: {pnl:.2f}")


def example_with_real_data():
    """Example showing how to use with real market data."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Using with Real Market Data")
    print("=" * 60)

    print("\nTo use with real market data from IronBeam API:")
    print("""
    from ironbeam import IronBeamClient
    from indicators import SignalGenerator
    import pandas as pd

    # Initialize client
    client = IronBeamClient(username='your_username', password='your_password')
    client.authenticate()

    # Get historical data
    symbol = 'MNQ'  # Example: Micro E-mini Nasdaq
    bars = client.get_historical_bars(
        symbol=symbol,
        interval='1H',
        start_date='2024-01-01',
        end_date='2024-01-31'
    )

    # Convert to DataFrame
    df = pd.DataFrame(bars)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Ensure required columns exist (high, low, close)
    # Adjust column names if needed based on API response

    # Initialize signal generator
    signal_gen = SignalGenerator()

    # Get current signal
    signal = signal_gen.get_current_signal(df)
    details = signal_gen.get_signal_details(df)

    print(f"Current Signal for {symbol}: {signal}")
    print(f"Signal Details: {details}")
    """)


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_custom_parameters()
    example_full_signal_history()
    example_trading_bot_integration()
    example_with_real_data()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
