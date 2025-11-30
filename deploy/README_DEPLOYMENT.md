# Trading Economics Commodities Scraper - Deployment Package

## 📦 Package Contents

- `commodities_scraper.py` - Main application
- `requirements.txt` - Python dependencies
- `Lithium.url` - Trading Economics URL reference
- `run_commodities_scraper.bat` - Windows batch file for scheduled execution
- `DEPLOYMENT_INSTRUCTIONS.txt` - Detailed deployment guide
- `README_DEPLOYMENT.md` - This file

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MySQL Password
Edit `commodities_scraper.py` line ~953:
```python
'password': 'YOUR_MYSQL_PASSWORD'
```

### 3. Run Script
```bash
python commodities_scraper.py
```

### 4. Schedule Daily at 5 AM
```powershell
# PowerShell (as Administrator)
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "commodities_scraper.py" -WorkingDirectory "C:\DEPLOYMENT\PATH"
$trigger = New-ScheduledTaskTrigger -Daily -At 5:00AM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName "CommoditiesDaily" -Action $action -Trigger $trigger -Settings $settings
```

## 📊 Features

- ✅ Automated daily data scraping from Trading Economics
- ✅ MySQL database storage with historical tracking
- ✅ Price change alerts via Email/SMS
- ✅ Multiple investment timeframe reports (Short/Mid/Long term)
- ✅ Strong leads identification across categories
- ✅ Ranking change tracking day-over-day

## 🗄️ Database

### Auto-Created Tables:
1. **commodities_daily** - All commodity data with full history
2. **strong_leads_daily** - Top performers by day
3. **investment_opportunities_daily** - Investment picks by timeframe

### Database Access:
```sql
mysql -u root -p
USE commodities_db;
SELECT * FROM strong_leads_daily WHERE date = CURDATE() ORDER BY ranking;
```

## 📧 Email/SMS Alerts

### Enable Notifications:
Set `notifications_enabled = True` in commodities_scraper.py

### Configure SMTP:
```python
notification_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',
    'sender_password': 'your_app_password'
}
```

### Add Subscriptions:
```python
subscriptions = [
    Subscription('Lithium', email='your@email.com', min_percent_change=1.0),
    Subscription('Gold', email='your@email.com', min_percent_change=1.0),
]
```

## 📝 Logging

Logs are automatically saved to `logs/` directory with date stamps:
```
logs/commodities_20251130.log
```

## 🔧 System Requirements

- **OS:** Windows 10/11 or Windows Server
- **Python:** 3.8+
- **MySQL:** 5.7+ or 8.0+
- **RAM:** 2GB minimum
- **Storage:** 500MB + growing database

## 📞 Support

For detailed instructions, see `DEPLOYMENT_INSTRUCTIONS.txt`

## 📄 License

MIT License - Free for personal and commercial use
