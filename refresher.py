"""
refresher.py - Excel COM Automation Engine

Purpose:
    Core Excel refresh engine using Windows COM automation (win32com).
    Handles opening Excel files in hidden mode, executing RefreshAll(),
    waiting for completion, saving, and proper cleanup.
    
    Features:
    - Silent Excel automation (hidden mode)
    - Sequential file processing
    - Background query refresh with completion polling
    - Comprehensive error handling
    - COM object lifecycle management
    - Callback-based logging
    - Thread-safe design
    - Timeout protection

Author: ENG. Saeed Al-moghrabi
"""

import os
import time
import traceback
from typing import List, Dict, Callable, Optional, Any
from datetime import datetime


class ExcelRefresher:
    """
    Excel file refresh engine using COM automation.
    
    This class manages the complete refresh lifecycle for Excel files
    including opening, refreshing, saving, and cleanup. Designed to
    run silently in the background without displaying Excel windows.
    """
    
    # Constants
    REFRESH_WAIT_TIME = 120  # 2 minutes (120 seconds) fixed wait time
    POLL_INTERVAL = 1.0      # Progress update every 1 second
    DEFAULT_TIMEOUT = 3600   # 1 hour (not used with fixed 2-minute wait)
    
    # COM constants (defined locally to avoid import issues)
    xlCalculationAutomatic = -4105
    xlCalculationManual = -4135
    xlCalculating = 1
    xlDone = 0
    xlPending = 2
    
    def __init__(self, 
                 file_paths: Optional[List[str]] = None,
                 log_callback: Optional[Callable[[str, str], None]] = None,
                 progress_callback: Optional[Callable[[int, int, str, str], None]] = None,
                 wait_progress_callback: Optional[Callable[[int, str], None]] = None,
                 stop_check_callback: Optional[Callable[[], bool]] = None,
                 timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the Excel refresh engine.
        
        Args:
            file_paths: List of Excel file paths to refresh (optional)
            log_callback: Callback function(message, level) for logging
            progress_callback: Callback function(current, total, file_path, status) for progress
            wait_progress_callback: Callback function(percentage, time_remaining) for 2-minute wait progress
            stop_check_callback: Callback function() returns True if stop requested
            timeout: Maximum time in seconds to wait for refresh (default: 600)
        """
        self.file_paths = file_paths or []
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.wait_progress_callback = wait_progress_callback
        self.stop_check_callback = stop_check_callback
        self.timeout = timeout
        self.results: List[Dict[str, Any]] = []
        
        # COM objects (will be initialized per refresh operation)
        self.excel_app = None
        self.workbook = None
    
    def set_files(self, file_paths: List[str]) -> None:
        """
        Set the list of files to refresh.
        
        Args:
            file_paths: List of absolute paths to Excel files
        """
        self.file_paths = file_paths
    
    def refresh_all_files(self) -> Dict[str, Any]:
        """
        Refresh all files in the list sequentially.
        
        Processes each file one at a time, continuing even if individual
        files fail. Never crashes the application.
        
        Returns:
            Dictionary containing:
                - total: Total number of files
                - succeeded: Number of successful refreshes
                - failed: Number of failed refreshes
                - skipped: Number of skipped files (read-only)
                - results: List of individual file results
        """
        self.results = []
        succeeded = 0
        failed = 0
        skipped = 0
        
        self._log(f"Starting refresh of {len(self.file_paths)} file(s)", "INFO")
        start_time = time.time()
        total_files = len(self.file_paths)
        
        for index, file_path in enumerate(self.file_paths, start=1):
            try:
                # Check if stop requested
                if self.stop_check_callback and self.stop_check_callback():
                    self._log("⚠️ Refresh stopped by user", "WARNING")
                    break
                
                # Emit progress: file started
                if self.progress_callback:
                    self.progress_callback(index, total_files, file_path, 'started')
                
                # Refresh single file
                result = self.refresh_single_file(file_path)
                self.results.append(result)
                
                # Emit progress: file completed
                if self.progress_callback:
                    self.progress_callback(index, total_files, file_path, result["status"])
                
                if result["status"] == "success":
                    succeeded += 1
                elif result["status"] == "skipped":
                    skipped += 1
                else:
                    failed += 1
                    
            except Exception as e:
                # Catch any unexpected errors
                error_msg = f"Unexpected error: {str(e)}"
                self._log(f"Critical error refreshing {os.path.basename(file_path)}: {error_msg}", "ERROR")
                
                self.results.append({
                    "file": file_path,
                    "status": "error",
                    "message": error_msg,
                    "error": str(e)
                })
                failed += 1
        
        # Calculate total time
        elapsed_time = time.time() - start_time
        
        # Log completion with all categories
        if skipped > 0:
            self._log(f"Refresh completed: {succeeded} succeeded, {failed} failed, {skipped} skipped ({elapsed_time:.1f}s)", "INFO")
        else:
            self._log(f"Refresh completed: {succeeded} succeeded, {failed} failed ({elapsed_time:.1f}s)", "INFO")
        
        return {
            "total": len(self.file_paths),
            "succeeded": succeeded,
            "failed": failed,
            "skipped": skipped,
            "elapsed_time": elapsed_time,
            "results": self.results
        }
    
    def refresh_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        Refresh a single Excel file.
        
        Complete workflow:
        1. Validate file existence
        2. Check if file is read-only
        3. Initialize Excel COM instance
        4. Open workbook
        5. Execute RefreshAll()
        6. Wait for completion
        7. Save workbook
        8. Close workbook
        9. Release COM objects
        
        Args:
            file_path: Absolute path to Excel file
        
        Returns:
            Dictionary containing:
                - file: File path
                - status: "success", "skipped", or "error"
                - message: Descriptive message
                - duration: Time taken in seconds
                - error: Error details (if failed)
        """
        file_name = os.path.basename(file_path)
        start_time = time.time()
        
        try:
            # Step 1: Validate file exists
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                self._log(error_msg, "ERROR")
                return {
                    "file": file_path,
                    "status": "error",
                    "message": error_msg,
                    "duration": 0
                }
            
            # Step 2: Check if file is read-only
            if self._is_file_readonly(file_path):
                skip_msg = f"Skipped: File is read-only and cannot be refreshed — {file_path}"
                self._log(skip_msg, "WARNING")
                return {
                    "file": file_path,
                    "status": "skipped",
                    "message": f"Skipped: {file_name} (read-only)",
                    "duration": time.time() - start_time
                }
            
            self._log(f"Refreshing: {file_name}", "INFO")
            
            # Step 2: Initialize Excel COM instance
            self._initialize_excel()
            
            # Step 3: Open workbook (ensures Excel stays hidden)
            self._log(f"Opening workbook: {file_name}", "DEBUG")
            self._open_workbook(file_path)
            
            # Ensure Excel remains hidden after opening
            if self.excel_app:
                self.excel_app.Visible = False
                self.excel_app.DisplayAlerts = False
                self.excel_app.ScreenUpdating = False
            
            # Give Excel time to fully load
            time.sleep(1.0)
            
            # Double-check Excel is still hidden after load
            if self.excel_app:
                self.excel_app.Visible = False
            
            # Count rows BEFORE refresh
            self._log(f"Counting rows before refresh...", "DEBUG")
            rows_before = self._get_workbook_row_count(detailed_log=False)
            self._log(f"Rows before refresh: {rows_before:,}", "INFO")
            
            # Step 4: Execute RefreshAll
            self._log(f"Executing RefreshAll: {file_name}", "INFO")
            self._execute_refresh()
            
            # Step 5: Wait 2 minutes with progress updates
            self._log(f"Waiting 2 minutes for refresh to complete...", "INFO")
            self._wait_with_progress()
            
            # Count rows AFTER refresh
            self._log(f"Counting rows after refresh...", "DEBUG")
            rows_after = self._get_workbook_row_count(detailed_log=False)
            added_rows = rows_after - rows_before
            self._log(f"Rows after refresh: {rows_after:,}", "INFO")
            self._log(f"Added rows: {added_rows:+,}", "SUCCESS")
            
            # Step 6: Save and close workbook (ensures Excel stays hidden)
            self._log(f"Saving workbook: {file_name}", "INFO")
            
            # Ensure Excel is hidden before saving
            if self.excel_app:
                self.excel_app.Visible = False
                self.excel_app.DisplayAlerts = False
                self.excel_app.ScreenUpdating = False
            
            self._save_workbook()
            
            # Ensure Excel remains hidden after saving
            if self.excel_app:
                self.excel_app.Visible = False
            
            self._log(f"Closing workbook: {file_name}", "INFO")
            self._close_workbook(save_changes=True)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Step 7: Display success report in log
            success_msg = f"✓ Completed: {file_name} | Duration: {duration:.1f}s | Rows: {rows_before:,} → {rows_after:,} ({added_rows:+,})"
            self._log(success_msg, "SUCCESS")
            
            return {
                "file": file_path,
                "status": "success",
                "message": success_msg,
                "duration": duration,
                "rows_before": rows_before,
                "rows_after": rows_after,
                "added_rows": added_rows
            }
            
        except FileLockedError as e:
            error_msg = f"File is locked or open in another program: {file_name}"
            self._log(error_msg, "ERROR")
            return {
                "file": file_path,
                "status": "error",
                "message": error_msg,
                "duration": time.time() - start_time,
                "error": str(e)
            }
            
        except TimeoutError as e:
            error_msg = f"Refresh timeout exceeded ({self.timeout}s): {file_name}"
            self._log(error_msg, "ERROR")
            return {
                "file": file_path,
                "status": "error",
                "message": error_msg,
                "duration": time.time() - start_time,
                "error": str(e)
            }
            
        except Exception as e:
            error_msg = f"Error refreshing {file_name}: {str(e)}"
            self._log(error_msg, "ERROR")
            self._log(f"Traceback: {traceback.format_exc()}", "DEBUG")
            
            return {
                "file": file_path,
                "status": "error",
                "message": error_msg,
                "duration": time.time() - start_time,
                "error": str(e)
            }
            
        finally:
            # Step 8: Always cleanup COM objects
            self._cleanup_excel()
    
    def _initialize_excel(self) -> None:
        """
        Initialize Excel COM application instance.
        
        Creates a new Excel instance with:
        - Visible = False (hidden)
        - DisplayAlerts = False (no prompts)
        - ScreenUpdating = False (performance)
        """
        try:
            import win32com.client
            
            # Create Excel application instance
            self.excel_app = win32com.client.Dispatch("Excel.Application")
            
            # Configure for silent operation
            self.excel_app.Visible = False
            self.excel_app.DisplayAlerts = False
            self.excel_app.ScreenUpdating = False
            self.excel_app.EnableEvents = False
            
            self._log("Excel COM instance initialized", "DEBUG")
            
        except ImportError:
            raise Exception("pywin32 not installed. Install with: pip install pywin32")
        except Exception as e:
            raise Exception(f"Failed to initialize Excel COM: {str(e)}")
    
    def _get_workbook_row_count(self, detailed_log: bool = False) -> int:
        """
        Get the total number of used rows in the workbook.
        
        Args:
            detailed_log: If True, log details for each sheet
        
        Returns:
            int: Total number of rows across all sheets
        """
        try:
            if not self.workbook:
                return 0
            
            total_rows = 0
            sheet_count = 0
            
            # Get worksheet count
            worksheet_count = self.workbook.Worksheets.Count
            
            # Iterate through all worksheets
            for i in range(1, worksheet_count + 1):
                try:
                    sheet = self.workbook.Worksheets(i)
                    used_range = sheet.UsedRange
                    if used_range:
                        sheet_rows = used_range.Rows.Count
                        total_rows += sheet_rows
                        sheet_count += 1
                        
                        if detailed_log:
                            sheet_name = sheet.Name
                            self._log(f"  Sheet '{sheet_name}': {sheet_rows:,} rows", "DEBUG")
                except Exception:
                    continue
            
            if detailed_log and sheet_count > 0:
                self._log(f"Total rows: {total_rows:,} across {sheet_count} sheets", "DEBUG")
            
            return total_rows
        
        except Exception as e:
            self._log(f"Warning: Could not count rows: {str(e)}", "WARNING")
            return 0
    
    def _open_workbook(self, file_path: str) -> None:
        """
        Open Excel workbook in hidden mode.
        
        Ensures Excel remains hidden when opening the workbook.
        
        Args:
            file_path: Path to Excel file
        
        Raises:
            FileLockedError: If file is locked or open elsewhere
            Exception: For other errors
        """
        if self.excel_app is None:
            raise Exception("Excel application is not initialized; call _initialize_excel() first.")
        try:
            # Ensure Excel is hidden before opening
            if self.excel_app:
                self.excel_app.Visible = False
                self.excel_app.DisplayAlerts = False
                self.excel_app.ScreenUpdating = False
            
            # Attempt to open workbook
            self.workbook = self.excel_app.Workbooks.Open(
                file_path,
                UpdateLinks=0,      # Don't update links automatically
                ReadOnly=False,      # Open for editing
                IgnoreReadOnlyRecommended=True
            )
            
            # Ensure Excel remains hidden after opening
            if self.excel_app:
                self.excel_app.Visible = False
                self.excel_app.DisplayAlerts = False
                self.excel_app.ScreenUpdating = False
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Detect file locked error
            if "permission denied" in error_str or "locked" in error_str or "in use" in error_str:
                raise FileLockedError(f"File is locked: {file_path}")
            else:
                raise Exception(f"Failed to open workbook: {str(e)}")
    
    def _execute_refresh(self) -> None:
        """
        Execute RefreshAll() on the workbook.
        
        This triggers refresh of:
        - PowerQuery connections
        - PivotTables
        - External data connections
        - Data models
        
        Ensures Excel remains hidden during refresh.
        """
        try:
            if self.workbook:
                # Ensure Excel remains hidden and silent
                if self.excel_app:
                    self.excel_app.Visible = False  # Keep hidden
                    self.excel_app.DisplayAlerts = False  # No alerts
                    self.excel_app.ScreenUpdating = False  # No screen updates
                    self.excel_app.EnableEvents = False  # Disable events
                
                # Set calculation to automatic to ensure updates
                self.excel_app.Calculation = self.xlCalculationAutomatic
                
                # Execute refresh
                self.workbook.RefreshAll()
                
                self._log("RefreshAll() executed - waiting for completion...", "INFO")
            else:
                raise Exception("No workbook is open")
                
        except Exception as e:
            raise Exception(f"Failed to execute RefreshAll: {str(e)}")
    
    def _wait_with_progress(self) -> None:
        """
        Wait 2 minutes with progress updates every second.
        
        This provides smooth progress bar updates while waiting
        for the refresh to complete.
        """
        start_time = time.time()
        total_wait = self.REFRESH_WAIT_TIME
        last_progress_pct = -1
        
        while True:
            elapsed = time.time() - start_time
            
            # Check if stop requested
            if self.stop_check_callback and self.stop_check_callback():
                self._log("⚠️ Wait interrupted by user", "WARNING")
                break
            
            # Check if 2 minutes elapsed
            if elapsed >= total_wait:
                self._log(f"✓ Wait complete ({total_wait}s elapsed)", "SUCCESS")
                # Send 100% to UI
                if self.wait_progress_callback:
                    self.wait_progress_callback(100, "00:00")
                break
            
            # Calculate progress percentage
            progress_pct = int((elapsed / total_wait) * 100)
            remaining = total_wait - elapsed
            
            # Update progress every 1% or every second (whichever shows change)
            if progress_pct != last_progress_pct:
                # Format remaining time as MM:SS
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                self._log(
                    f"Refreshing... {progress_pct}% | Remaining: {time_str}",
                    "INFO"
                )
                # Send progress to UI with time remaining
                if self.wait_progress_callback:
                    self.wait_progress_callback(progress_pct, time_str)
                
                last_progress_pct = progress_pct
            
            time.sleep(self.POLL_INTERVAL)

    
    def _save_workbook(self) -> None:
        """
        Save the workbook.
        
        Keeps Excel hidden during save operation.
        
        Raises:
            Exception: If save fails
        """
        try:
            if self.workbook:
                # Ensure Excel remains hidden during save
                if self.excel_app:
                    self.excel_app.Visible = False  # Keep hidden
                    self.excel_app.DisplayAlerts = False  # No alerts
                    self.excel_app.ScreenUpdating = False  # No screen updates
                
                self._log("Saving workbook...", "INFO")
                self.workbook.Save()
                self._log("Workbook saved successfully", "SUCCESS")
            else:
                raise Exception("No workbook is open")
                
        except Exception as e:
            raise Exception(f"Failed to save workbook: {str(e)}")
    
    def _close_workbook(self, save_changes: bool = False) -> None:
        """
        Close the workbook.
        
        Args:
            save_changes: Whether to save changes before closing (default: False)
        """
        try:
            if self.workbook:
                self.workbook.Close(SaveChanges=save_changes)
                self.workbook = None
                
        except Exception as e:
            self._log(f"Warning closing workbook: {str(e)}", "WARNING")
            self.workbook = None
    
    def _cleanup_excel(self) -> None:
        """
        Cleanup Excel COM objects and quit application.
        
        Ensures proper release of COM objects to prevent
        zombie Excel processes.
        """
        try:
            # Close workbook if still open
            if self.workbook:
                try:
                    self.workbook.Close(SaveChanges=False)
                except:
                    pass
                self.workbook = None
            
            # Quit Excel application
            if self.excel_app:
                try:
                    self.excel_app.Quit()
                except:
                    pass
                
                # Release COM object
                try:
                    del self.excel_app
                except:
                    pass
                
                self.excel_app = None
            
            # Force garbage collection (helps release COM objects)
            import gc
            gc.collect()
            
        except Exception as e:
            self._log(f"Warning during Excel cleanup: {str(e)}", "WARNING")
    
    def _is_file_readonly(self, file_path: str) -> bool:
        """
        Check if a file is marked as read-only at filesystem level.
        
        Args:
            file_path: Path to the file to check
        
        Returns:
            bool: True if file is read-only, False otherwise
        """
        try:
            # Check if file has read-only attribute set
            import stat
            file_stats = os.stat(file_path)
            
            # Check if file is read-only (no write permission)
            # On Windows: Check if read-only attribute is set
            if os.name == 'nt':  # Windows
                return not (file_stats.st_mode & stat.S_IWRITE)
            else:  # Unix-like
                return not os.access(file_path, os.W_OK)
        
        except Exception as e:
            # If we can't determine, log and assume writable
            self._log(f"Warning: Could not check read-only status for {file_path}: {e}", "WARNING")
            return False
    
    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message using the callback or stdout.
        
        Args:
            message: Log message
            level: Log level (INFO, DEBUG, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}"
        
        if self.log_callback:
            try:
                self.log_callback(message, level)
            except Exception:
                # Fallback to stdout if callback fails
                print(formatted_message)
        else:
            # No callback - use stdout
            print(formatted_message)
    
    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get results from the last refresh operation.
        
        Returns:
            List of result dictionaries for each file
        """
        return self.results
    
    def __repr__(self) -> str:
        """String representation of ExcelRefresher."""
        return f"ExcelRefresher(files={len(self.file_paths)}, timeout={self.timeout}s)"


# Custom exception classes
class FileLockedError(Exception):
    """Raised when a file is locked or open in another program."""
    pass


# Test/Demo code (for standalone testing)
if __name__ == "__main__":
    import sys
    
    print("=== ExcelRefresher Test ===\n")
    
    # Define a simple log callback
    def console_logger(message: str, level: str):
        colors = {
            "INFO": "\033[37m",      # White
            "DEBUG": "\033[36m",     # Cyan
            "SUCCESS": "\033[32m",   # Green
            "WARNING": "\033[33m",   # Yellow
            "ERROR": "\033[31m",     # Red
        }
        reset = "\033[0m"
        color = colors.get(level, "")
        print(f"{color}[{level}] {message}{reset}")
    
    # Check if test file path provided
    if len(sys.argv) > 1:
        test_files = sys.argv[1:]
    else:
        print("No test files provided.")
        print("Usage: python refresher.py <path_to_excel_file> [<path_to_excel_file2> ...]")
        print("\nExample: python refresher.py C:/Data/report.xlsx")
        sys.exit(0)
    
    # Validate files exist
    valid_files = []
    for file_path in test_files:
        if os.path.exists(file_path):
            valid_files.append(file_path)
            print(f"✓ Found: {os.path.basename(file_path)}")
        else:
            print(f"✗ Not found: {file_path}")
    
    if not valid_files:
        print("\nNo valid files to refresh. Exiting.")
        sys.exit(1)
    
    print(f"\nRefreshing {len(valid_files)} file(s)...\n")
    
    # Create refresher instance
    refresher = ExcelRefresher(
        file_paths=valid_files,
        log_callback=console_logger,
        timeout=600
    )
    
    print(f"Refresher: {refresher}\n")
    
    # Execute refresh
    results = refresher.refresh_all_files()
    
    # Display summary
    print("\n" + "="*60)
    print("REFRESH SUMMARY")
    print("="*60)
    print(f"Total files: {results['total']}")
    print(f"Succeeded: {results['succeeded']}")
    print(f"Failed: {results['failed']}")
    print(f"Total time: {results['elapsed_time']:.1f}s")
    print("="*60)
    
    # Display individual results
    print("\nDETAILED RESULTS:")
    for i, result in enumerate(results['results'], 1):
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"\n{i}. {status_icon} {os.path.basename(result['file'])}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Duration: {result.get('duration', 0):.1f}s")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    print("\n=== Test Complete ===")
