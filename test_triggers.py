"""
Quick Trigger Test Script
Tests all 5 auto-manifest triggers
"""

import os
import subprocess
from pathlib import Path

print("=" * 70)
print("         AUTO-MANIFEST TRIGGERS TEST")
print("=" * 70)
print()

app_root = Path(__file__).parent

# Test 1: CLI Generation
print("[Test 1] --generate-manifest flag")
result = subprocess.run(
    ["python", "main.py", "--generate-manifest"],
    capture_output=True,
    text=True,
    cwd=app_root
)
success = "generated successfully" in result.stdout.lower()
print(f"    Result: {'PASSED' if success else 'FAILED'}")
if success:
    print(f"    Output: {result.stdout.strip().split(chr(10))[1]}")
print()

# Test 2: .dev_mode file
print("[Test 2] .dev_mode file trigger")
dev_file = app_root / ".dev_mode"
dev_file.touch()
print(f"    Created: {dev_file.exists()}")

from integrity_checker import IntegrityChecker
checker = IntegrityChecker()
was_gen, elapsed = checker.auto_generate_if_triggered()
file_exists_after = dev_file.exists()

print(f"    Generated: {was_gen}")
print(f"    Time: {elapsed:.2f} ms" if elapsed else "    Time: N/A")
print(f"    File auto-deleted: {not file_exists_after}")
print(f"    Result: {'PASSED' if (was_gen and not file_exists_after) else 'FAILED'}")
print()

# Test 3: Environment Variable
print("[Test 3] APP_DEV_MODE environment variable")
os.environ["APP_DEV_MODE"] = "1"
checker2 = IntegrityChecker()
should_gen = checker2.should_auto_generate()
os.environ.pop("APP_DEV_MODE")
should_not_gen = checker2.should_auto_generate()

print(f"    With env var: {should_gen}")
print(f"    Without env var: {should_not_gen}")
print(f"    Result: {'PASSED' if (should_gen and not should_not_gen) else 'FAILED'}")
print()

# Test 4: Metadata Verification
print("[Test 4] Manifest metadata")
metadata = checker.get_manifest_metadata()
print(f"    Exists: {metadata['exists']}")
print(f"    Generated at: {metadata['generated_at']}")
print(f"    Mode: {metadata['generation_mode']}")
print(f"    Files: {metadata['total_files']}")
print(f"    Result: {'PASSED' if metadata['exists'] else 'FAILED'}")
print()

# Test 5: Detailed Report
print("[Test 5] Detailed report")
report = checker.get_detailed_report()
print(f"    Status: {report['overall_status']}")
print(f"    Matched: {report['matched']}")
print(f"    Last generated: {report['last_generated']}")
print(f"    Generation mode: {report['generation_mode']}")
print(f"    Result: {'PASSED' if report['overall_status'] == 'verified' else 'FAILED'}")
print()

# Final Summary
print("=" * 70)
print("         ALL TRIGGER TESTS COMPLETED")
print("=" * 70)
