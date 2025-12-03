# Safe Auto-Manifest Activation Guide

## Overview

The application includes a secure auto-manifest generation system that updates the integrity verification baseline **ONLY** when explicitly triggered by a developer. This ensures integrity protection remains active during normal user execution.

---

## 🔒 Safety Guarantees

✅ **DOES NOT** run during normal application startup  
✅ **DOES NOT** activate without explicit developer signals  
✅ **DOES NOT** override manifest if critical files are missing  
✅ **DOES** log warnings for unhashable files  
✅ **DOES** use atomic file writes to prevent corruption  

---

## 🛠️ Developer Triggers

### Method 1: Command-Line Flag (Immediate Generation)

Generate manifest and exit immediately:

```powershell
python main.py --generate-manifest
```

**Output:**
```
Generating integrity manifest...
✓ Manifest generated successfully in 4.3ms
  Location: F:\Master Refreshing App\integrity_manifest.json
```

**Use Case:** Quick manifest regeneration during development

---

### Method 2: .dev_mode File (Auto-Generation on Startup)

Create a trigger file to enable auto-generation:

```powershell
# Create trigger file
New-Item -ItemType File -Name ".dev_mode"

# Launch application (will auto-generate and delete .dev_mode)
python main.py
```

**What Happens:**
1. Application detects `.dev_mode` file on startup
2. Automatically generates new manifest with current file hashes
3. Deletes `.dev_mode` file after successful generation
4. Continues normal startup with updated manifest

**Use Case:** Convenient for testing code changes without manual manifest updates

---

### Method 3: Environment Variable (Session-Based)

Enable auto-manifest for entire PowerShell session:

```powershell
# Set environment variable
$env:APP_DEV_MODE = "1"

# Launch application (will auto-generate on startup)
python main.py
```

**Use Case:** Development sessions where multiple launches need manifest updates

---

### Method 4: --auto-manifest Flag (GUI + Auto-Generate)

Launch application with auto-generation enabled:

```powershell
python main.py --auto-manifest
```

**What Happens:**
1. Sets `APP_DEV_MODE=1` environment variable internally
2. Launches full GUI application
3. Auto-generates manifest during startup if needed
4. Shows log entry: "🔧 Auto-manifest generated successfully"

**Use Case:** Testing GUI with automatic manifest updates

---

### Method 5: Developer UI Button (Interactive)

From within the running application:

1. Open **Tools → Integrity Details**
2. Click **🔧 Auto-Generate Manifest** button
3. Confirm the developer action warning
4. Manifest regenerated instantly

**Use Case:** Manual developer control with visual feedback

---

## 📊 Manifest Metadata

The new manifest format includes comprehensive metadata:

```json
{
  "_metadata": {
    "generated_at": "2025-12-03 14:49:07",
    "generation_mode": "auto",
    "total_files": 11,
    "hashed_files": 11,
    "missing_files": 0,
    "failed_files": 0
  },
  "files": {
    "main.py": "6a52072df8b51dca...",
    "ui_main.py": "6329860bd86b6264...",
    ...
  }
}
```

### Generation Modes:
- **`manual`** - Generated via Developer UI button
- **`auto`** - Generated via `.dev_mode` file or `APP_DEV_MODE` env variable
- **`cli`** - Generated via `--generate-manifest` flag

---

## 🔍 Integrity Details UI

The **Integrity Details** window now displays:

| Field | Description |
|-------|-------------|
| **Last Manifest Generation** | Timestamp of last manifest creation |
| **Generation Mode** | How the manifest was created (Manual/Auto/CLI) |
| **Overall Status** | ✓ Verified / ✗ Modified / ⚠ Missing Files |
| **Total Files Monitored** | Number of critical files |
| **✓ Matched** | Files with matching hashes |
| **✗ Modified** | Files with changed hashes |
| **⚠ Missing** | Files not found on disk |
| **Verification Time** | How long integrity check took (ms) |

---

## 🧪 Testing All Triggers

### Test 1: CLI Generation
```powershell
python main.py --generate-manifest
# Expected: Manifest generated in ~4ms, application exits
```

