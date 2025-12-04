"""
integrity_checker.py - Application Self-Verification System

Purpose:
    Lightweight, secure, and non-intrusive integrity verification system.
    Detects tampering or modifications to critical application files using
    SHA-256 hash verification. Operates entirely locally with zero network access.
    
    Features:
    - SHA-256 hash generation for all critical files
    - Runtime verification on application startup
    - Manifest-based integrity checking
    - Non-blocking detection (logs only, no exit)
    - Millisecond-level performance (< 100ms)
    - No antivirus false positives
    - Zero impact on application operations
    
    Security Model:
    - Detection only (no modification/deletion)
    - Pure Python standard library (hashlib, json, os)
    - No system hooks or PowerShell usage
    - Tamper detection without blocking

Author: ENG. Saeed Al-moghrabi
Version: 1.0.0 - Production Ready
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Tuple, Optional, Callable, Any
from pathlib import Path
from utils.paths import get_app_root


class IntegrityChecker:
    """
    Application integrity verification system.
    
    This class provides fast, lightweight integrity checking for critical
    application files using SHA-256 hashing. Designed to detect tampering
    without impacting performance or triggering false positives.
    """
    
    # Critical files to monitor (relative to application root)
    CRITICAL_FILES = [
        "main.py",
        "ui_main.py",
        "refresher.py",
        "scheduler.py",
        "tray.py",
        "config_handler.py",
        "file_manager.py",
        "logs_window.py",
        "theme.py",
        "startup_manager.py",
        "integrity_checker.py"
    ]
    
    # Manifest file name
    MANIFEST_FILE = "integrity_manifest.json"
    
    # Developer mode trigger file
    DEV_MODE_FILE = ".dev_mode"
    
    def __init__(self, 
                 app_root: Optional[str] = None,
                 log_callback: Optional[Callable[[str, str], None]] = None):
        """
        Initialize the integrity checker.
        
        Args:
            app_root: Root directory of the application (default: uses get_app_root())
            log_callback: Optional callback function(message, level) for logging
        """
        # Use centralized path resolution
        if app_root is not None:
            self.app_root = Path(app_root)
        else:
            self.app_root = get_app_root()
        
        self.log_callback = log_callback
        self.manifest_path = self.app_root / self.MANIFEST_FILE
        
        # Verification results
        self.is_verified = False
        self.is_tampered = False
        self.modified_files: List[str] = []
        self.missing_files: List[str] = []
        self.verification_time_ms = 0.0
        self.manifest_data: Optional[Dict] = None
    
    def _check_dev_mode_file(self) -> bool:
        """Check if developer mode trigger file exists."""
        dev_file = self.app_root / self.DEV_MODE_FILE
        return dev_file.exists()
    
    def _delete_dev_mode_file(self) -> bool:
        """
        Delete developer mode trigger file.
        
        Returns:
            bool: True if deleted successfully or file doesn't exist
        """
        try:
            dev_file = self.app_root / self.DEV_MODE_FILE
            if dev_file.exists():
                dev_file.unlink()
                self._log("Developer mode file removed", "DEBUG")
            return True
        except Exception as e:
            self._log(f"Failed to remove developer mode file: {e}", "WARNING")
            return False
    
    def _check_auto_manifest_env(self) -> bool:
        """Check if auto-manifest environment variable is set."""
        return os.environ.get("APP_DEV_MODE", "").lower() in ["1", "true", "yes"]
    
    def should_auto_generate(self) -> bool:
        """
        Check if auto-manifest generation should be triggered.
        
        Returns:
            bool: True if any developer trigger is active
        """
        return self._check_dev_mode_file() or self._check_auto_manifest_env()
    
    def _log(self, message: str, level: str = "INFO"):
        """
        Internal logging method.
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        if self.log_callback:
            self.log_callback(message, level)
    
    def _compute_file_hash(self, file_path: Path) -> Optional[str]:
        """
        Compute SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            str: SHA-256 hex digest, or None if file cannot be read
        """
        try:
            sha256_hash = hashlib.sha256()
            
            # Read file in chunks for memory efficiency
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            return sha256_hash.hexdigest()
        
        except Exception as e:
            self._log(f"Failed to compute hash for {file_path.name}: {e}", "ERROR")
            return None
    
    def generate_manifest(self, mode: str = "manual") -> float:
        """
        Generate integrity manifest with SHA-256 hashes of all critical files.
        
        This should be run once during build/deployment to create the baseline.
        
        Args:
            mode: Generation mode ("manual", "auto", "cli")
        
        Returns:
            float: Generation time in milliseconds
        
        Raises:
            RuntimeError: If manifest generation fails critically
        """
        self._log(f"Generating integrity manifest (mode: {mode})...", "INFO")
        
        start_time = time.time()
        
        # Build file hashes
        file_hashes = {}
        failed_files = []
        missing_files = []
        
        for file_name in self.CRITICAL_FILES:
            file_path = self.app_root / file_name
            
            if not file_path.exists():
                self._log(f"Warning: Critical file '{file_name}' not found during manifest generation", "WARNING")
                missing_files.append(file_name)
                continue
            
            file_hash = self._compute_file_hash(file_path)
            
            if file_hash:
                file_hashes[file_name] = file_hash
                self._log(f"  ✓ {file_name}: {file_hash[:16]}...", "DEBUG")
            else:
                self._log(f"  ✗ Failed to hash: {file_name}", "WARNING")
                failed_files.append(file_name)
        
        # Safety check: Don't overwrite manifest if too many files are missing
        if len(missing_files) > len(self.CRITICAL_FILES) * 0.3:  # > 30% missing
            error_msg = f"Too many missing files ({len(missing_files)}). Aborting manifest generation for safety."
            self._log(error_msg, "ERROR")
            raise RuntimeError(error_msg)
        
        # Build complete manifest with metadata
        manifest = {
            "_metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "generation_mode": mode,
                "total_files": len(self.CRITICAL_FILES),
                "hashed_files": len(file_hashes),
                "missing_files": len(missing_files),
                "failed_files": len(failed_files)
            },
            "files": file_hashes
        }
        
        # Save manifest atomically
        try:
            # Write to temporary file first
            temp_path = self.manifest_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, sort_keys=True)
            
            # Atomic rename
            temp_path.replace(self.manifest_path)
            
            elapsed_ms = (time.time() - start_time) * 1000
            self._log(f"Integrity manifest generated successfully ({len(file_hashes)} files, {elapsed_ms:.1f}ms)", "INFO")
            self._log(f"Manifest saved to: {self.manifest_path}", "INFO")
            
            # Clean up dev mode file if auto-generated
            if mode == "auto" and self._check_dev_mode_file():
                self._delete_dev_mode_file()
            
            return elapsed_ms
        
        except Exception as e:
            self._log(f"Failed to save manifest: {e}", "ERROR")
            raise RuntimeError(f"Manifest save failed: {e}")
    
    def auto_generate_if_triggered(self) -> Tuple[bool, Optional[float]]:
        """
        Check for developer triggers and auto-generate manifest if detected.
        
        This is called during application startup to support developer workflow.
        DOES NOT run during normal user execution.
        
        Returns:
            Tuple[bool, Optional[float]]: (was_generated, elapsed_ms)
        """
        if not self.should_auto_generate():
            return False, None
        
        try:
            self._log("🔧 Developer trigger detected - Auto-generating integrity manifest...", "INFO")
            elapsed_ms = self.generate_manifest(mode="auto")
            self._log(f"✓ Auto-manifest generated successfully ({elapsed_ms:.1f}ms)", "INFO")
            return True, elapsed_ms
        
        except Exception as e:
            self._log(f"✗ Auto-manifest generation failed: {e}", "ERROR")
            return False, None
    
    def verify_integrity(self) -> bool:
        """
        Verify application integrity against stored manifest.
        
        This is the main verification method called on application startup.
        Performs fast SHA-256 verification of all critical files.
        
        Returns:
            bool: True if all files verified successfully
        """
        start_time = time.time()
        
        # Reset state
        self.is_verified = False
        self.is_tampered = False
        self.modified_files = []
        self.missing_files = []
        
        # Check if manifest exists
        if not self.manifest_path.exists():
            self._log("Integrity manifest not found. Verification skipped.", "WARNING")
            self.verification_time_ms = (time.time() - start_time) * 1000
            return False
        
        # Load manifest
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                self.manifest_data = json.load(f)
        except Exception as e:
            self._log(f"Failed to load integrity manifest: {e}", "ERROR")
            self.verification_time_ms = (time.time() - start_time) * 1000
            return False
        
        if not self.manifest_data:
            self._log("Integrity manifest is empty. Verification skipped.", "WARNING")
            self.verification_time_ms = (time.time() - start_time) * 1000
            return False
        
        # Extract file hashes (handle both old and new manifest formats)
        if "_metadata" in self.manifest_data:
            manifest = self.manifest_data.get("files", {})
        else:
            # Legacy format (backwards compatibility)
            manifest = self.manifest_data
        
        # Verify each file
        all_verified = True
        
        for file_name, stored_hash in manifest.items():
            file_path = self.app_root / file_name
            
            # Check if file exists
            if not file_path.exists():
                self._log(f"Integrity warning: File '{file_name}' is missing", "WARNING")
                self.missing_files.append(file_name)
                all_verified = False
                continue
            
            # Compute current hash
            current_hash = self._compute_file_hash(file_path)
            
            if current_hash is None:
                self._log(f"Integrity error: Cannot read '{file_name}'", "ERROR")
                all_verified = False
                continue
            
            # Compare hashes
            if current_hash != stored_hash:
                self._log(f"Integrity warning: File '{file_name}' has been modified", "WARNING")
                self.modified_files.append(file_name)
                all_verified = False
        
        # Set final status
        self.is_verified = all_verified
        self.is_tampered = not all_verified
        self.verification_time_ms = (time.time() - start_time) * 1000
        
        # Log results
        if all_verified:
            self._log(f"Integrity check passed: All {len(manifest)} files verified ({self.verification_time_ms:.1f}ms)", "INFO")
        else:
            tamper_count = len(self.modified_files) + len(self.missing_files)
            self._log(f"Integrity check failed: {tamper_count} file(s) tampered ({self.verification_time_ms:.1f}ms)", "WARNING")
            
            if self.modified_files:
                self._log(f"Modified files: {', '.join(self.modified_files)}", "WARNING")
            if self.missing_files:
                self._log(f"Missing files: {', '.join(self.missing_files)}", "WARNING")
        
        return all_verified
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current integrity status.
        
        Returns:
            Dictionary containing:
                - is_verified: bool - All files verified successfully
                - is_tampered: bool - Tampering detected
                - modified_files: List[str] - Files that were modified
                - missing_files: List[str] - Files that are missing
                - verification_time_ms: float - Verification duration
        """
        return {
            "is_verified": self.is_verified,
            "is_tampered": self.is_tampered,
            "modified_files": self.modified_files.copy(),
            "missing_files": self.missing_files.copy(),
            "verification_time_ms": self.verification_time_ms
        }
    
    def get_status_text(self) -> str:
        """
        Get human-readable status text for UI display.
        
        Returns:
            str: Status text ("Verified", "Modified", "Missing Files", "Unknown")
        """
        if not self.manifest_path.exists():
            return "Unknown"
        
        if self.is_verified:
            return "Verified"
        elif self.missing_files:
            return "Missing Files"
        elif self.modified_files:
            return "Modified"
        else:
            return "Unknown"
    
    def get_status_color(self) -> str:
        """
        Get status color for UI styling.
        
        Returns:
            str: Color code ("green", "orange", "red", "gray")
        """
        if not self.manifest_path.exists():
            return "gray"
        
        if self.is_verified:
            return "green"
        elif self.missing_files:
            return "red"
        elif self.modified_files:
            return "orange"
        else:
            return "gray"
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """
        Generate detailed integrity report for UI display.
        
        Returns:
            Dictionary containing:
                - overall_status: str - "verified", "tampered", or "unknown"
                - total_files: int - Total number of monitored files
                - matched: int - Number of matching files
                - mismatched: int - Number of modified files
                - missing: int - Number of missing files
                - verification_time_ms: float - Verification duration
                - last_generated: str - Timestamp of last manifest generation
                - generation_mode: str - Mode used to generate manifest
                - files: List[Dict] - Detailed file information
        """
        if not self.manifest_path.exists():
            return {
                "overall_status": "unknown",
                "total_files": 0,
                "matched": 0,
                "mismatched": 0,
                "missing": 0,
                "verification_time_ms": 0.0,
                "last_generated": "N/A",
                "generation_mode": "N/A",
                "files": []
            }
        
        # Load manifest
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            return {
                "overall_status": "unknown",
                "total_files": 0,
                "matched": 0,
                "mismatched": 0,
                "missing": 0,
                "verification_time_ms": self.verification_time_ms,
                "last_generated": "N/A",
                "generation_mode": "N/A",
                "files": []
            }
        
        # Extract metadata and file hashes
        metadata = manifest_data.get("_metadata", {})
        manifest = manifest_data.get("files", manifest_data if "_metadata" not in manifest_data else {})
        
        # Build detailed file list
        files_detail = []
        matched = 0
        mismatched = 0
        missing = 0
        
        for file_name, stored_hash in manifest.items():
            file_path = self.app_root / file_name
            
            if not file_path.exists():
                status = "missing"
                current_hash = "N/A"
                missing += 1
            else:
                current_hash = self._compute_file_hash(file_path)
                if current_hash is None:
                    status = "error"
                    current_hash = "Error"
                elif current_hash == stored_hash:
                    status = "match"
                    matched += 1
                else:
                    status = "modified"
                    mismatched += 1
            
            files_detail.append({
                "name": file_name,
                "stored_hash": stored_hash,
                "current_hash": current_hash,
                "status": status,
                "path": str(file_path)
            })
        
        # Determine overall status
        if missing > 0 or mismatched > 0:
            overall_status = "tampered"
        else:
            overall_status = "verified"
        
        return {
            "overall_status": overall_status,
            "total_files": len(manifest),
            "matched": matched,
            "mismatched": mismatched,
            "missing": missing,
            "verification_time_ms": self.verification_time_ms,
            "last_generated": metadata.get("generated_at", "N/A"),
            "generation_mode": metadata.get("generation_mode", "N/A"),
            "files": files_detail
        }
    
    def get_manifest_metadata(self) -> Dict[str, Any]:
        """
        Get manifest metadata information.
        
        Returns:
            Dict containing generation timestamp, mode, and file counts
        """
        if not self.manifest_path.exists():
            return {
                "exists": False,
                "generated_at": "N/A",
                "generation_mode": "N/A",
                "total_files": 0
            }
        
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            metadata = manifest_data.get("_metadata", {})
            
            return {
                "exists": True,
                "generated_at": metadata.get("generated_at", "N/A"),
                "generation_mode": metadata.get("generation_mode", "manual"),
                "total_files": metadata.get("hashed_files", len(manifest_data.get("files", manifest_data))),
                "missing_files": metadata.get("missing_files", 0),
                "failed_files": metadata.get("failed_files", 0)
            }
        except Exception:
            return {
                "exists": True,
                "generated_at": "Unknown",
                "generation_mode": "Unknown",
                "total_files": 0
            }


# ═══════════════════════════════════════════════════════════════
# MANIFEST GENERATION UTILITY
# ═══════════════════════════════════════════════════════════════

def generate_manifest_standalone():
    """
    Standalone utility to generate integrity manifest.
    
    Run this during build/deployment:
    python integrity_checker.py --generate
    """
    print("="*70)
    print("Master Refreshing App - Integrity Manifest Generator")
    print("="*70)
    print()
    
    def console_log(message: str, level: str):
        """Simple console logger."""
        prefix = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }.get(level, "•")
        print(f"{prefix} {message}")
    
    checker = IntegrityChecker(log_callback=console_log)
    
    print(f"Application root: {checker.app_root}")
    print(f"Critical files: {len(checker.CRITICAL_FILES)}")
    print()
    
    success = checker.generate_manifest()
    
    print()
    if success:
        print("✅ Integrity manifest generated successfully!")
        print(f"📁 Location: {checker.manifest_path}")
        print()
        print("This manifest should be shipped with your application.")
    else:
        print("❌ Failed to generate integrity manifest.")
        print("Check the error messages above.")
    
    print()
    print("="*70)


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--generate":
        generate_manifest_standalone()
    else:
        print("Usage:")
        print("  python integrity_checker.py --generate    Generate integrity manifest")
        print()
        print("For integration, import IntegrityChecker class in your application.")
