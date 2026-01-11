# Master Refreshing App

<div align="center">

![Version](https://img.shields.io/badge/version-1.3.3-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**أداة احترافية لتحديث ملفات Excel تلقائياً بشكل يومي مع إدارة متقدمة وتتبع البيانات**

**Professional Desktop Application for Automated Daily Excel File Refresh with Advanced Management and Data Tracking**

</div>

---

## 📋 نظرة عامة | Overview

**Master Refreshing App** هو تطبيق سطح مكتب متطور مبني بلغة Python باستخدام PyQt6، مصمم لأتمتة عملية تحديث ملفات Excel التي تحتوي على اتصالات بيانات خارجية، PowerQuery، وجداول محورية. يعمل التطبيق بصمت في الخلفية وينفذ التحديثات المجدولة دون أي تدخل يدوي. النسخة 1.3.3 تضيف تحسينات هامة على الاستقرار، بما في ذلك "فترة سماح" للجدولة وحماية من الإغلاق العرضي.

**Master Refreshing App** is an advanced Python desktop application built with PyQt6, designed to automate the refresh process for Excel files containing external data connections, PowerQuery, and PivotTables. The application runs silently in the background and executes scheduled updates without manual intervention. Version 1.3.3 adds critical stability improvements, including a "grace period" for scheduling and protection against accidental closure.

---

## ✨ المميزات | Features

### 🔄 التحديث التلقائي | Automated Refresh
- تحديث تلقائي صامت لملفات Excel باستخدام COM automation
- **عملية التحديث تتم بالكامل في الذاكرة - لا يظهر Excel في الواجهة** **جديد v1.3.2**
- دعم PowerQuery، PivotTables، والاتصالات الخارجية
- معالجة متعددة للملفات بشكل متسلسل
- تتبع حالة كل ملف (نجاح/خطأ/متخطى)
- **تتبع عدد الصفوف قبل وبعد التحديث** **جديد v1.2.0**
- **زر "Stop All Operations" لإيقاف العمليات الجارية** **جديد v1.3.2**
- Silent Excel refresh using COM automation
- **Memory-only refresh operations - Excel never appears in UI** **NEW v1.3.2**
- Support for PowerQuery, PivotTables, and external connections
- Sequential multi-file processing
- Track status of each file (Success/Error/Skipped)
- **Row count tracking before and after refresh** **NEW v1.2.0**
- **"Stop All Operations" button to gracefully stop running operations** **NEW v1.3.2**

### 📅 الجدولة اليومية | Daily Scheduling
- جدولة تحديث يومية في وقت محدد قابل للتخصيص
- تحديث ديناميكي للوقت بدون إعادة تشغيل
- تشغيل في الخلفية حتى عند تصغير التطبيق
- **زر "Create Startup Setting" لإعداد بدء التشغيل التلقائي** **جديد v1.3.2**
- **التطبيق يبقى في الذاكرة حتى بعد إعادة تشغيل Windows** **جديد v1.3.2**
- Daily refresh scheduling at customizable time
- Dynamic time updates without restart
- Background execution even when minimized
- **"Create Startup Setting" button for automatic Windows startup** **NEW v1.3.2**
- **Application persists in memory even after Windows restart** **NEW v1.3.2**

### 🎯 إدارة متقدمة للملفات | Advanced File Management
- إضافة وإزالة ملفات Excel بسهولة
- **تفعيل/تعطيل ملفات فردية بدون حذف**
- **تتبع تاريخ آخر تحديث لكل ملف**
- **عرض حالة آخر عملية تحديث**
- **مراقبة نمو البيانات من خلال عدد الصفوف** **جديد v1.2.0**
- دعم جميع صيغ Excel (.xlsx, .xlsm, .xlsb, .xls)
- التحقق من صحة الملفات تلقائياً
- منع التكرار
- Easy add/remove Excel files
- **Enable/disable individual files without deletion**
- **Track last refresh time for each file**
- **Display last operation status**
- **Monitor data growth through row counting** **NEW v1.2.0**
- Support for all Excel formats
- Automatic file validation
- Duplicate prevention

### 🔒 نظام نسخة واحدة | Single Instance System
- **منع تشغيل نسخ متعددة من التطبيق** **جديد v1.1.0**
- **تفعيل النافذة تلقائياً عند محاولة تشغيل نسخة ثانية** **جديد v1.1.0**
- **يعمل حتى مع النافذة المخفية في System Tray** **جديد v1.1.0**
- **Prevent running multiple instances** **NEW v1.1.0**
- **Auto-activate window when trying to launch second instance** **NEW v1.1.0**
- **Works even with window hidden in System Tray** **NEW v1.1.0**

### ⚙️ إعدادات قابلة للتخصيص | Customizable Settings
- **إعدادات مركزية لمسار السجلات** **جديد v1.1.0**
- **قائمة إعدادات منظمة في شريط القوائم** **جديد v1.1.0**
- حفظ تلقائي لجميع التغييرات
- **Centralized settings for log directory** **NEW v1.1.0**
- **Organized settings menu in menu bar** **NEW v1.1.0**
- Auto-save all changes

### 🌐 تكامل مع System Tray
- التشغيل الصامت في خلفية النظام
- قائمة سريعة من System Tray
- إشعارات عند اكتمال التحديث
- Silent background operation
- Quick access tray menu
- Refresh completion notifications

### 📊 السجلات المباشرة | Real-Time Logging
- عرض السجلات بشكل مباشر مع ترميز بالألوان
- حفظ السجلات في ملف خارجي
- تتبع مفصل لكل عملية
- Real-time color-coded log display
- External log file storage
- Detailed operation tracking

### 💾 إعدادات دائمة | Persistent Configuration
- حفظ تلقائي لجميع الإعدادات
- استعادة حالة التطبيق عند إعادة التشغيل
- تخزين آمن بصيغة JSON
- Auto-save all settings
- State restoration on restart
- Secure JSON storage

### 🎨 واجهة مستخدم عصرية | Modern UI
- تصميم احترافي مع ألوان متدرجة
- زوايا مستديرة وتأثيرات سلسة
- **نظام ثيمات مزدوج (Dark Mode / Light Mode)** **جديد v1.3.2**
- **تبديل سريع بين الثيمات من قائمة File** **جديد v1.3.2**
- سهولة الاستخدام للمستخدمين غير التقنيين
- Professional design with gradients
- Rounded corners and smooth effects
- **Dual theme system (Dark Mode / Light Mode)** **NEW v1.3.2**
- **Quick theme toggle from File menu** **NEW v1.3.2**
- User-friendly for non-technical users

---

## 🖥️ متطلبات النظام | System Requirements

### الأساسيات | Essentials
- **نظام التشغيل | OS**: Windows 10/11 (64-bit)
- **Microsoft Excel**: 2016 أو أحدث | 2016 or later *(مطلوب | Required)*
- **Python**: 3.9 أو أحدث | 3.9 or later

### المكتبات المطلوبة | Dependencies
```
PyQt6 >= 6.6.0
pywin32 >= 306
```

---

## 🚀 التثبيت والتشغيل | Installation & Usage

### 1. استنساخ المشروع | Clone Repository
```bash
git clone https://github.com/moghrabi89/Master-Refreshing-App.git
cd "Master Refreshing App"
```

### 2. تثبيت المتطلبات | Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. تشغيل التطبيق | Run Application
```bash
python main.py
```

---

## 📖 دليل الاستخدام | User Guide

### إضافة ملفات Excel | Adding Excel Files
1. انقر على زر **"➕ Add Files"**
2. اختر ملفات Excel المطلوب تحديثها
3. ستظهر الملفات في الجدول مع التفاصيل
4. Click **"➕ Add Files"** button
5. Select Excel files to refresh
6. Files will appear in table with details

### جدولة التحديث | Scheduling Refresh
1. اختر وقت التحديث اليومي من خانة **"Refresh Time"**
2. انقر **"▶️ Start Scheduler"** لتفعيل الجدولة
3. سيعمل التطبيق تلقائياً في الوقت المحدد
4. Select daily refresh time from **"Refresh Time"**
5. Click **"▶️ Start Scheduler"** to activate
6. App will run automatically at scheduled time

### التحديث اليدوي | Manual Refresh
- انقر على **"⚡ Refresh Now"** لتحديث فوري لجميع الملفات
- Click **"⚡ Refresh Now"** for immediate refresh of all files

### العمل في الخلفية | Background Operation
- قلل التطبيق إلى System Tray للعمل في الخلفية
- استخدم القائمة السريعة من الأيقونة
- Minimize to System Tray for background operation
- Use quick menu from tray icon

---

## 🏗️ البنية المعمارية | Architecture

### وحدات المشروع | Project Modules

```
Master Refreshing App/
├── main.py                      # نقطة البداية | Entry point
├── ui_main.py                  # الواجهة الرسومية | UI implementation
├── config_handler.py           # إدارة الإعدادات | Configuration manager
├── file_manager.py             # إدارة الملفات | File management
├── refresher.py                # محرك التحديث | Refresh engine
├── scheduler.py                # نظام الجدولة | Scheduling system
├── tray.py                     # تكامل System Tray | Tray integration
├── logs_window.py              # نظام السجلات | Logging system
├── theme.py                    # نظام الألوان | Theme manager
├── single_instance.py          # نظام النسخة الواحدة | Single instance [NEW v1.1.0]
├── settings_dialog.py          # حوار الإعدادات | Settings dialog [NEW v1.1.0]
├── integrity_checker.py        # فحص السلامة | Integrity checker
├── integrity_ui.py             # واجهة السلامة | Integrity UI
├── startup_manager.py          # إدارة بدء التشغيل | Startup manager
├── utils/                      # أدوات مساعدة | Utilities [NEW v1.1.0]
│   ├── __init__.py
│   └── paths.py               # إدارة المسارات | Path management
├── resources/                  # الموارد | Resources
└── logs/                       # ملفات السجلات | Log files
```

### التقنيات المستخدمة | Technologies

- **واجهة المستخدم | UI**: PyQt6
- **أتمتة Excel | Excel Automation**: win32com (pywin32)
- **الجدولة | Scheduling**: APScheduler
- **التخزين | Storage**: JSON
- **الخيوط | Threading**: Python threading

---

## 📝 الإعدادات | Configuration

يتم حفظ الإعدادات تلقائياً في ملف `config.json`:

Settings are automatically saved in `config.json`:

```json
{
  "files": ["C:/path/to/file1.xlsx", "C:/path/to/file2.xlsm"],
  "schedule_time": "06:00",
  "auto_refresh_enabled": false,
  "theme_mode": "modern"
}
```

---

## 📊 السجلات | Logging

### عرض مباشر في الواجهة | Real-time UI Display
- سجلات ملونة حسب الحالة (نجاح/خطأ/معلومات)
- Color-coded logs by status (success/error/info)

### ملف خارجي | External File
- المسار: `logs/app.log`
- حد أقصى: 5 ميجابايت
- نسخ احتياطية: 3 ملفات
- Path: `logs/app.log`
- Max size: 5MB
- Backups: 3 files

---

## 🔒 الأمان | Security

- ✅ لا توجد اتصالات شبكية خارجية | No external network connections
- ✅ جميع البيانات محلية | All data stored locally
- ✅ لا يتم رفع أو نقل بيانات | No data upload or transmission
- ✅ صلاحيات مستخدم عادية | Standard user privileges

---

## 🛠️ التطوير | Development

### حالة المشروع | Project Status
- ✅ **v0.1.0**: البنية الأساسية والوحدات الرئيسية | Core structure and main modules
- ✅ **v0.2.0**: تكامل كامل للواجهة والنظام | Full UI and system integration
- ✅ **v1.0.0**: إصدار الإنتاج - نظام حماية السلامة | Production Release - Integrity protection system
- ✅ **v1.1.0**: إدارة متقدمة - تتبع الحالة، تفعيل/تعطيل الملفات، نظام نسخة واحدة | Advanced Management - Status tracking, file enable/disable, single instance
- ✅ **v1.2.0**: تتبع عدد الصفوف - مراقبة نمو البيانات | Row count tracking - Data growth monitoring
- ✅ **v1.3.2**: نظام ثيمات مزدوج، تحديث محسّن في الذاكرة، إدارة بدء التشغيل | Dual theme system, memory-only refresh, startup management
- 📋 **المخطط | Planned**: ميزات إضافية وتحسينات | Additional features and improvements

### المساهمة | Contributing
نرحب بالمساهمات! الرجاء:
1. عمل Fork للمشروع
2. إنشاء فرع للميزة الجديدة
3. Commit التغييرات
4. Push إلى الفرع
5. فتح Pull Request

Contributions welcome! Please:
1. Fork the project
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📞 التواصل | Contact

**المطور | Developer**: ENG. Saeed Al-moghrabi

**GitHub**: [moghrabi89](https://github.com/moghrabi89)

**المشروع | Project**: [Master-Refreshing-App](https://github.com/moghrabi89/Master-Refreshing-App)

---

## 📄 الترخيص | License

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 شكر وتقدير | Acknowledgments

- **PyQt6** - إطار العمل الرسومي | GUI framework
- **pywin32** - تكامل COM مع Windows | Windows COM integration
- **APScheduler** - نظام الجدولة | Scheduling system

---

<div align="center">

**صنع بـ ❤️ في الاردن | Made with ❤️ in jordan**

⭐ إذا أعجبك المشروع، لا تنسى النجمة! | Star this repo if you find it useful!

</div>
