# Master Refreshing App - Project Structure

```
Master Refreshing App/
│
├── main.py                    # Application entry point
├── ui_main.py                 # Main window UI implementation
├── tray.py                    # System tray integration
├── scheduler.py               # Daily scheduling engine
├── refresher.py               # Excel COM automation engine
├── config_handler.py          # Configuration persistence (JSON)
├── logs_window.py             # Logging panel and file logging
├── file_manager.py            # File list management logic
├── theme.py                   # UI theme and stylesheet generator
│
├── resources/                 # Assets and icons
│   └── icon.png              # System tray icon (placeholder)
│
├── logs/                      # Log files directory (auto-created)
│   └── app.log               # Application log file
│
├── config.json               # User configuration (auto-generated)
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Module Responsibilities

### Core Application
- **main.py**: Bootstrap, initialization, event wiring
- **ui_main.py**: PyQt6 main window and all UI panels

### Business Logic
- **file_manager.py**: Excel file list operations
- **refresher.py**: Excel COM background refresh engine
- **scheduler.py**: Daily scheduling mechanism

### Infrastructure
- **config_handler.py**: JSON configuration persistence
- **logs_window.py**: Logging UI and file output
- **tray.py**: System tray icon and menu
- **theme.py**: Centralized styling and theming

### Resources
- **resources/**: Icons, images, and static assets
