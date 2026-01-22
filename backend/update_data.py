"""
Data update scheduler - runs daily to update fund data
"""
import schedule
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.database import init_db, get_session, Fund, FundValue, FundPerformance
from scrapers.fund_scraper import FundScraper


class DataUpdater:
    """Handles daily data updates"""
    
    def __init__(self):
        self.scraper = FundScraper()
        init_db()
    
    def update_fund_list(self):
        """Update the list of funds"""
        print(f"[{datetime.now()}] Updating fund list...")
        session = get_session()
        
        try:
            funds = self.scraper.get_fund_list()
            
            for fund_data in funds:
                # Check if fund already exists
                existing = session.query(Fund).filter_by(
                    fund_code=fund_data['code']
                ).first()
                
                if not existing:
                    # Get detailed info
                    fund_info = self.scraper.get_fund_info(fund_data['code'])
                    if fund_info:
                        fund = Fund(
                            fund_code=fund_data['code'],
                            fund_name=fund_data['name'],
                            fund_type=fund_data.get('type', ''),
                            company=fund_info.get('company', ''),
                            manager=fund_info.get('manager', '')
                        )
                        session.add(fund)
                        print(f"  Added new fund: {fund_data['code']} - {fund_data['name']}")
            
            session.commit()
            print(f"Fund list update completed. Total funds: {session.query(Fund).count()}")
            
        except Exception as e:
            print(f"Error updating fund list: {e}")
            session.rollback()
        finally:
            session.close()
    
    def update_fund_values(self):
        """Update daily values for all funds"""
        print(f"[{datetime.now()}] Updating fund values...")
        session = get_session()
        
        try:
            funds = session.query(Fund).all()
            
            for fund in funds:
                # Get latest value date
                latest = session.query(FundValue).filter_by(
                    fund_code=fund.fund_code
                ).order_by(FundValue.date.desc()).first()
                
                start_date = latest.date if latest else datetime.now().date()
                
                # Get recent values
                values = self.scraper.get_fund_values(
                    fund.fund_code,
                    start_date=datetime.combine(start_date, datetime.min.time())
                )
                
                for value_data in values[-10:]:  # Only last 10 days
                    # Check if already exists
                    existing = session.query(FundValue).filter_by(
                        fund_code=fund.fund_code,
                        date=value_data['date'].date()
                    ).first()
                    
                    if not existing:
                        value = FundValue(
                            fund_code=fund.fund_code,
                            date=value_data['date'].date(),
                            net_value=value_data['net_value'],
                            accumulated_value=value_data['accumulated_value'],
                            daily_growth_rate=value_data['daily_growth_rate']
                        )
                        session.add(value)
                
                # Update performance metrics
                performance_data = self.scraper.get_fund_performance(fund.fund_code)
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
            
            session.commit()
            print(f"Fund values update completed.")
            
        except Exception as e:
            print(f"Error updating fund values: {e}")
            session.rollback()
        finally:
            session.close()
    
    def run_daily_update(self):
        """Run complete daily update"""
        print(f"\n{'='*50}")
        print(f"Starting daily update at {datetime.now()}")
        print(f"{'='*50}\n")
        
        self.update_fund_list()
        self.update_fund_values()
        
        print(f"\n{'='*50}")
        print(f"Daily update completed at {datetime.now()}")
        print(f"{'='*50}\n")


def main():
    """Main scheduler function"""
    updater = DataUpdater()
    
    # Run immediately on start
    updater.run_daily_update()
    
    # Schedule daily updates at 6 PM
    schedule.every().day.at("18:00").do(updater.run_daily_update)
    
    print("Scheduler started. Daily updates scheduled for 18:00.")
    print("Press Ctrl+C to stop.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == '__main__':
    main()
