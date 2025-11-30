"""
Trading Economics Commodities Scraper
Parses commodities data from tradingeconomics.com using class-based architecture
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod


@dataclass
class Commodity:
    """Data class representing a single commodity entry"""
    asset: str
    name: str
    unit: str
    price: float
    change: float
    daily_pct: float
    weekly_pct: float
    monthly_pct: float
    yearly_pct: float
    three_year_pct: float
    date: str


class WebScraper:
    """Handles HTTP requests and HTML retrieval"""
    
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_page(self) -> Optional[str]:
        """Fetch the webpage content"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None


class TableParser:
    """Parses HTML tables and extracts commodities data"""
    
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.commodities: List[Commodity] = []
        self.current_asset_category = "Unknown"
    
    def parse_tables(self) -> List[Commodity]:
        """Parse all commodity tables from the page"""
        # Find all table rows
        rows = self.soup.find_all('tr')
        
        for row in rows:
            # Check if this row is a header row (category name)
            header = row.find('th')
            if header:
                header_text = header.get_text(strip=True)
                if header_text and header_text not in ['Price', 'Day', '%', 'Week', 'Month', 'Year', '3Y']:
                    # This is a category header (Energy, Metals, etc.)
                    self.current_asset_category = header_text
                continue
            
            cols = row.find_all('td')
            if len(cols) >= 8:  # Valid commodity row
                try:
                    commodity = self._parse_row(cols, self.current_asset_category)
                    if commodity:
                        self.commodities.append(commodity)
                except Exception as e:
                    # Skip malformed rows
                    continue
        
        return self.commodities
    
    def _parse_row(self, cols: List, asset_category: str) -> Optional[Commodity]:
        """Parse a single table row into a Commodity object"""
        try:
            # Extract text from cells
            cell_texts = [col.get_text(strip=True) for col in cols]
            
            # First cell contains name and unit (possibly on separate lines)
            name_unit_cell = cols[0]
            name, unit = self._split_name_unit_from_cell(name_unit_cell)
            
            # Parse numeric values
            price = self._parse_number(cell_texts[1])
            change = self._parse_number(cell_texts[2])
            daily = self._parse_percentage(cell_texts[3])
            weekly = self._parse_percentage(cell_texts[4])
            monthly = self._parse_percentage(cell_texts[5])
            yearly = self._parse_percentage(cell_texts[6])
            three_year = self._parse_percentage(cell_texts[7])
            date_raw = cell_texts[8] if len(cell_texts) > 8 else ""
            date = self._parse_date(date_raw)
            
            return Commodity(
                asset=asset_category,
                name=name,
                unit=unit,
                price=price,
                change=change,
                daily_pct=daily,
                weekly_pct=weekly,
                monthly_pct=monthly,
                yearly_pct=yearly,
                three_year_pct=three_year,
                date=date
            )
        except Exception:
            return None
    
    @staticmethod
    def _split_name_unit_from_cell(cell) -> tuple:
        """Split commodity name and unit from table cell"""
        # The cell contains name and unit, possibly in separate elements or lines
        # Try to find separate text elements within the cell
        text_elements = cell.find_all(text=True, recursive=True)
        clean_elements = [elem.strip() for elem in text_elements if elem.strip()]
        
        if len(clean_elements) >= 2:
            # Name is typically first, unit is second
            name = clean_elements[0]
            unit = clean_elements[1]
            return name, unit
        elif len(clean_elements) == 1:
            # Fall back to splitting single text
            text = clean_elements[0]
            parts = text.rsplit(' ', 1)
            if len(parts) == 2:
                return parts[0], parts[1]
            return text, ""
        else:
            return "", ""
    
    @staticmethod
    def _split_name_unit(text: str) -> tuple:
        """Split commodity name and unit from text (legacy method)"""
        # Pattern: Name Unit (e.g., "Crude Oil USD/Bbl")
        parts = text.rsplit(' ', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return text, ""
    
    @staticmethod
    def _parse_number(text: str) -> float:
        """Parse numeric value, handling commas and special cases"""
        try:
            # Remove commas and whitespace
            cleaned = text.replace(',', '').replace(' ', '').strip()
            return float(cleaned)
        except ValueError:
            return 0.0
    
    @staticmethod
    def _parse_percentage(text: str) -> float:
        """Parse percentage value"""
        try:
            # Remove % sign and whitespace
            cleaned = text.replace('%', '').replace(' ', '').strip()
            if cleaned == '' or cleaned == '-':
                return 0.0
            return float(cleaned)
        except ValueError:
            return 0.0
    
    @staticmethod
    def _parse_date(date_str: str) -> str:
        """Parse date from format like 'Nov/28' to 'yyyy/mm/dd'"""
        if not date_str or date_str.strip() == '':
            return ""
        
        try:
            # Handle format like "Nov/28" or "Nov/27"
            parts = date_str.strip().split('/')
            if len(parts) == 2:
                month_str = parts[0]
                day_str = parts[1]
                
                # Use current year (2025)
                year = 2025
                
                # Parse month name
                date_obj = datetime.strptime(f"{month_str} {day_str} {year}", "%b %d %Y")
                return date_obj.strftime("%Y/%m/%d")
            else:
                return date_str
        except Exception:
            return date_str


class CommodityDataManager:
    """Manages commodity data and provides analysis functionality"""
    
    def __init__(self, commodities: List[Commodity]):
        self.commodities = commodities
        self.df = self._create_dataframe()
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Convert commodities list to pandas DataFrame"""
        data = [
            {
                'Asset': c.asset,
                'Name': c.name,
                'Unit': c.unit,
                'Price': c.price,
                'Change': c.change,
                'Daily %': c.daily_pct,
                'Weekly %': c.weekly_pct,
                'Monthly %': c.monthly_pct,
                'Yearly %': c.yearly_pct,
                '3-Year %': c.three_year_pct,
                'Date': c.date
            }
            for c in self.commodities
        ]
        return pd.DataFrame(data)
    
    def get_columns(self) -> List[str]:
        """Return list of column names"""
        return self.df.columns.tolist()
    
    def display_summary(self):
        """Display summary of the data"""
        print(f"\n{'='*80}")
        print(f"COMMODITIES DATA SUMMARY")
        print(f"{'='*80}")
        print(f"Total commodities: {len(self.commodities)}")
        print(f"\nColumns: {', '.join(self.get_columns())}")
        print(f"{'='*80}\n")
    
    def display_data(self, num_rows: int = None):
        """Display first n rows of data. If num_rows is None, display all rows"""
        if num_rows is None:
            print(self.df.to_string(index=False))
        else:
            print(self.df.head(num_rows).to_string(index=False))
    
    def filter_by_category(self, keyword: str) -> pd.DataFrame:
        """Filter commodities by name keyword"""
        mask = self.df['Name'].str.contains(keyword, case=False, na=False)
        return self.df[mask]
    
    def get_top_performers(self, period: str = 'Daily %', n: int = 10) -> pd.DataFrame:
        """Get top performing commodities by period"""
        return self.df.nlargest(n, period)[['Asset', 'Name', 'Price', period]]
    
    def get_top_by_category(self, period: str = 'Daily %', n: int = 5) -> pd.DataFrame:
        """Get top n performers from each asset category"""
        result_frames = []
        
        # Get unique categories
        categories = self.df['Asset'].unique()
        
        for category in categories:
            # Filter by category
            category_df = self.df[self.df['Asset'] == category]
            # Get top n from this category
            top_n = category_df.nlargest(n, period)[['Asset', 'Name', 'Unit', 'Price', 'Change', period, 'Date']]
            result_frames.append(top_n)
        
        # Combine all results
        if result_frames:
            return pd.concat(result_frames, ignore_index=True)
        return pd.DataFrame()
    
    def get_strong_leads(self) -> pd.DataFrame:
        """Get commodities that appear in top 3 for any period (Daily, Weekly, Monthly, Yearly) within their category"""
        result_frames = []
        
        # Get unique categories
        categories = self.df['Asset'].unique()
        
        for category in categories:
            # Filter by category
            category_df = self.df[self.df['Asset'] == category]
            
            if len(category_df) == 0:
                continue
            
            # Get top 3 performers for each period
            top3_daily = set(category_df.nlargest(3, 'Daily %')['Name'].values)
            top3_weekly = set(category_df.nlargest(3, 'Weekly %')['Name'].values)
            top3_monthly = set(category_df.nlargest(3, 'Monthly %')['Name'].values)
            top3_yearly = set(category_df.nlargest(3, 'Yearly %')['Name'].values)
            
            # Union of all top 3 - any commodity in top 3 of ANY period qualifies
            strong_leads = top3_daily | top3_weekly | top3_monthly | top3_yearly
            
            if strong_leads:
                # Get details for all strong leads in this category
                leads_df = category_df[category_df['Name'].isin(strong_leads)][
                    ['Asset', 'Name', 'Unit', 'Price', 'Daily %', 'Weekly %', 'Monthly %', 'Yearly %', 'Date']
                ].copy()
                
                # Count how many periods each commodity is in top 3
                def count_top3_appearances(row):
                    count = 0
                    periods = []
                    if row['Name'] in top3_daily:
                        count += 1
                        periods.append('D')
                    if row['Name'] in top3_weekly:
                        count += 1
                        periods.append('W')
                    if row['Name'] in top3_monthly:
                        count += 1
                        periods.append('M')
                    if row['Name'] in top3_yearly:
                        count += 1
                        periods.append('Y')
                    return f"{count}/4 ({','.join(periods)})"
                
                leads_df['Match'] = leads_df.apply(count_top3_appearances, axis=1)
                
                result_frames.append(leads_df)
        
        # Combine all results
        if result_frames:
            combined_df = pd.concat(result_frames, ignore_index=True)
            
            # Add sort key for match count
            combined_df['_match_count'] = combined_df['Match'].str.split('/').str[0].astype(int)
            
            # Sort differently based on match count
            # For 1/4: sort by Daily %, then Weekly %
            # For 2/4+: sort by Weekly %, then Monthly %
            def sort_key(row):
                if row['_match_count'] == 1:
                    return (row['_match_count'], row['Daily %'], row['Weekly %'])
                else:
                    return (row['_match_count'], row['Weekly %'], row['Monthly %'])
            
            combined_df['_sort_tuple'] = combined_df.apply(sort_key, axis=1)
            combined_df = combined_df.sort_values('_sort_tuple', ascending=False).drop(columns=['_match_count', '_sort_tuple'])
            
            # Add rank column (overall ranking)
            combined_df.insert(0, 'Rank', range(1, len(combined_df) + 1))
            
            # Add rank within asset category
            combined_df['Rank_Asset'] = combined_df.groupby('Asset').cumcount() + 1
            combined_df.insert(1, 'Rank_Asset', combined_df.pop('Rank_Asset'))
            
            return combined_df
        return pd.DataFrame()
    
    def get_investment_opportunities(self) -> Dict[str, pd.DataFrame]:
        """Get best short-term, mid-term, and long-term investment opportunities by asset category"""
        opportunities = {
            'short_term': [],
            'mid_term': [],
            'long_term': []
        }
        
        # Get unique categories
        categories = self.df['Asset'].unique()
        
        for category in categories:
            # Filter by category
            category_df = self.df[self.df['Asset'] == category]
            
            if len(category_df) == 0:
                continue
            
            # Short-term: Strong Daily % with positive Weekly % confirmation
            # Look for high momentum right now
            short_term_candidates = category_df[
                (category_df['Daily %'] > 0) & 
                (category_df['Weekly %'] > 0)
            ].nlargest(1, 'Daily %')[['Asset', 'Name', 'Unit', 'Price', 'Daily %', 'Weekly %', 'Date']].copy()
            if not short_term_candidates.empty:
                short_term_candidates['Timeframe'] = 'Short-term'
                opportunities['short_term'].append(short_term_candidates)
            
            # Mid-term: Best Weekly % with positive Monthly % confirmation
            # Look for sustained momentum over weeks
            mid_term_candidates = category_df[
                (category_df['Weekly %'] > 0) & 
                (category_df['Monthly %'] > 0)
            ].nlargest(1, 'Weekly %')[['Asset', 'Name', 'Unit', 'Price', 'Weekly %', 'Monthly %', 'Date']].copy()
            if not mid_term_candidates.empty:
                mid_term_candidates['Timeframe'] = 'Mid-term'
                opportunities['mid_term'].append(mid_term_candidates)
            
            # Long-term: Best Yearly % with positive Monthly % confirmation
            # Look for strong long-term trends
            long_term_candidates = category_df[
                (category_df['Yearly %'] > 0) & 
                (category_df['Monthly %'] > 0)
            ].nlargest(1, 'Yearly %')[['Asset', 'Name', 'Unit', 'Price', 'Monthly %', 'Yearly %', 'Date']].copy()
            if not long_term_candidates.empty:
                long_term_candidates['Timeframe'] = 'Long-term'
                opportunities['long_term'].append(long_term_candidates)
        
        # Combine results for each timeframe
        result = {}
        for timeframe, frames in opportunities.items():
            if frames:
                combined = pd.concat(frames, ignore_index=True)
                
                # Add overall rank
                combined.insert(0, 'Rank', range(1, len(combined) + 1))
                
                # Add rank within asset category
                combined['Rank_Asset'] = combined.groupby('Asset').cumcount() + 1
                combined.insert(1, 'Rank_Asset', combined.pop('Rank_Asset'))
                
                result[timeframe] = combined
            else:
                result[timeframe] = pd.DataFrame()
        
        return result
    
    def export_to_csv(self, filename: str = 'commodities_data.csv'):
        """Export data to CSV file"""
        self.df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")


class DatabaseManager:
    """Manages MySQL database operations for daily commodity tracking"""
    
    def __init__(self, host: str = 'localhost', user: str = 'root', password: str = '', database: str = 'commodities_db'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print(f"Successfully connected to MySQL database: {self.database}")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.close()
            connection.close()
            print(f"Database {self.database} ready")
            return True
        except Error as e:
            print(f"Error creating database: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables for daily tracking"""
        if not self.connection or not self.connection.is_connected():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Table 1: Daily commodities data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commodities_daily (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    asset VARCHAR(50),
                    name VARCHAR(100),
                    unit VARCHAR(50),
                    price DECIMAL(15, 4),
                    change_value DECIMAL(15, 4),
                    daily_pct DECIMAL(10, 2),
                    weekly_pct DECIMAL(10, 2),
                    monthly_pct DECIMAL(10, 2),
                    yearly_pct DECIMAL(10, 2),
                    three_year_pct DECIMAL(10, 2),
                    update_date VARCHAR(20),
                    INDEX idx_date (date),
                    INDEX idx_asset_name (asset, name),
                    INDEX idx_name (name)
                )
            """)
            
            # Table 2: Strong leads tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strong_leads_daily (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    ranking INT,
                    rank_asset INT,
                    asset VARCHAR(50),
                    name VARCHAR(100),
                    unit VARCHAR(50),
                    price DECIMAL(15, 4),
                    daily_pct DECIMAL(10, 2),
                    weekly_pct DECIMAL(10, 2),
                    monthly_pct DECIMAL(10, 2),
                    yearly_pct DECIMAL(10, 2),
                    match_info VARCHAR(50),
                    update_date VARCHAR(20),
                    INDEX idx_date (date),
                    INDEX idx_ranking (ranking),
                    INDEX idx_asset_name (asset, name)
                )
            """)
            
            # Table 3: Investment opportunities tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_opportunities_daily (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    timeframe VARCHAR(20),
                    ranking INT,
                    rank_asset INT,
                    asset VARCHAR(50),
                    name VARCHAR(100),
                    unit VARCHAR(50),
                    price DECIMAL(15, 4),
                    daily_pct DECIMAL(10, 2),
                    weekly_pct DECIMAL(10, 2),
                    monthly_pct DECIMAL(10, 2),
                    yearly_pct DECIMAL(10, 2),
                    update_date VARCHAR(20),
                    INDEX idx_date (date),
                    INDEX idx_timeframe (timeframe),
                    INDEX idx_asset_name (asset, name)
                )
            """)
            
            cursor.close()
            print("Database tables created successfully")
            return True
        except Error as e:
            print(f"Error creating tables: {e}")
            return False
    
    def save_commodities(self, df: pd.DataFrame, current_date: date):
        """Save daily commodities data"""
        if not self.connection or not self.connection.is_connected():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO commodities_daily 
                    (date, asset, name, unit, price, change_value, daily_pct, weekly_pct, 
                     monthly_pct, yearly_pct, three_year_pct, update_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    current_date, row['Asset'], row['Name'], row['Unit'], row['Price'],
                    row['Change'], row['Daily %'], row['Weekly %'], row['Monthly %'],
                    row['Yearly %'], row['3-Year %'], row['Date']
                ))
            
            self.connection.commit()
            cursor.close()
            print(f"Saved {len(df)} commodities records for {current_date}")
            return True
        except Error as e:
            print(f"Error saving commodities: {e}")
            return False
    
    def save_strong_leads(self, df: pd.DataFrame, current_date: date):
        """Save daily strong leads data"""
        if not self.connection or not self.connection.is_connected():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO strong_leads_daily 
                    (date, ranking, rank_asset, asset, name, unit, price, daily_pct, weekly_pct,
                     monthly_pct, yearly_pct, match_info, update_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    current_date, row['Rank'], row['Rank_Asset'], row['Asset'], row['Name'],
                    row['Unit'], row['Price'], row['Daily %'], row['Weekly %'],
                    row['Monthly %'], row['Yearly %'], row['Match'], row['Date']
                ))
            
            self.connection.commit()
            cursor.close()
            print(f"Saved {len(df)} strong leads records for {current_date}")
            return True
        except Error as e:
            print(f"Error saving strong leads: {e}")
            return False
    
    def save_investment_opportunities(self, opportunities: Dict[str, pd.DataFrame], current_date: date):
        """Save daily investment opportunities data"""
        if not self.connection or not self.connection.is_connected():
            return False
        
        try:
            cursor = self.connection.cursor()
            total_saved = 0
            
            for timeframe, df in opportunities.items():
                if df.empty:
                    continue
                
                for _, row in df.iterrows():
                    # Get the appropriate percentage columns based on timeframe
                    daily_pct = row.get('Daily %', None)
                    weekly_pct = row.get('Weekly %', None)
                    monthly_pct = row.get('Monthly %', None)
                    yearly_pct = row.get('Yearly %', None)
                    
                    cursor.execute("""
                        INSERT INTO investment_opportunities_daily 
                        (date, timeframe, ranking, rank_asset, asset, name, unit, price,
                         daily_pct, weekly_pct, monthly_pct, yearly_pct, update_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        current_date, timeframe, row['Rank'], row['Rank_Asset'], row['Asset'],
                        row['Name'], row['Unit'], row['Price'], daily_pct, weekly_pct,
                        monthly_pct, yearly_pct, row['Date']
                    ))
                    total_saved += 1
            
            self.connection.commit()
            cursor.close()
            print(f"Saved {total_saved} investment opportunity records for {current_date}")
            return True
        except Error as e:
            print(f"Error saving investment opportunities: {e}")
            return False
    
    def get_ranking_changes(self, current_date: date, previous_days: int = 1) -> pd.DataFrame:
        """Get ranking changes compared to previous day(s)"""
        if not self.connection or not self.connection.is_connected():
            return pd.DataFrame()
        
        try:
            query = """
                SELECT 
                    t.name,
                    t.asset,
                    t.ranking as current_rank,
                    p.ranking as previous_rank,
                    (p.ranking - t.ranking) as rank_change,
                    t.daily_pct as current_daily_pct,
                    t.weekly_pct as current_weekly_pct,
                    t.match_info as current_match
                FROM strong_leads_daily t
                LEFT JOIN strong_leads_daily p ON t.name = p.name AND t.asset = p.asset
                    AND p.date = DATE_SUB(%s, INTERVAL %s DAY)
                WHERE t.date = %s
                ORDER BY ABS(p.ranking - t.ranking) DESC
            """
            
            df = pd.read_sql(query, self.connection, params=(current_date, previous_days, current_date))
            return df
        except Error as e:
            print(f"Error getting ranking changes: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")