### Test 2: .dev_mode File Trigger
```powershell
New-Item -ItemType File -Name ".dev_mode"
python -c "from integrity_checker import IntegrityChecker; checker = IntegrityChecker(); was_gen, elapsed = checker.auto_generate_if_triggered(); print('Generated:', was_gen, '| Time:', elapsed, 'ms'); print('File exists after:', checker._check_dev_mode_file())"
# Expected: Generated: True | Time: ~4 ms | File exists after: False
```

### Test 3: Environment Variable Trigger
```powershell
$env:APP_DEV_MODE = "1"
python -c "from integrity_checker import IntegrityChecker; checker = IntegrityChecker(); was_gen, elapsed = checker.auto_generate_if_triggered(); print('Generated:', was_gen)"
# Expected: Generated: True
```

### Test 4: Metadata Verification
```powershell
python -c "from integrity_checker import IntegrityChecker; checker = IntegrityChecker(); metadata = checker.get_manifest_metadata(); print('Generated at:', metadata['generated_at']); print('Mode:', metadata['generation_mode']); print('Files:', metadata['total_files'])"
# Expected: Shows current timestamp, generation mode, and file count
```

### Test 5: Integrity Verification After Auto-Manifest
```powershell
$env:APP_DEV_MODE = "1"
python -c "from integrity_checker import IntegrityChecker; checker = IntegrityChecker(); checker.auto_generate_if_triggered(); result = checker.verify_integrity(); print('Status:', checker.get_status_text())"
# Expected: Status: Verified
```

---

## 🚨 Safety Validation

### Test: Normal User Startup (No Auto-Manifest)
```powershell
# Remove all triggers
Remove-Item ".dev_mode" -ErrorAction SilentlyContinue
Remove-Item Env:\APP_DEV_MODE -ErrorAction SilentlyContinue

# Launch normally
python -c "from integrity_checker import IntegrityChecker; checker = IntegrityChecker(); print('Should auto-generate:', checker.should_auto_generate())"
# Expected: Should auto-generate: False
```

### Test: Missing Files Safety
```powershell
# Temporarily rename a file
Rename-Item "theme.py" "theme.py.backup"

# Try to generate manifest
python main.py --generate-manifest
# Expected: Warning logged, manifest still generated for available files

# Restore file
Rename-Item "theme.py.backup" "theme.py"
```

---

## 📝 Developer Workflow Examples

### Scenario 1: Code Modification Session
```powershell
# Start development session
$env:APP_DEV_MODE = "1"

# Make code changes to main.py
# Edit main.py...

# Launch app - manifest auto-updates
python main.py

# Continue development...
# Edit ui_main.py...

# Launch again - manifest auto-updates again
python main.py
```

### Scenario 2: Quick Fix and Test
```powershell
# Fix a bug in refresher.py
# Edit refresher.py...

# Create trigger for one-time auto-update
New-Item -ItemType File -Name ".dev_mode"

# Test the fix - manifest updates automatically
python main.py

# .dev_mode file auto-deleted, safe for normal use
```

### Scenario 3: Build/Deployment Preparation
```powershell
# Final manifest generation before commit
python main.py --generate-manifest

# Verify all files included
python -c "from integrity_checker import IntegrityChecker; checker = IntegrityChecker(); metadata = checker.get_manifest_metadata(); print('Total files:', metadata['total_files'])"

# Commit to repository
git add integrity_manifest.json
git commit -m "Update integrity manifest"
```

---

## 🎯 Summary

**For Developers (المطور):**
- Use `.dev_mode` file for convenient auto-updates during development
- Use `--generate-manifest` for explicit manifest creation
- Use `APP_DEV_MODE=1` for session-based auto-updates
- Use UI button for interactive control

**For Users (المستخدم):**
- No action needed
- Integrity protection always active
- No performance impact
- No security compromise

**Safety Model:**
✅ Requires explicit developer trigger  
✅ No automatic updates during normal use  
✅ Atomic file writes prevent corruption  
✅ Missing file detection prevents partial manifests  
✅ Auto-cleanup of trigger files  

---

## 🔗 Related Files

- `integrity_checker.py` - Core auto-manifest logic
- `main.py` - Command-line flag handling
- `integrity_ui.py` - Developer UI controls
- `integrity_manifest.json` - Generated manifest with metadata
- `.dev_mode` - Optional trigger file (auto-deleted after use)

---

**Version:** 1.0.0  
**Last Updated:** 2025-12-03  
**Author:** ENG. Saeed Al-moghrabi
