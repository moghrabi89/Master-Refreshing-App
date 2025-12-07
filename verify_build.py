"""
verify_build.py - Post-Build Verification Script
Master Refreshing App v1.0.0

Purpose:
    Automated verification of built executables to ensure:
    - File exists and has reasonable size
    - Digital signature present (if signed)
    - Manifest embedded correctly
    - No suspicious imports or characteristics
    - Ready for distribution

Usage:
    python verify_build.py [path_to_exe]
    
    If no path provided, checks: dist\\MasterRefreshingApp.exe

Author: ENG. Saeed Al-moghrabi
"""

import os
import sys
import subprocess
import hashlib
from pathlib import Path


class BuildVerifier:
    """Comprehensive build verification for Windows executables."""
    
    def __init__(self, exe_path=None):
        """Initialize verifier with executable path."""
        if exe_path is None:
            exe_path = Path("dist") / "MasterRefreshingApp.exe"
        
        self.exe_path = Path(exe_path)
        self.results = []
        self.errors = []
        self.warnings = []
    
    def verify_existence(self):
        """Check if executable exists."""
        print("\n[1/7] Checking file existence...")
        if not self.exe_path.exists():
            self.errors.append(f"Executable not found: {self.exe_path}")
            print(f"    [X] FAILED - File not found")
            return False
        
        print(f"    [OK] File exists: {self.exe_path}")
        return True
    
    def verify_size(self):
        """Check if file size is reasonable."""
        print("\n[2/7] Checking file size...")
        
        if not self.exe_path.exists():
            print("    [SKIP] File doesn't exist")
            return False
        
        size_bytes = self.exe_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        # Expected ranges
        min_size_mb = 20  # Too small = missing dependencies
        max_size_mb = 150  # Too large = bloated
        
        print(f"    Size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
        
        if size_mb < min_size_mb:
            self.warnings.append(f"Executable is very small ({size_mb:.1f} MB) - may be missing dependencies")
            print(f"    [!] WARNING - Smaller than expected ({min_size_mb} MB)")
        elif size_mb > max_size_mb:
            self.warnings.append(f"Executable is very large ({size_mb:.1f} MB) - may be bloated")
            print(f"    [!] WARNING - Larger than expected ({max_size_mb} MB)")
        else:
            print(f"    [OK] Size is reasonable")
        
        return True
    
    def calculate_hash(self):
        """Calculate SHA-256 hash for verification."""
        print("\n[3/7] Calculating SHA-256 hash...")
        
        if not self.exe_path.exists():
            print("    [SKIP] File doesn't exist")
            return None
        
        sha256_hash = hashlib.sha256()
        with open(self.exe_path, "rb") as f:
            # Ensure the lambda is typed as returning bytes so the type checker is satisfied
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)  # type: ignore[arg-type]
        
        hash_value = sha256_hash.hexdigest()
        print(f"    [OK] SHA-256: {hash_value}")
        
        # Save to file
        hash_file = self.exe_path.parent / "SHA256SUMS.txt"
        with open(hash_file, "w") as f:
            f.write(f"{hash_value}  {self.exe_path.name}\n")
        
        print(f"    [OK] Hash saved to: {hash_file}")
        return hash_value
    
    def verify_signature(self):
        """Check if executable is digitally signed."""
        print("\n[4/7] Checking digital signature...")
        
        if not self.exe_path.exists():
            print("    [SKIP] File doesn't exist")
            return False
        
        try:
            # Use signtool to verify (if available)
            result = subprocess.run(
                ["signtool", "verify", "/pa", str(self.exe_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("    [OK] Digital signature verified")
                return True
            else:
                self.warnings.append("Executable is not digitally signed")
                print("    [!] WARNING - Not signed (recommended for production)")
                return False
        
        except FileNotFoundError:
            print("    [SKIP] SignTool not available (install Windows SDK)")
            self.warnings.append("Could not verify signature - SignTool not found")
            return False
        except Exception as e:
            print(f"    [SKIP] Could not verify signature: {e}")
            return False
    
    def verify_manifest(self):
        """Check if Windows manifest is embedded."""
        print("\n[5/7] Checking Windows manifest...")
        
        if not self.exe_path.exists():
            print("    [SKIP] File doesn't exist")
            return False
        
        # Read file and check for manifest markers
        try:
            with open(self.exe_path, "rb") as f:
                content = f.read()
            
            # Check for manifest markers
            manifest_markers = [
                b"asInvoker",
                b"requestedExecutionLevel",
                b"Microsoft.Windows.Common-Controls"
            ]
            
            found_markers = sum(1 for marker in manifest_markers if marker in content)
            
            if found_markers >= 2:
                print(f"    [OK] Manifest appears to be embedded ({found_markers}/3 markers found)")
                return True
            else:
                self.warnings.append("Windows manifest may not be properly embedded")
                print(f"    [!] WARNING - Manifest markers not found")
                return False
        
        except Exception as e:
            print(f"    [SKIP] Could not check manifest: {e}")
            return False
    
    def verify_dependencies(self):
        """Check for suspicious or unnecessary dependencies."""
        print("\n[6/7] Checking dependencies...")
        
        if not self.exe_path.exists():
            print("    [SKIP] File doesn't exist")
            return False
        
        # Read file and check for unwanted imports
        try:
            with open(self.exe_path, "rb") as f:
                content = f.read()
            
            # Suspicious patterns (should NOT be present)
            suspicious_patterns = [
                (b"tkinter", "Tkinter (should be excluded)"),
                (b"numpy", "NumPy (should be excluded)"),
                (b"matplotlib", "Matplotlib (should be excluded)"),
                (b"pandas", "Pandas (should be excluded)"),
                (b"PIL", "Pillow/PIL (should be excluded)"),
            ]
            
            found_suspicious = []
            for pattern, name in suspicious_patterns:
                if pattern in content:
                    found_suspicious.append(name)
            
            if found_suspicious:
                self.warnings.append(f"Unnecessary modules detected: {', '.join(found_suspicious)}")
                print(f"    [!] WARNING - Found: {', '.join(found_suspicious)}")
            else:
                print("    [OK] No unnecessary modules detected")
            
            return len(found_suspicious) == 0
        
        except Exception as e:
            print(f"    [SKIP] Could not check dependencies: {e}")
            return False
    
    def test_execution(self):
        """Test if executable runs (quick validation mode)."""
        print("\n[7/7] Testing execution...")
        print("    [INFO] Manual testing required")
        print("    [INFO] Run: dist\\MasterRefreshingApp.exe")
        print("    [INFO] Verify: Application launches without errors")
        return True
    
    def generate_report(self):
        """Generate verification report."""
        print("\n" + "=" * 60)
        print("  BUILD VERIFICATION REPORT")
        print("=" * 60)
        
        print(f"\nExecutable: {self.exe_path}")
        
        if self.exe_path.exists():
            size_mb = self.exe_path.stat().st_size / (1024 * 1024)
            print(f"Size: {size_mb:.2f} MB")
        
        # Errors
        if self.errors:
            print(f"\n[ERRORS] {len(self.errors)} critical issue(s):")
            for error in self.errors:
                print(f"  [X] {error}")
        
        # Warnings
        if self.warnings:
            print(f"\n[WARNINGS] {len(self.warnings)} issue(s):")
            for warning in self.warnings:
                print(f"  [!] {warning}")
        
        # Final verdict
        print("\n" + "=" * 60)
        if self.errors:
            print("  VERDICT: BUILD FAILED")
            print("  Please fix errors and rebuild.")
        elif self.warnings:
            print("  VERDICT: BUILD SUCCESSFUL WITH WARNINGS")
            print("  Executable is usable but improvements recommended.")
        else:
            print("  VERDICT: BUILD SUCCESSFUL")
            print("  Executable is ready for distribution!")
        print("=" * 60)
        
        return len(self.errors) == 0
    
    def run_all_checks(self):
        """Run all verification checks."""
        print("\n" + "=" * 60)
        print("  Master Refreshing App - Build Verification")
        print("  Version: 1.0.0")
        print("=" * 60)
        
        # Run all checks
        self.verify_existence()
        self.verify_size()
        self.calculate_hash()
        self.verify_signature()
        self.verify_manifest()
        self.verify_dependencies()
        self.test_execution()
        
        # Generate report
        return self.generate_report()


def main():
    """Main entry point."""
    # Get executable path from command line or use default
    exe_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create verifier and run checks
    verifier = BuildVerifier(exe_path)
    success = verifier.run_all_checks()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
