# Master Refreshing App

<div align="center">

![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**أداة احترافية لتحديث ملفات Excel تلقائياً بشكل يومي**

**Professional Desktop Application for Automated Daily Excel File Refresh**

</div>

---

## 📋 نظرة عامة | Overview

**Master Refreshing App** هو تطبيق سطح مكتب متطور مبني بلغة Python باستخدام PyQt6، مصمم لأتمتة عملية تحديث ملفات Excel التي تحتوي على اتصالات بيانات خارجية، PowerQuery، وجداول محورية. يعمل التطبيق بصمت في الخلفية وينفذ التحديثات المجدولة دون أي تدخل يدوي.

**Master Refreshing App** is an advanced Python desktop application built with PyQt6, designed to automate the refresh process for Excel files containing external data connections, PowerQuery, and PivotTables. The application runs silently in the background and executes scheduled updates without manual intervention.

---

## ✨ المميزات | Features

### 🔄 التحديث التلقائي | Automated Refresh
- تحديث تلقائي صامت لملفات Excel باستخدام COM automation
- دعم PowerQuery، PivotTables، والاتصالات الخارجية
- معالجة متعددة للملفات بشكل متسلسل
- Silent Excel refresh using COM automation
- Support for PowerQuery, PivotTables, and external connections
- Sequential multi-file processing

### 📅 الجدولة اليومية | Daily Scheduling
- جدولة تحديث يومية في وقت محدد قابل للتخصيص
- تحديث ديناميكي للوقت بدون إعادة تشغيل
- تشغيل في الخلفية حتى عند تصغير التطبيق
- Daily refresh scheduling at customizable time
- Dynamic time updates without restart
- Background execution even when minimized

### 🎯 إدارة متقدمة للملفات | Advanced File Management
- إضافة وإزالة ملفات Excel بسهولة
- دعم جميع صيغ Excel (.xlsx, .xlsm, .xlsb, .xls)
- التحقق من صحة الملفات تلقائياً
- منع التكرار
- Easy add/remove Excel files
- Support for all Excel formats
- Automatic file validation
- Duplicate prevention

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
- سهولة الاستخدام للمستخدمين غير التقنيين
- Professional design with gradients
- Rounded corners and smooth effects
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
APScheduler >= 3.10.0
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
├── main.py                 # نقطة البداية | Entry point
├── ui_main.py             # الواجهة الرسومية | UI implementation
├── config_handler.py      # إدارة الإعدادات | Configuration manager
├── file_manager.py        # إدارة الملفات | File management
├── refresher.py           # محرك التحديث | Refresh engine
├── scheduler.py           # نظام الجدولة | Scheduling system
├── tray.py               # تكامل System Tray | Tray integration
├── logs_window.py        # نظام السجلات | Logging system
├── theme.py              # نظام الألوان | Theme manager
├── resources/            # الموارد | Resources
└── logs/                 # ملفات السجلات | Log files
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

**صنع بـ ❤️ في فلسطين | Made with ❤️ in Palestine**

⭐ إذا أعجبك المشروع، لا تنسى النجمة! | Star this repo if you find it useful!

</div>
