# 🚀 Quick Build Guide

**Fast-track instructions to build Master Refreshing App executable**

---

## ⚡ Quick Start (2 minutes)

### Option 1: PyInstaller (Recommended)

```cmd
cd "f:\Master Refreshing App"
build_exe.bat
```

**Result:** `dist\MasterRefreshingApp.exe` (ready in 2-5 minutes)

---

### Option 2: Nuitka (Lowest AV Detection)

```cmd
cd "f:\Master Refreshing App"
build_exe_nuitka.bat
```

**Result:** `dist\MasterRefreshingApp.exe` (ready in 5-15 minutes)

---

## 📋 Prerequisites

Install required packages:

```bash
pip install pyinstaller pywin32
```

For Nuitka (optional):
```bash
pip install nuitka ordered-set
```

---

## ✅ Verify Build

```bash
python verify_build.py
```

---

## 📚 Full Documentation

See **BUILD_DOCUMENTATION.md** for:
- Digital signing instructions
- Antivirus optimization tips
- Distribution guidelines
- Troubleshooting

---

## 🎯 Build Outputs

| File | Description |
|------|-------------|
| `dist\MasterRefreshingApp.exe` | Main executable |
| `dist\SHA256SUMS.txt` | Hash for verification |
| `build\` | Build artifacts (can be deleted) |

---

## 🔐 Recommended: Add Digital Signature

```cmd
signtool sign /a /tr http://timestamp.digicert.com /td sha256 /fd sha256 dist\MasterRefreshingApp.exe
```

*(Requires code signing certificate - reduces AV false positives by 70-90%)*

---

## 📞 Support

Issues? See [BUILD_DOCUMENTATION.md](BUILD_DOCUMENTATION.md) or open an issue on GitHub.

---

**Master Refreshing App v1.0.0** | Made with ❤️ in Palestine 🇵🇸
