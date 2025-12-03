"""
Quick test script for Auto-Manifest system
"""

from integrity_checker import IntegrityChecker
import os

print('=' * 70)
print('         FINAL SYSTEM VERIFICATION')
print('=' * 70)
print()

# Initialize checker
checker = IntegrityChecker()

# [1] Manifest Status
metadata = checker.get_manifest_metadata()
print('[1] Manifest Status:')
print(f'    EXISTS: {metadata["exists"]}')
print(f'    Generated: {metadata["generated_at"]}')
print(f'    Mode: {metadata["generation_mode"]}')
print(f'    Files: {metadata["total_files"]}')
print()

# [2] Integrity Check
result = checker.verify_integrity()
print('[2] Integrity Check:')
print(f'    Result: {"PASSED" if result else "FAILED"}')
print(f'    Status: {checker.get_status_text()}')
print(f'    Time: {checker.verification_time_ms:.2f} ms')
print()

# [3] Available Triggers
print('[3] Available Triggers:')
print('    [A] --generate-manifest (CLI)')
print('    [B] .dev_mode file')
print('    [C] APP_DEV_MODE=1 (env)')
print('    [D] --auto-manifest (GUI)')
print('    [E] UI Button (Tools menu)')
print()

# [4] Safety Check
print('[4] Safety Check:')
os.environ.pop('APP_DEV_MODE', None)
should_gen = checker.should_auto_generate()
print(f'    Auto-generate without triggers: {should_gen}')
print(f'    Protection active: {not should_gen}')
print()

# [5] Detailed Report
report = checker.get_detailed_report()
print('[5] Detailed Report:')
print(f'    Overall: {report["overall_status"]}')
print(f'    Matched: {report["matched"]}')
print(f'    Modified: {report["mismatched"]}')
print(f'    Missing: {report["missing"]}')
print(f'    Last generated: {report["last_generated"]}')
print(f'    Generation mode: {report["generation_mode"]}')
print()

# Final verdict
print('=' * 70)
if result and not should_gen and metadata['exists']:
    print('         ✓✓✓ ALL SYSTEMS OPERATIONAL ✓✓✓')
else:
    print('         ⚠ SYSTEM ERROR DETECTED')
print('=' * 70)
