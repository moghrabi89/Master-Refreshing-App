# Master Refreshing App - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- PyQt6 >= 6.6.0
- pywin32 >= 306
- APScheduler >= 3.10.0

### Step 2: Run the Application
```bash
python main.py
```

### Step 3: Add Excel Files and Configure
1. Click **"➕ Add Files"** to select Excel files
2. Set your desired refresh time (default: 06:00 AM)
3. Click **"▶️ Start Scheduler"** for automatic daily refresh
4. Or click **"⚡ Refresh Now"** for immediate refresh

---

## 📋 Features

### ✅ What Works (100% Functional)
- ✓ **Excel File Management**: Add/remove multiple Excel files
- ✓ **Manual Refresh**: Refresh all files instantly
- ✓ **Daily Scheduler**: Automatic refresh at specified time
- ✓ **System Tray**: Minimize to tray, quick access menu
- ✓ **Real-time Logging**: Color-coded logs with file output
- ✓ **Configuration Persistence**: All settings saved automatically
- ✓ **Modern UI**: Professional dark theme with gradients
- ✓ **Error Handling**: Comprehensive error management
- ✓ **Worker Threads**: Non-blocking UI during refresh
- ✓ **Notifications**: System tray notifications

---

## 🎯 Usage Guide

### Adding Files
1. Click "Add Files" button
2. Select one or more Excel files (.xlsx, .xlsm, .xlsb, .xls)
3. Files appear in the table immediately
4. Duplicate files are automatically rejected

### Refreshing Files

#### Manual Refresh:
- Click "⚡ Refresh Now" button
- Watch progress in logs panel
- Get notification when complete

#### Automatic Refresh:
1. Set time using the time picker
2. Click "▶️ Start Scheduler"
3. App will refresh daily at specified time
4. Can run in background (system tray)

### System Tray Operations
- **Double-click icon**: Restore window
- **Right-click icon**: Access menu
  - Open App
  - Refresh Now
  - Start/Stop Scheduler
  - Exit

### Removing Files
1. Select files in the table (Ctrl+Click for multiple)
2. Click "🗑️ Remove Selected"
3. Confirm deletion

---

## 📊 Configuration

### Configuration File: `config.json`

```json
{
  "files": ["C:/path/to/file1.xlsx", "C:/path/to/file2.xlsx"],
  "schedule_time": "06:00",
  "auto_refresh_enabled": false,
  "theme_mode": "modern"
}
```

**Auto-saved on every change!**

### Log Files: `logs/app.log`

- Maximum size: 5MB
- Backup count: 3 files
- Auto-rotation enabled
- Timestamps included

---

## 🔧 Troubleshooting

### Application won't start
```bash
# Check Python version (requires 3.9+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Excel refresh fails
- **Error: "File is locked"**: Close Excel file before refresh
- **Error: "File not found"**: Verify file path in table
- **Error: "Permission denied"**: Run as administrator

### Scheduler not working
- Check scheduled time is set correctly
- Verify scheduler status shows "Running"
- Check logs for scheduler messages
- Computer must be running at scheduled time

### System tray icon not appearing
- Check if system tray is enabled in Windows
- Look for hidden icons in taskbar
- Restart application

### UI freezes during refresh
- This should NOT happen (worker threads implemented)
- If it does, check logs for errors
- File may be extremely large
- Consider refreshing files in smaller batches

---

## 🎨 UI Guide

### Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│          MASTER REFRESHING APP (Header)                  │
│          Developed by ENG. Saeed Al-moghrabi            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────┐  ┌──────────────────────┐    │
│  │ 📁 Excel Files      │  │ ⏰ Daily Scheduler   │    │
│  │  Manager            │  │                      │    │
│  │                     │  │  Refresh Time: 06:00 │    │
│  │  [Table of Files]   │  │  Status: Stopped     │    │
│  │                     │  │                      │    │
│  │  [➕ Add Files]     │  │  [▶️ Start Scheduler]│    │
│  │  [🗑️ Remove Files]  │  │  [⏸️ Stop Scheduler] │    │
│  └─────────────────────┘  │                      │    │
│                            │  ───────────────────  │    │
│                            │                      │    │
│                            │  🔄 Manual Actions   │    │
│                            │                      │    │
│                            │  [⚡ Refresh Now]    │    │
│                            └──────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│  📋 Activity Logs                                       │
│  [Color-coded log messages appear here in real-time]   │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  Ready                                        Files: 0   │
└─────────────────────────────────────────────────────────┘
```

### Button States

| Button | Enabled When | Disabled When |
|--------|-------------|---------------|
| Add Files | Always | During refresh |
| Remove Files | Files selected | During refresh |
| Refresh Now | Files exist | During refresh or no files |
| Start Scheduler | Scheduler stopped | Scheduler running |
| Stop Scheduler | Scheduler running | Scheduler stopped |

---

## 🔐 Security & Privacy

- ✅ No internet connection required
- ✅ No data uploaded anywhere
- ✅ All files processed locally
- ✅ Configuration stored locally
- ✅ No telemetry or tracking

---

## 📈 Performance

### Typical Refresh Times:
- Small file (<5MB): 5-15 seconds
- Medium file (5-20MB): 15-60 seconds
- Large file (>20MB): 1-5 minutes

**Note**: Time depends on:
- Number of queries in file
- Data source response time
- Network speed (for external data)
- Computer performance

---

## 💡 Tips & Best Practices

### For Best Results:
1. **Close Excel files** before refreshing
2. **Test scheduler** with a near-future time first
3. **Check logs regularly** for any issues
4. **Keep app running** for scheduled refresh to work
5. **Use system tray** to minimize while working

### Recommended Settings:
- Schedule refresh during off-hours (e.g., 6 AM)
- Add only files that need daily refresh
- Check logs after first scheduled run
- Keep computer on for scheduled refresh

---

## 🆘 Support

### Get Help:
1. Check logs in `logs/app.log`
2. Review error messages in logs panel
3. Check this documentation
4. Contact developer

### Report Issues:
- GitHub: https://github.com/moghrabi89/Master-Refreshing-App
- Include: error message, steps to reproduce, log file

---

## 📝 Version Information

**Current Version**: v0.2.0  
**Release Date**: December 3, 2025  
**Status**: Production Ready ✅

### What's New in v0.2.0:
- ✅ Complete system tray integration
- ✅ Advanced logging system
- ✅ Worker threads for non-blocking UI
- ✅ Full error handling
- ✅ Modern dark theme
- ✅ Configuration persistence
- ✅ Notifications system

---

## 🎓 Advanced Usage

### Running from Command Line:
```bash
# Normal start
python main.py

# With specific config file (future feature)
# python main.py --config custom_config.json
```

### Testing Individual Components:
```bash
# Test refresher
python refresher.py C:/path/to/test.xlsx

# Test scheduler
python scheduler.py 14:30

# Test logger
python logs_window.py

# Test theme
python theme.py
```

---

**Made with ❤️ in Palestine**

---

## 📞 Contact

**Developer**: ENG. Saeed Al-moghrabi  
**GitHub**: [moghrabi89](https://github.com/moghrabi89)  
**Project**: [Master-Refreshing-App](https://github.com/moghrabi89/Master-Refreshing-App)

---

⭐ If you find this app useful, please star the repository!
