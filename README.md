# Trading Economics Commodities Scraper

A comprehensive Python-based web scraper that collects, analyzes, and tracks commodity price data from Trading Economics. Features automated alerts, historical tracking, and investment analysis across multiple timeframes.

## 🌟 Features

- **Automated Data Collection**: Scrapes commodity prices, percentage changes, and trends from Trading Economics
- **Multi-Category Support**: Tracks commodities across Energy, Metals, Agriculture, Livestock, and Industrial sectors
- **Historical Database**: MySQL persistence with day-over-day ranking change detection
- **Smart Analysis**:
  - Top performers by category (Daily, Weekly, Monthly)
  - Strong leads identification (commodities topping multiple timeframes)
  - Investment opportunities (Short/Mid/Long term with momentum confirmation)
- **Alert System**: Email and SMS notifications for price changes based on custom subscriptions
- **Class-Based Architecture**: Clean OOP design with encapsulation and loose coupling
- **Task Automation**: Windows Task Scheduler integration for daily runs

## 📋 Requirements

- Python 3.8+
- MySQL Server 5.7+ or 8.0+
- Internet connection

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/TradingEconomics.git
   cd TradingEconomics
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install MySQL Server**
   - Download from [MySQL Downloads](https://dev.mysql.com/downloads/mysql/)
   - Set root password during installation
   - Verify service is running:
     ```powershell
     Get-Service MySQL*
     ```

## ⚙️ Configuration

Edit `commodities_scraper.py` to configure:

### Database Settings (line ~953)
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',
    'database': 'commodities_db'
}
```

### Enable Notifications (line ~961)
```python
notifications_enabled = True  # Default: False

notification_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',
    'sender_password': 'your_app_password'
}
```

### Add Subscriptions (line ~968)
```python
subscriptions = [
    Subscription(commodity_name='Lithium', email='alerts@example.com', min_percent_change=1.0),
    Subscription(commodity_name='Gold', email='alerts@example.com', min_percent_change=1.0),
    # Add more...
]
```

## 🎯 Usage

### Run Manually
```bash
python commodities_scraper.py
```

### Schedule Daily at 5 AM

**Option 1: PowerShell (Administrator)**
```powershell
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "commodities_scraper.py" -WorkingDirectory "C:\Path\To\TradingEconomics"
$trigger = New-ScheduledTaskTrigger -Daily -At 5:00AM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName "CommoditiesDaily" -Action $action -Trigger $trigger -Settings $settings
```

**Option 2: Use Batch File**
```bash
# Schedule run_commodities_scraper.bat in Task Scheduler
# Logs will be saved to logs/ directory
```

## 📊 Output Reports

The scraper generates several reports:

1. **All Commodities** - Complete dataset with asset, name, unit, price, changes, date
2. **Top 5 Daily Performers by Category** - Best daily movers per asset type
3. **Top 5 Weekly Performers by Category** - Best weekly movers per asset type
4. **Strong Leads** - Commodities appearing in top 3 across multiple timeframes
5. **Investment Opportunities** - Categorized by Short/Mid/Long term with rankings

## 🗄️ Database Schema

Three main tables auto-created on first run:

- `commodities_daily` - Full historical commodity data
- `strong_leads_daily` - Daily top performers with rankings
- `investment_opportunities_daily` - Investment picks by timeframe

### Data Columns

- **Asset**: The category/type of commodity (Energy, Metals, Agriculture, Livestock, Industrial)
- **Name**: The commodity name (e.g., Lithium, Gold, Silver)
- **Unit**: The unit of measurement (e.g., CNY/T, USD/t Oz, USD/lb)
- **Price**: Current price
- **Change**: Price change in absolute units
- **Daily %**: Daily percentage change
- **Weekly %**: Weekly percentage change
- **Monthly %**: Monthly percentage change
- **Yearly %**: Yearly percentage change
- **3-Year %**: Three-year percentage change
- **Date**: Date of the data in yyyy/mm/dd format

### Query Examples
```sql
-- View today's data
SELECT * FROM commodities_daily WHERE date = CURDATE();

-- Check strong leads
SELECT * FROM strong_leads_daily WHERE date = CURDATE() ORDER BY ranking;

-- Find investment opportunities
SELECT * FROM investment_opportunities_daily 
WHERE date = CURDATE() AND timeframe = 'Short-term' 
ORDER BY ranking;

-- Track ranking changes
SELECT commodity_name, ranking, previous_ranking, ranking_change 
FROM strong_leads_daily 
WHERE date = CURDATE() AND ranking_change IS NOT NULL;
```

## 🏗️ Architecture

### Core Classes

- **Commodity** (dataclass) - Data model for commodity information
- **WebScraper** - HTTP client with user-agent headers
- **TableParser** - HTML parsing with multi-line cell handling and category detection
- **CommodityDataManager** - DataFrame operations, analysis, and report generation
- **DatabaseManager** - MySQL CRUD operations and historical tracking
- **NotificationChannel** (ABC) - Abstract interface for notifications
- **EmailNotification** / **SMSNotification** - Concrete notification implementations
- **AlertService** - Manages subscriptions and sends price alerts
- **CommoditiesApp** - Main orchestrator

### Design Principles
- Separation of concerns
- Dependency injection
- Abstract base classes for extensibility
- Type hints for clarity
- Comprehensive error handling

## 📧 Email/SMS Alerts

### Gmail Setup
1. Enable 2-Factor Authentication
2. Generate App Password: Google Account → Security → App passwords
3. Use App Password in `notification_config`

### SMS via Email Gateway
```python
# Carrier email-to-SMS gateways (US)
AT&T: number@txt.att.net
T-Mobile: number@tmomail.net
Verizon: number@vtext.com
Sprint: number@messaging.sprintpcs.com
```

## 📁 Project Structure

```
TradingEconomics/
├── commodities_scraper.py          # Main application
├── requirements.txt                # Python dependencies
├── run_commodities_scraper.bat     # Batch file for scheduling
├── DEPLOYMENT_INSTRUCTIONS.txt     # Detailed deployment guide
├── README_DEPLOYMENT.md            # Quick deployment reference
├── README.md                       # This file
├── Lithium.url                     # Trading Economics URL
└── logs/                          # Auto-generated log files
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| MySQL connection fails | Check service status: `Get-Service MySQL*` |
| Python not found | Add Python to PATH environment variable |
| Package install fails | Use `python -m pip install -r requirements.txt` |
| No data scraped | Verify internet connection and Trading Economics URL |
| Notifications not sent | Check SMTP settings and app password |

## 📝 Logging

Logs are automatically saved to `logs/` with date stamps:
```
logs/commodities_20251130.log
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Data source: [Trading Economics](https://tradingeconomics.com/commodities)
- Built with: Python, BeautifulSoup4, Pandas, MySQL

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check `DEPLOYMENT_INSTRUCTIONS.txt` for detailed setup help
- Review logs in `logs/` directory

---

**Note**: Remember to keep your MySQL password and SMTP credentials secure. Never commit sensitive configuration to version control.
