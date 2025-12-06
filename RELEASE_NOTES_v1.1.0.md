# 🎉 Master Refreshing App v1.1.0

## 🎯 Major Features

### Per-File Management
- ✅ **Enable/Disable Toggle**: Control individual files without deletion
- ✅ **Status Tracking**: View last refresh status (Success/Error/Skipped)  
- ✅ **Timestamp History**: Track when each file was last refreshed
- ✅ **6-Column Table**: Enhanced view with all metadata

### Single Instance System
- ✅ **Prevent Duplicates**: Only one app instance can run
- ✅ **Auto-Activate**: Window comes to front on second launch
- ✅ **Tray Support**: Works even with window hidden in system tray
- ✅ **Crash Recovery**: Automatic stale server cleanup

### Settings & Configuration  
- ✅ **Settings Dialog**: Centralized configuration UI
- ✅ **Custom Log Directory**: Choose where logs are saved
- ✅ **Menu Bar**: Organized File and Tools menus

---

## 🏗️ Architecture Improvements (Phase 1)

- ✅ **Centralized Paths**: New utils/paths.py for PyInstaller compatibility
- ✅ **COM Threading**: pythoncom stability for Excel automation
- ✅ **Startup Validation**: Auto-cleanup of missing files
- ✅ **Dependency Cleanup**: Removed unused APScheduler
- ✅ **Type Safety**: Full type hints throughout codebase

---

## 📊 User Experience (Phase 2)

### Enhanced Table View
| Enabled | File Name | Full Path | Extension | Last Status | Last Refresh |
|---------|-----------|-----------|-----------|-------------|--------------|
| ☑️ | report.xlsx | C:\...\report.xlsx | .xlsx | Success | 2024-12-04 10:30 |
| ☐ | backup.xlsm | C:\...\backup.xlsm | .xlsm | Never Run | Never |

### Smart Filtering
- Only **enabled** files are processed during refresh
- Disabled files remain in list but are skipped
- Status updates automatically after each operation

### Backward Compatibility
- Old config format (string paths) automatically upgraded
- No data loss during migration
- Seamless transition from v1.0.0

---

## 🔧 Technical Details

### New Files
- `single_instance.py` - Single instance manager
- `settings_dialog.py` - Settings UI dialog
- `utils/paths.py` - Centralized path management
- `resources/icon.ico` - Application icon

### Modified Files  
- `main.py` - Single instance integration
- `config_handler.py` - Metadata support
- `file_manager.py` - Enable/disable logic
- `ui_main.py` - 6-column table
- `logs_window.py` - Custom log directory

### Data Model
**Old Format:**
```json
{"files": ["C:\\file1.xlsx", "C:\\file2.xlsx"]}
```

**New Format:**
```json
{
  "files": [
    {"path": "C:\\file1.xlsx", "enabled": true, "last_status": "Success", "last_run": "2024-12-04T10:30:00"},
    {"path": "C:\\file2.xlsx", "enabled": false, "last_status": null, "last_run": null}
  ],
  "log_directory": "C:\\CustomLogs"
}
```

---

## 🧪 Testing

### Test Coverage
- ✅ **Phase 1 Tests**: 8/8 passing (Architecture)
- ✅ **Phase 2 Tests**: 5/5 passing (UX Features)
- ✅ **Total**: 13/13 tests passing

### Verified Scenarios
- ✅ Enable/disable persistence
- ✅ Status updates after refresh
- ✅ Single instance detection
- ✅ Window activation from tray
- ✅ Backward compatibility
- ✅ Log directory configuration
- ✅ Crash recovery

---

## 📚 Documentation

Three comprehensive guides included:
1. **PHASE1_IMPLEMENTATION_SUMMARY.md** - Architecture improvements
2. **PHASE2_IMPLEMENTATION_SUMMARY.md** - UX features  
3. **SINGLE_INSTANCE_GUIDE.md** - Single instance testing

---

## 🚀 Installation

```bash
git clone https://github.com/moghrabi89/Master-Refreshing-App.git
cd Master-Refreshing-App
pip install -r requirements.txt
python main.py
```

---

## 📋 Requirements

- Windows 10/11 (64-bit)
- Python 3.13+
- Microsoft Excel 2016+
- PyQt6 >= 6.6.0
- pywin32 >= 306

---

## 🎬 What's Next?

Stay tuned for future releases with:
- Email notifications on completion
- Multiple schedule times
- Cloud backup integration
- Custom refresh scripts

---

## 🙏 Acknowledgments

Built with ❤️ using:
- **PyQt6** - Modern GUI framework
- **pywin32** - Windows COM automation
- **Qt Network** - Single instance IPC

---

**Full Changelog**: https://github.com/moghrabi89/Master-Refreshing-App/compare/v1.0.0...v1.1.0

**صنع بـ ❤️ في فلسطين | Made with ❤️ in Palestine**
