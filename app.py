"""
Flask web application for fund analysis visualization
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
from datetime import datetime, timedelta
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.database import init_db, get_session, Fund, FundValue, FundPerformance
from strategies.trading_strategies import analyze_fund, MovingAverageStrategy

app = Flask(__name__)
CORS(app)

# Initialize database
init_db()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/funds')
def get_funds():
    """Get list of all funds"""
    session = get_session()
    try:
        funds = session.query(Fund).all()
        result = [{
            'code': f.fund_code,
            'name': f.fund_name,
            'type': f.fund_type,
            'company': f.company,
            'manager': f.manager
        } for f in funds]
        return jsonify(result)
    finally:
        session.close()


@app.route('/api/fund/<fund_code>')
def get_fund_detail(fund_code):
    """Get detailed information for a specific fund"""
    session = get_session()
    try:
        fund = session.query(Fund).filter_by(fund_code=fund_code).first()
        if not fund:
            return jsonify({'error': 'Fund not found'}), 404
        
        return jsonify({
            'code': fund.fund_code,
            'name': fund.fund_name,
            'type': fund.fund_type,
            'company': fund.company,
            'manager': fund.manager
        })
    finally:
        session.close()


@app.route('/api/fund/<fund_code>/values')
def get_fund_values(fund_code):
    """Get historical values for a fund"""
    days = request.args.get('days', 365, type=int)
    session = get_session()
    
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        values = session.query(FundValue).filter(
            FundValue.fund_code == fund_code,
            FundValue.date >= start_date,
            FundValue.date <= end_date
        ).order_by(FundValue.date).all()
        
        result = [{
            'date': v.date.isoformat(),
            'net_value': v.net_value,
            'accumulated_value': v.accumulated_value,
            'daily_growth_rate': v.daily_growth_rate
        } for v in values]
        
        return jsonify(result)
    finally:
        session.close()


@app.route('/api/fund/<fund_code>/performance')
def get_fund_performance(fund_code):
    """Get performance metrics for a fund"""
    session = get_session()
    
    try:
        performance = session.query(FundPerformance).filter_by(
            fund_code=fund_code
        ).order_by(FundPerformance.date.desc()).first()
        
        if not performance:
            return jsonify({'error': 'No performance data available'}), 404
        
        return jsonify({
            'fund_code': performance.fund_code,
            'date': performance.date.isoformat(),
            'week_return': performance.week_return,
            'month_return': performance.month_return,
            'quarter_return': performance.quarter_return,
            'half_year_return': performance.half_year_return,
            'year_return': performance.year_return,
            'three_year_return': performance.three_year_return
        })
    finally:
        session.close()


@app.route('/api/fund/<fund_code>/analysis')
def get_fund_analysis(fund_code):
    """Get quantitative analysis and trading signals for a fund"""
    try:
        analysis = analyze_fund(fund_code)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/fund/<fund_code>/backtest')
def get_backtest(fund_code):
    """Get backtest results for a fund"""
    try:
        strategy = MovingAverageStrategy(fund_code)
        results = strategy.backtest()
        
        if results is None:
            return jsonify({'error': 'Insufficient data for backtesting'}), 400
        
        # Convert datetime objects to strings
        for trade in results['trades']:
            trade['date'] = trade['date'].isoformat()
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/top-performers')
def get_top_performers():
    """Get top performing funds"""
    period = request.args.get('period', 'month')
    limit = request.args.get('limit', 10, type=int)
    
    session = get_session()
    
    try:
        # Map period to column
        period_map = {
            'week': FundPerformance.week_return,
            'month': FundPerformance.month_return,
            'quarter': FundPerformance.quarter_return,
            'year': FundPerformance.year_return
        }
        
        if period not in period_map:
            period = 'month'
        
        # Get top performers
        performances = session.query(
            FundPerformance, Fund
        ).join(
            Fund, FundPerformance.fund_code == Fund.fund_code
        ).order_by(
            period_map[period].desc()
        ).limit(limit).all()
        
        result = [{
            'fund_code': perf.fund_code,
            'fund_name': fund.fund_name,
            'return': getattr(perf, f'{period}_return'),
            'fund_type': fund.fund_type
        } for perf, fund in performances]
        
        return jsonify(result)
    finally:
        session.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