@dataclass
class PriceAlert:
    """Data class for price change alerts"""
    commodity_name: str
    asset_type: str
    current_price: float
    previous_price: float
    price_change: float
    percent_change: float
    daily_pct: float
    weekly_pct: float
    date: str


class NotificationChannel(ABC):
    """Abstract base class for notification channels"""
    
    @abstractmethod
    def send(self, alert: PriceAlert, recipient: str) -> bool:
        """Send notification through this channel"""
        pass


class EmailNotification(NotificationChannel):
    """Email notification implementation"""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send(self, alert: PriceAlert, recipient: str) -> bool:
        """Send email notification"""
        try:
            subject = f"Price Alert: {alert.commodity_name} - {alert.percent_change:+.2f}%"
            
            body = f"""
            Commodity Price Alert
            =====================
            
            Commodity: {alert.commodity_name}
            Asset Type: {alert.asset_type}
            
            Current Price: {alert.current_price:.2f} {alert.asset_type}
            Previous Price: {alert.previous_price:.2f}
            Price Change: {alert.price_change:+.2f} ({alert.percent_change:+.2f}%)
            
            Performance:
            - Daily: {alert.daily_pct:+.2f}%
            - Weekly: {alert.weekly_pct:+.2f}%
            
            Date: {alert.date}
            
            This is an automated alert from your Commodities Tracker.
            """
            
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"Email sent to {recipient} for {alert.commodity_name}")
            return True
        except Exception as e:
            print(f"Error sending email to {recipient}: {e}")
            return False


