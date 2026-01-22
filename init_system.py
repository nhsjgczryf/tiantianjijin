#!/usr/bin/env python3
"""
Initialize the fund analysis system
This script sets up the database and loads initial data
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import init_db, get_session, Fund, FundValue, FundPerformance
from scrapers.fund_scraper import FundScraper
from datetime import datetime, timedelta

def main():
    """Initialize the system"""
    print("="*60)
    print("天天基金分析系统 - 初始化")
    print("="*60)
    
    # Step 1: Initialize database
    print("\n1. 初始化数据库...")
    init_db()
    print("   ✓ 数据库初始化完成")
    
    # Step 2: Load initial fund data
    print("\n2. 加载基金数据...")
    scraper = FundScraper()
    session = get_session()
    
    try:
        # Get fund list
        funds = scraper.get_fund_list()
        print(f"   找到 {len(funds)} 只基金")
        
        # Add funds to database
        for fund_data in funds:
            # Check if exists
            existing = session.query(Fund).filter_by(
                fund_code=fund_data['code']
            ).first()
            
            if not existing:
                # Get detailed info
                fund_info = scraper.get_fund_info(fund_data['code'])
                
                fund = Fund(
                    fund_code=fund_data['code'],
                    fund_name=fund_data['name'],
                    fund_type=fund_data.get('type', ''),
                    company=fund_info.get('company', '') if fund_info else '',
                    manager=fund_info.get('manager', '') if fund_info else ''
                )
                session.add(fund)
                print(f"   + 添加基金: {fund_data['code']} - {fund_data['name']}")
        
        session.commit()
        print("   ✓ 基金列表加载完成")
        
        # Step 3: Load historical data
        print("\n3. 加载历史数据...")
        funds_in_db = session.query(Fund).all()
        
        for fund in funds_in_db:
            # Get historical values (last 30 days for initial load)
            values = scraper.get_fund_values(
                fund.fund_code,
                start_date=datetime.now() - timedelta(days=30)
            )
            
            for value_data in values:
                value = FundValue(
                    fund_code=fund.fund_code,
                    date=value_data['date'].date(),
                    net_value=value_data['net_value'],
                    accumulated_value=value_data['accumulated_value'],
                    daily_growth_rate=value_data['daily_growth_rate']
                )
                session.add(value)
            
            # Get performance metrics
            performance_data = scraper.get_fund_performance(fund.fund_code)
            if performance_data:
                performance = FundPerformance(
                    fund_code=fund.fund_code,
                    date=performance_data['date'],
                    week_return=performance_data['week_return'],
                    month_return=performance_data['month_return'],
                    quarter_return=performance_data['quarter_return'],
                    half_year_return=performance_data['half_year_return'],
                    year_return=performance_data['year_return'],
                    three_year_return=performance_data['three_year_return']
                )
                session.add(performance)
            
            print(f"   + 加载 {fund.fund_code} 的历史数据")
        
        session.commit()
        print("   ✓ 历史数据加载完成")
        
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        session.rollback()
    finally:
        session.close()
    
    print("\n" + "="*60)
    print("✓ 初始化完成！")
    print("="*60)
    print("\n使用说明:")
    print("1. 启动Web服务: python app.py")
    print("2. 访问: http://localhost:5000")
    print("3. 每日更新: python backend/update_data.py")
    print("\n")

if __name__ == '__main__':
    main()
