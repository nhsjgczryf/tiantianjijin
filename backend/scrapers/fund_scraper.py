"""
Web scraper for fund data from public sources
"""
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta
import json

class FundScraper:
    """Scraper for fund data"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.base_url = 'http://fund.eastmoney.com'
    
    def get_fund_list(self, page=1, per_page=50):
        """
        Get list of funds
        Returns a list of fund codes and names
        """
        # Using a popular fund data source (East Money)
        url = f'{self.base_url}/data/fundranking.html'
        
        try:
            # For demonstration, return some popular fund codes
            # In production, this would scrape actual data
            sample_funds = [
                {'code': '110022', 'name': '易方达消费行业', 'type': '股票型'},
                {'code': '161725', 'name': '招商中证白酒指数', 'type': '指数型'},
                {'code': '000001', 'name': '华夏成长', 'type': '混合型'},
                {'code': '110011', 'name': '易方达中小盘', 'type': '股票型'},
                {'code': '163406', 'name': '兴全合润', 'type': '混合型'},
                {'code': '217005', 'name': '招商先锋', 'type': '股票型'},
                {'code': '519674', 'name': '银河创新成长', 'type': '混合型'},
                {'code': '260108', 'name': '景顺长城新兴成长', 'type': '股票型'},
                {'code': '001475', 'name': '易方达国防军工', 'type': '股票型'},
                {'code': '320007', 'name': '诺安成长', 'type': '股票型'},
            ]
            
            return sample_funds
        except Exception as e:
            print(f"Error fetching fund list: {e}")
            return []
    
    def get_fund_info(self, fund_code):
        """
        Get detailed information for a specific fund
        """
        url = f'{self.base_url}/f10/jbgk_{fund_code}.html'
        
        try:
            # Simulated fund info for demonstration
            fund_info = {
                'fund_code': fund_code,
                'fund_name': f'基金{fund_code}',
                'fund_type': '混合型',
                'company': '示例基金公司',
                'manager': '示例基金经理'
            }
            return fund_info
        except Exception as e:
            print(f"Error fetching fund info for {fund_code}: {e}")
            return None
    
    def get_fund_values(self, fund_code, start_date=None, end_date=None):
        """
        Get historical net values for a fund
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        try:
            # Simulated historical data for demonstration
            # In production, this would fetch real data from API or scraping
            values = []
            current_date = start_date
            base_value = 1.0
            
            while current_date <= end_date:
                # Skip weekends
                if current_date.weekday() < 5:
                    # Simulate random daily changes
                    import random
                    daily_change = random.uniform(-0.03, 0.03)
                    base_value *= (1 + daily_change)
                    
                    values.append({
                        'date': current_date,
                        'net_value': round(base_value, 4),
                        'accumulated_value': round(base_value * 1.2, 4),
                        'daily_growth_rate': round(daily_change * 100, 2)
                    })
                
                current_date += timedelta(days=1)
            
            return values
        except Exception as e:
            print(f"Error fetching fund values for {fund_code}: {e}")
            return []
    
    def get_fund_performance(self, fund_code):
        """
        Get performance metrics for a fund
        """
        try:
            # Simulated performance data
            import random
            performance = {
                'fund_code': fund_code,
                'date': datetime.now().date(),
                'week_return': round(random.uniform(-5, 5), 2),
                'month_return': round(random.uniform(-10, 10), 2),
                'quarter_return': round(random.uniform(-15, 15), 2),
                'half_year_return': round(random.uniform(-20, 20), 2),
                'year_return': round(random.uniform(-30, 30), 2),
                'three_year_return': round(random.uniform(-40, 60), 2)
            }
            return performance
        except Exception as e:
            print(f"Error fetching performance for {fund_code}: {e}")
            return None