class SMSNotification(NotificationChannel):
    """SMS notification implementation (using email-to-SMS gateway)"""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        
        # Common carrier SMS gateways
        self.carrier_gateways = {
            'verizon': '@vtext.com',
            'att': '@txt.att.net',
            't-mobile': '@tmomail.net',
            'sprint': '@messaging.sprintpcs.com',
            'boost': '@sms.myboostmobile.com',
            'cricket': '@sms.cricketwireless.net',
            'uscellular': '@email.uscc.net'
        }
    
    def send(self, alert: PriceAlert, recipient: str) -> bool:
        """Send SMS notification via email-to-SMS gateway"""
        try:
            # Short SMS message (160 chars limit consideration)
            body = f"{alert.commodity_name} Alert: ${alert.current_price:.2f} ({alert.percent_change:+.2f}%) Daily:{alert.daily_pct:+.2f}% Weekly:{alert.weekly_pct:+.2f}%"
            
            message = MIMEText(body)
            message['From'] = self.sender_email
            message['To'] = recipient
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"SMS sent to {recipient} for {alert.commodity_name}")
            return True
        except Exception as e:
            print(f"Error sending SMS to {recipient}: {e}")
            return False


@dataclass
class Subscription:
    """Subscription configuration for price alerts"""
    commodity_name: str
    email: Optional[str] = None
    sms_number: Optional[str] = None  # Format: phone@carrier.com (e.g., 5551234567@vtext.com)
    min_percent_change: float = 1.0  # Alert if change >= this percentage


