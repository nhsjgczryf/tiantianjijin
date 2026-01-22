"""
Quantitative trading strategies for fund analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.database import get_session, Fund, FundValue


class StrategyBase:
    """Base class for trading strategies"""
    
    def __init__(self, fund_code):
        self.fund_code = fund_code
        self.session = get_session()
    
    def get_historical_data(self, days=365):
        """Get historical fund data as DataFrame"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        values = self.session.query(FundValue).filter(
            FundValue.fund_code == self.fund_code,
            FundValue.date >= start_date,
            FundValue.date <= end_date
        ).order_by(FundValue.date).all()
        
        data = [{
            'date': v.date,
            'net_value': v.net_value,
            'accumulated_value': v.accumulated_value,
            'daily_growth_rate': v.daily_growth_rate
        } for v in values]
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        return df
    
    def calculate_signal(self):
        """Calculate trading signal - to be implemented by subclasses"""
        raise NotImplementedError
    
    def backtest(self):
        """Backtest the strategy - to be implemented by subclasses"""
        raise NotImplementedError


class MovingAverageStrategy(StrategyBase):
    """Moving Average Crossover Strategy"""
    
    def __init__(self, fund_code, short_window=5, long_window=20):
        super().__init__(fund_code)
        self.short_window = short_window
        self.long_window = long_window
    
    def calculate_signal(self):
        """
        Calculate trading signal based on moving average crossover
        Returns: 'BUY', 'SELL', or 'HOLD'
        """
        df = self.get_historical_data(days=100)
        
        if df.empty or len(df) < self.long_window:
            return 'HOLD', 0.0
        
        # Calculate moving averages
        df['MA_short'] = df['net_value'].rolling(window=self.short_window).mean()
        df['MA_long'] = df['net_value'].rolling(window=self.long_window).mean()
        
        # Get latest values
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        signal = 'HOLD'
        confidence = 0.0
        
        # Golden cross - buy signal
        if previous['MA_short'] <= previous['MA_long'] and latest['MA_short'] > latest['MA_long']:
            signal = 'BUY'
            confidence = min(abs(latest['MA_short'] - latest['MA_long']) / latest['MA_long'] * 100, 100)
        
        # Death cross - sell signal
        elif previous['MA_short'] >= previous['MA_long'] and latest['MA_short'] < latest['MA_long']:
            signal = 'SELL'
            confidence = min(abs(latest['MA_short'] - latest['MA_long']) / latest['MA_long'] * 100, 100)
        
        return signal, confidence
    
    def backtest(self, initial_capital=10000):
        """
        Backtest the moving average strategy
        """
        df = self.get_historical_data(days=365)
        
        if df.empty or len(df) < self.long_window:
            return None
        
        # Calculate moving averages
        df['MA_short'] = df['net_value'].rolling(window=self.short_window).mean()
        df['MA_long'] = df['net_value'].rolling(window=self.long_window).mean()
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['MA_short'] > df['MA_long'], 'signal'] = 1  # Buy signal
        df['position'] = df['signal'].diff()
        
        # Calculate returns
        capital = initial_capital
        shares = 0
        trades = []
        
        for idx, row in df.iterrows():
            if row['position'] == 1:  # Buy
                shares = capital / row['net_value']
                trades.append({
                    'date': idx,
                    'action': 'BUY',
                    'price': row['net_value'],
                    'shares': shares,
                    'capital': capital
                })
                capital = 0
            elif row['position'] == -1 and shares > 0:  # Sell
                capital = shares * row['net_value']
                trades.append({
                    'date': idx,
                    'action': 'SELL',
                    'price': row['net_value'],
                    'shares': shares,
                    'capital': capital
                })
                shares = 0
        
        # Calculate final value
        final_value = capital if capital > 0 else shares * df.iloc[-1]['net_value']
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'trades': trades,
            'num_trades': len(trades)
        }


class MomentumStrategy(StrategyBase):
    """Momentum Strategy - buy winners, sell losers"""
    
    def __init__(self, fund_code, lookback_days=20):
        super().__init__(fund_code)
        self.lookback_days = lookback_days
    
    def calculate_signal(self):
        """
        Calculate signal based on momentum
        """
        df = self.get_historical_data(days=100)
        
        if df.empty or len(df) < self.lookback_days:
            return 'HOLD', 0.0
        
        # Calculate momentum
        recent_data = df.tail(self.lookback_days)
        momentum = (recent_data['net_value'].iloc[-1] - recent_data['net_value'].iloc[0]) / recent_data['net_value'].iloc[0] * 100
        
        signal = 'HOLD'
        confidence = min(abs(momentum), 100)
        
        if momentum > 5:  # Strong positive momentum
            signal = 'BUY'
        elif momentum < -5:  # Strong negative momentum
            signal = 'SELL'
        
        return signal, confidence


class ValueStrategy(StrategyBase):
    """Value Strategy - based on performance metrics"""
    
    def calculate_signal(self):
        """
        Calculate signal based on value metrics
        This is a simplified version - in practice would use more metrics
        """
        df = self.get_historical_data(days=100)
        
        if df.empty:
            return 'HOLD', 0.0
        
        # Calculate simple metrics
        current_value = df['net_value'].iloc[-1]
        avg_value = df['net_value'].mean()
        
        # If current value is significantly below average, consider buying
        deviation = (current_value - avg_value) / avg_value * 100
        
        signal = 'HOLD'
        confidence = min(abs(deviation), 100)
        
        if deviation < -10:  # 10% below average
            signal = 'BUY'
        elif deviation > 10:  # 10% above average
            signal = 'SELL'
        
        return signal, confidence


def analyze_fund(fund_code):
    """
    Comprehensive analysis of a fund using multiple strategies
    """
    strategies = {
        'Moving Average': MovingAverageStrategy(fund_code),
        'Momentum': MomentumStrategy(fund_code),
        'Value': ValueStrategy(fund_code)
    }
    
    results = {}
    
    for name, strategy in strategies.items():
        try:
            signal, confidence = strategy.calculate_signal()
            results[name] = {
                'signal': signal,
                'confidence': round(confidence, 2)
            }
        except Exception as e:
            results[name] = {
                'signal': 'ERROR',
                'confidence': 0,
                'error': str(e)
            }
    
    # Aggregate signals
    buy_votes = sum(1 for r in results.values() if r['signal'] == 'BUY')
    sell_votes = sum(1 for r in results.values() if r['signal'] == 'SELL')
    
    if buy_votes > sell_votes:
        overall_signal = 'BUY'
    elif sell_votes > buy_votes:
        overall_signal = 'SELL'
    else:
        overall_signal = 'HOLD'
    
    avg_confidence = np.mean([r['confidence'] for r in results.values() if 'error' not in r])
    
    return {
        'fund_code': fund_code,
        'overall_signal': overall_signal,
        'confidence': round(avg_confidence, 2),
        'strategy_signals': results
    }
