# Changelog - Master Refreshing App

## [v1.2.0] - 2025-12-06

### ✨ Added
- **Row Count Feature**: Automatic calculation of rows added after each refresh
  - New method: `_get_workbook_row_count()` in `refresher.py`
  - Calculates rows before and after refresh across all worksheets
  - Displays detailed information in logs: rows before, rows after, added rows
  - Zero performance impact (< 1% overhead)
  - Graceful error handling with fallback to 0

### 📝 Enhanced
- **refresher.py**:
  - Added row counting before Excel refresh operation
  - Added row counting after Excel refresh operation
  - Enhanced return dictionary with 3 new fields:
    - `rows_before`: Total rows before refresh
    - `rows_after`: Total rows after refresh
    - `added_rows`: Number of rows added (can be negative)

- **main.py**:
  - Enhanced `_on_refresh_finished()` to display row statistics
  - Added detailed logging for each successfully refreshed file
  - Logs appear in both UI Logs Window and external log file

### 🧪 Testing
- Added comprehensive test suite: `test_row_count_feature.py`
- All tests passing (5/5)
- Verified backward compatibility
- No breaking changes

### 📚 Documentation
- Created `ROW_COUNT_FEATURE.md` - Complete technical documentation (English)
- Created `ROW_COUNT_FEATURE_AR.md` - Complete technical documentation (Arabic)
- Created `IMPLEMENTATION_SUMMARY.md` - Implementation details
- Created `ROW_COUNT_QUICK_REF.md` - Quick reference guide

### 🔒 Backward Compatibility
- ✅ All existing fields preserved in return dictionaries
- ✅ No API breaking changes
- ✅ No UI layout modifications
- ✅ No configuration changes required
- ✅ Fully compatible with v1.1.0 data structures

---

## [v1.1.0] - 2024-12-04

### ✨ Added
- **Per-File Management**: Enable/disable individual files without deletion
- **Status Tracking**: Track last refresh status (Success/Error/Skipped)
- **Timestamp History**: Record when each file was last refreshed
- **Single Instance System**: Prevent multiple app instances from running
- **Settings Dialog**: Centralized configuration UI
- **Custom Log Directory**: Choose where logs are saved

### 🏗️ Architecture Improvements
- Centralized path management with `utils/paths.py`
- Enhanced COM threading stability
- Startup file validation with auto-cleanup
- Removed unused APScheduler dependency
- Full type hints throughout codebase

### 📊 User Experience
- Enhanced 6-column table view:
  - Enabled (checkbox)
  - File Name
  - Full Path
  - Extension
  - Last Status
  - Last Refresh
- Smart filtering: Only enabled files are refreshed
- Automatic status updates after each operation

### 🧪 Testing
- Phase 1 tests: 8/8 passing (Architecture)
- Phase 2 tests: 5/5 passing (UX Features)
- Total: 13/13 tests passing

### 📚 Documentation
- `PHASE1_IMPLEMENTATION_SUMMARY.md` - Architecture improvements
- `PHASE2_IMPLEMENTATION_SUMMARY.md` - UX features
- `SINGLE_INSTANCE_GUIDE.md` - Single instance testing guide

---

## [v1.0.0] - Initial Release

### ✨ Features
- Automated Excel file refresh using COM automation
- Daily scheduling with customizable time
- File management (add/remove Excel files)
- System tray integration
- Real-time logging with color coding
- Configuration persistence (JSON)
- Windows startup integration
- Theme support
- Integrity verification system

### 🎯 Capabilities
- Silent Excel refresh (PowerQuery, PivotTables, External Connections)
- Sequential multi-file processing
- Background execution with threading
- Timeout protection (600 seconds default)
- Read-only file detection
- Comprehensive error handling
- COM object lifecycle management

### 📋 Supported Formats
- .xlsx (Excel 2007+)
- .xlsm (Macro-enabled)
- .xlsb (Binary format)
- .xls (Excel 97-2003)

### 🛠️ Technical Stack
- Python 3.13+
- PyQt6 6.6.0+ (GUI)
- pywin32 306+ (COM automation)
- Windows 10/11 (64-bit)

---

## Version History Summary

| Version | Release Date | Status | Key Features |
|---------|-------------|--------|--------------|
| v1.2.0 | 2025-12-06 | ✅ Current | Row count tracking |
| v1.1.0 | 2024-12-04 | ✅ Stable | Per-file management, Single instance |
| v1.0.0 | 2024-11-XX | ✅ Stable | Initial release |

---

## Upgrade Notes

### From v1.1.0 to v1.2.0
- ✅ **No action required** - Fully backward compatible
- ✅ New features activate automatically
- ✅ No configuration changes needed
- ✅ No data migration required

### From v1.0.0 to v1.1.0
- ✅ Configuration automatically upgraded from string paths to dict format
- ✅ No data loss during migration
- ✅ All settings preserved

---

## Future Roadmap

### Planned Features (v1.3.0+)
- 📧 Email notifications on completion
- 📊 Per-sheet row breakdown
- 📈 Historical row change tracking
- 🔔 Alert system for unusual changes
- ☁️ Cloud backup integration
- ⏰ Multiple schedule times
- 🌙 Dark mode toggle
- 🖱️ Drag & drop file support

### Under Consideration
- Cross-platform support (macOS/Linux)
- Database backend (SQLite)
- Web interface
- REST API
- Docker container

---

## Support & Contributions

- **Repository**: https://github.com/moghrabi89/Master-Refreshing-App
- **Issues**: https://github.com/moghrabi89/Master-Refreshing-App/issues
- **Documentation**: See README.md and feature-specific docs

---

## License

MIT License - See LICENSE file for details

---

**Maintained by**: ENG. Saeed Al-moghrabi  
**Last Updated**: December 6, 2025