class AlertService:
    """Manages price alerts and notifications"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.notification_channels: List[NotificationChannel] = []
        self.subscriptions: List[Subscription] = []
    
    def add_notification_channel(self, channel: NotificationChannel):
        """Add a notification channel (email, SMS, etc.)"""
        self.notification_channels.append(channel)
    
    def add_subscription(self, subscription: Subscription):
        """Add a commodity subscription"""
        self.subscriptions.append(subscription)
    
    def check_and_send_alerts(self, current_data: pd.DataFrame, current_date: date):
        """Check for price changes and send alerts based on subscriptions"""
        alerts_sent = 0
        
        for subscription in self.subscriptions:
            # Get current data for subscribed commodity
            current_commodity = current_data[
                current_data['Name'].str.lower() == subscription.commodity_name.lower()
            ]
            
            if current_commodity.empty:
                continue
            
            current_row = current_commodity.iloc[0]
            
            # Get previous day's data from database
            previous_data = self._get_previous_day_data(
                subscription.commodity_name, 
                current_row['Asset'],
                current_date
            )
            
            if previous_data is None:
                print(f"No previous data for {subscription.commodity_name} - skipping alert")
                continue
            
            # Calculate price change
            price_change = current_row['Price'] - previous_data['price']
            percent_change = (price_change / previous_data['price']) * 100 if previous_data['price'] != 0 else 0
            
            # Check if alert threshold is met
            if abs(percent_change) >= subscription.min_percent_change:
                alert = PriceAlert(
                    commodity_name=current_row['Name'],
                    asset_type=current_row['Asset'],
                    current_price=current_row['Price'],
                    previous_price=previous_data['price'],
                    price_change=price_change,
                    percent_change=percent_change,
                    daily_pct=current_row['Daily %'],
                    weekly_pct=current_row['Weekly %'],
                    date=current_row['Date']
                )
                
                # Send notifications through all channels
                for channel in self.notification_channels:
                    if subscription.email and isinstance(channel, EmailNotification):
                        if channel.send(alert, subscription.email):
                            alerts_sent += 1
                    
                    if subscription.sms_number and isinstance(channel, SMSNotification):
                        if channel.send(alert, subscription.sms_number):
                            alerts_sent += 1
        
        return alerts_sent
    
    def _get_previous_day_data(self, commodity_name: str, asset_type: str, current_date: date) -> Optional[Dict]:
        """Retrieve previous day's price from database"""
        if not self.db_manager.connection or not self.db_manager.connection.is_connected():
            return None
        
        try:
            cursor = self.db_manager.connection.cursor(dictionary=True)
            query = """
                SELECT price, daily_pct, weekly_pct
                FROM commodities_daily
                WHERE name = %s AND asset = %s AND date = DATE_SUB(%s, INTERVAL 1 DAY)
                LIMIT 1
            """
            cursor.execute(query, (commodity_name, asset_type, current_date))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Error retrieving previous data: {e}")
            return None


class CommoditiesApp:
    """Main application class orchestrating the scraping process"""
    
    def __init__(self, url: str):
        self.url = url
        self.scraper = WebScraper(url)
        self.data_manager: Optional[CommodityDataManager] = None
    
    def run(self):
        """Execute the scraping and parsing process"""
        print("Fetching data from Trading Economics...")
        html = self.scraper.fetch_page()
        
        if not html:
            print("Failed to fetch data.")
            return
        
        print("Parsing commodities tables...")
        parser = TableParser(html)
        commodities = parser.parse_tables()
        
        if not commodities:
            print("No commodities data found.")
            return
        
        print(f"Successfully parsed {len(commodities)} commodities.")
        
        self.data_manager = CommodityDataManager(commodities)
        return self.data_manager


def main():
    """Main entry point"""
    # Read URL from file
    url = "https://tradingeconomics.com/commodities"
    
    # Database configuration (update these with your MySQL credentials)
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Ilms2009',  # Add your MySQL password here
        'database': 'commodities_db'
    }
    
    # Notification settings - Set to True to enable alerts
    notifications_enabled = False  # Change to True to enable email/SMS alerts
    
    # Email/SMS configuration (update with your SMTP settings)
    notification_config = {
        'smtp_server': 'smtp.gmail.com',  # e.g., Gmail
        'smtp_port': 587,
        'sender_email': 'your_email@gmail.com',  # Your email
        'sender_password': 'your_app_password'   # App-specific password
    }
    
    # Define subscriptions for price alerts
    subscriptions = [
        Subscription(commodity_name='Lithium', email='recipient@example.com', sms_number=None, min_percent_change=1.0),
        Subscription(commodity_name='Gold', email='recipient@example.com', sms_number=None, min_percent_change=1.0),
        Subscription(commodity_name='Silver', email='recipient@example.com', sms_number=None, min_percent_change=1.0),
        Subscription(commodity_name='Platinum', email='recipient@example.com', sms_number=None, min_percent_change=1.0),
    ]
    
    # Create and run the application
    app = CommoditiesApp(url)
    data_manager = app.run()
    
    if data_manager:
        # Display summary and columns
        data_manager.display_summary()
        
        # Show first 40 commodities
        print("\nFirst 40 Commodities:")
        print("=" * 80)
        data_manager.display_data()  # Shows all records if no argument provided
        
        # Show top 5 daily performers from each category
        print("\n\nTop 5 Daily Performers by Category:")
        print("=" * 80)
        top_daily_by_category = data_manager.get_top_by_category('Daily %', 5)
        print(top_daily_by_category.to_string(index=False))
        
        # Show top 5 weekly performers from each category
        print("\n\nTop 5 Weekly Performers by Category:")
        print("=" * 80)
        top_weekly_by_category = data_manager.get_top_by_category('Weekly %', 5)
        print(top_weekly_by_category.to_string(index=False))
        
        # Show strong leads (top in daily, weekly, monthly, AND yearly for each category)
        print("\n\nStrong Leads (Top in Daily, Weekly, Monthly & Yearly by Category):")
        print("=" * 80)
        strong_leads = data_manager.get_strong_leads()
        print(strong_leads.to_string(index=False))
        
        # Show investment opportunities
        print("\n\nINVESTMENT OPPORTUNITIES BY TIMEFRAME:")
        print("=" * 80)
        opportunities = data_manager.get_investment_opportunities()
        
        print("\n--- SHORT-TERM (Daily/Weekly Momentum) ---")
        if not opportunities['short_term'].empty:
            print(opportunities['short_term'].to_string(index=False))
        else:
            print("No opportunities found")
        
        print("\n\n--- MID-TERM (Weekly/Monthly Trends) ---")
        if not opportunities['mid_term'].empty:
            print(opportunities['mid_term'].to_string(index=False))
        else:
            print("No opportunities found")
        
        print("\n\n--- LONG-TERM (Yearly Trends) ---")
        if not opportunities['long_term'].empty:
            print(opportunities['long_term'].to_string(index=False))
        else:
            print("No opportunities found")
        
        # Debug: Show top performers in Metals category for each period
        print("\n\nDEBUG - Metals Category Top Performers:")
        print("=" * 80)
        metals_df = data_manager.df[data_manager.df['Asset'] == 'Metals']
        if not metals_df.empty:
            print("\nTop Daily %:")
            print(metals_df.nlargest(3, 'Daily %')[['Name', 'Daily %', 'Weekly %', 'Monthly %', 'Yearly %']].to_string(index=False))
            print("\nTop Weekly %:")
            print(metals_df.nlargest(3, 'Weekly %')[['Name', 'Daily %', 'Weekly %', 'Monthly %', 'Yearly %']].to_string(index=False))
            print("\nTop Monthly %:")
            print(metals_df.nlargest(3, 'Monthly %')[['Name', 'Daily %', 'Weekly %', 'Monthly %', 'Yearly %']].to_string(index=False))
            print("\nTop Yearly %:")
            print(metals_df.nlargest(3, 'Yearly %')[['Name', 'Daily %', 'Weekly %', 'Monthly %', 'Yearly %']].to_string(index=False))
        
        # Export to CSV
        print("\n")
        data_manager.export_to_csv('commodities_data.csv')
        
        # Save to MySQL database
        print("\n" + "=" * 80)
        print("SAVING TO MYSQL DATABASE")
        print("=" * 80)
        
        db = DatabaseManager(**db_config)
        db.create_database()
        
        if db.connect():
            db.create_tables()
            
            current_date = date.today()
            
            # Save all data
            db.save_commodities(data_manager.df, current_date)
            db.save_strong_leads(strong_leads, current_date)
            db.save_investment_opportunities(opportunities, current_date)
            
            # Show ranking changes from previous day
            print("\n\nRANKING CHANGES (vs Previous Day):")
            print("=" * 80)
            ranking_changes = db.get_ranking_changes(current_date, previous_days=1)
            if not ranking_changes.empty:
                # Show top movers
                ranking_changes['rank_change'] = ranking_changes['rank_change'].fillna(0)
                top_movers = ranking_changes[ranking_changes['rank_change'] != 0].head(10)
                if not top_movers.empty:
                    print(top_movers.to_string(index=False))
                else:
                    print("No ranking changes detected (first run or same data)")
            else:
                print("No previous data for comparison (first run)")
            
            db.close()
            print("\nDatabase operations completed successfully!")
        
        # Send price alerts (if enabled)
        if notifications_enabled:
            print("\n" + "=" * 80)
            print("CHECKING PRICE ALERTS")
            print("=" * 80)
            
            # Initialize alert service
            db_for_alerts = DatabaseManager(**db_config)
            if db_for_alerts.connect():
                alert_service = AlertService(db_for_alerts)
                
                # Add notification channels
                email_channel = EmailNotification(
                    notification_config['smtp_server'],
                    notification_config['smtp_port'],
                    notification_config['sender_email'],
                    notification_config['sender_password']
                )
                sms_channel = SMSNotification(
                    notification_config['smtp_server'],
                    notification_config['smtp_port'],
                    notification_config['sender_email'],
                    notification_config['sender_password']
                )
                
                alert_service.add_notification_channel(email_channel)
                alert_service.add_notification_channel(sms_channel)
                
                # Add subscriptions
                for sub in subscriptions:
                    alert_service.add_subscription(sub)
                
                # Check and send alerts
                current_date = date.today()
                alerts_sent = alert_service.check_and_send_alerts(data_manager.df, current_date)
                print(f"\nTotal alerts sent: {alerts_sent}")
                
                db_for_alerts.close()
        else:
            print("\n" + "=" * 80)
            print("PRICE ALERTS: DISABLED")
            print("Set 'notifications_enabled = True' to enable alerts")
            print("=" * 80)


if __name__ == "__main__":
    main()
