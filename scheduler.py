"""
scheduler.py - Daily Refresh Scheduling System

Purpose:
    Background scheduler for automatic daily Excel refresh operations.
    Runs in a separate thread, triggers refresh at configured time,
    and supports dynamic time updates without restart.
    
    Features:
    - Background thread execution
    - Daily scheduling at specific time
    - Start/Stop functionality
    - Dynamic time updates (no restart needed)
    - Callback-based trigger system
    - Minimal CPU usage (smart sleep)
    - Safe thread termination
    - Comprehensive error handling

Author: ENG. Saeed Al-moghrabi
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Optional, List
import re


class RefreshScheduler:
    """
    Daily refresh scheduler with background thread execution.
    
    This class manages automatic daily refresh operations by running
    a background thread that waits until the configured time and
    triggers a callback function.
    """
    
    # Constants
    CHECK_INTERVAL = 30  # Check time every 30 seconds (balance between responsiveness and CPU)
    
    def __init__(self,
                 scheduled_times: Optional[List[str]] = None,
                 refresh_callback: Optional[Callable[[], None]] = None,
                 log_callback: Optional[Callable[[str, str], None]] = None):
        """
        Initialize the refresh scheduler.
        
        Args:
            scheduled_times: List of times in HH:MM format (24-hour), up to 3 times
            refresh_callback: Function to call when scheduled time is reached
            log_callback: Function(message, level) for logging
        """
        if scheduled_times is None:
            scheduled_times = ["06:00"]
        
        self.scheduled_times = [t for t in scheduled_times if t and t.strip()]  # Remove empty
        self.refresh_callback = refresh_callback
        self.log_callback = log_callback
        
        # Threading control
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        self._lock = threading.Lock()
        
        # State tracking
        self._last_execution_date = None
        self._executed_times_today = set()  # Track which times executed today
        
        # Validate initial times
        valid_times = []
        for time_str in self.scheduled_times:
            if self._validate_time_format(time_str):
                valid_times.append(time_str)
            else:
                self._log(f"Invalid time format: {time_str}. Skipping.", "WARNING")
        
        self.scheduled_times = valid_times if valid_times else ["06:00"]
    
    def start(self) -> bool:
        """
        Start the scheduler's background thread.
        
        If already running, does nothing.
        
        Returns:
            True if started successfully, False if already running
        """
        with self._lock:
            if self._running:
                self._log("Scheduler is already running", "WARNING")
                return False
            
            # Clear stop event
            self._stop_event.clear()
            
            # Create and start thread
            # Note: daemon=False ensures the thread keeps the application alive
            # and prevents premature shutdown when scheduler is running
            self._thread = threading.Thread(
                target=self._run_scheduler_loop,
                daemon=False,  # Changed from True to False to prevent app shutdown
                name="RefreshSchedulerThread"
            )
            self._running = True
            self._thread.start()
            
            times_str = ", ".join(self.scheduled_times)
            self._log(f"Scheduler started: Daily refresh at [{times_str}]", "INFO")
            
            # Placeholder: UI signal for scheduler started
            # ui_signal_scheduler_started.emit()
            
            return True
    
    def stop(self) -> bool:
        """
        Stop the scheduler gracefully.
        
        Signals the thread to stop and waits for it to terminate.
        
        Returns:
            True if stopped successfully, False if not running
        """
        with self._lock:
            if not self._running:
                self._log("Scheduler is not running", "WARNING")
                return False
            
            # Signal thread to stop
            self._stop_event.set()
            self._running = False
        
        # Wait for thread to finish (outside lock to avoid deadlock)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
            
            if self._thread.is_alive():
                self._log("Warning: Scheduler thread did not stop cleanly", "WARNING")
        
        self._thread = None
        self._log("Scheduler stopped", "INFO")
        
        # Placeholder: UI signal for scheduler stopped
        # ui_signal_scheduler_stopped.emit()
        
        return True
    
    def set_times(self, new_times: List[str]) -> bool:
        """
        Update the scheduled refresh times dynamically.
        
        Changes take effect immediately without restarting the scheduler.
        
        Args:
            new_times: List of new times in HH:MM format (up to 3)
        
        Returns:
            True if times were updated, False if all invalid
        """
        # Validate and filter valid times
        valid_times = []
        for time_str in new_times[:3]:  # Only take first 3
            if time_str and time_str.strip() and self._validate_time_format(time_str):
                valid_times.append(time_str.strip())
            elif time_str and time_str.strip():
                self._log(f"Invalid time format: {time_str}. Skipping.", "ERROR")
        
        if not valid_times:
            self._log("No valid times provided. Keeping current schedule.", "ERROR")
            return False
        
        old_times = ", ".join(self.scheduled_times)
        self.scheduled_times = valid_times
        
        # Reset execution tracking for today
        self._executed_times_today.clear()
        
        new_times_str = ", ".join(self.scheduled_times)
        self._log(f"Scheduled times updated: [{old_times}] → [{new_times_str}]", "INFO")
        
        return True
    
    def set_time(self, new_time: str) -> bool:
        """
        Update the scheduled refresh time (backward compatibility - sets first time only).
        
        Args:
            new_time: New time in HH:MM format
        
        Returns:
            True if time was updated, False if invalid format
        """
        return self.set_times([new_time])
    
    def is_running(self) -> bool:
        """
        Check if scheduler is currently running.
        
        Returns:
            True if running, False otherwise
        """
        return self._running
    
    def get_scheduled_time(self) -> str:
        """
        Get the first scheduled time (backward compatibility).
        
        Returns:
            Time string in HH:MM format
        """
        return self.scheduled_times[0] if self.scheduled_times else "06:00"
    
    def get_scheduled_times(self) -> List[str]:
        """
        Get all scheduled times.
        
        Returns:
            List of time strings in HH:MM format
        """
        return self.scheduled_times.copy()
    
    def get_next_run_time(self) -> Optional[datetime]:
        """
        Calculate the next scheduled execution time.
        
        Returns:
            DateTime of next scheduled run, or None if not running
        """
        if not self._running:
            return None
        
        return self._calculate_next_run_time()
    
    def _run_scheduler_loop(self) -> None:
        """
        Main scheduler loop running in background thread.
        
        This method runs continuously, checking if the current time
        matches the scheduled time. When matched, triggers the refresh
        callback and waits until the next day.
        """
        self._log("Scheduler thread started", "DEBUG")
        
        try:
            while not self._stop_event.is_set():
                try:
                    # Check if it's time to run any of the scheduled times
                    matched_time = self._is_time_to_refresh()
                    if matched_time:
                        self._log(f"Scheduled time reached: {matched_time}", "INFO")
                        self._execute_scheduled_refresh()
                        
                        # Mark this time as executed today
                        self._executed_times_today.add(matched_time)
                    
                    # Reset execution tracking at midnight
                    now = datetime.now()
                    if self._last_execution_date and self._last_execution_date != now.date():
                        self._executed_times_today.clear()
                    self._last_execution_date = now.date()
                    
                    # Smart sleep: wait until next check interval or stop signal
                    self._stop_event.wait(timeout=self.CHECK_INTERVAL)
                    
                except Exception as e:
                    # Log error but continue running
                    self._log(f"Error in scheduler loop: {str(e)}", "ERROR")
                    self._stop_event.wait(timeout=60)  # Wait 1 minute before retry
        
        except Exception as e:
            self._log(f"Critical error in scheduler thread: {str(e)}", "ERROR")
        
        finally:
            self._log("Scheduler thread stopped", "DEBUG")
    
    GRACE_PERIOD_MINUTES = 10  # Window to catch up if exact minute was missed (e.g. sleep)

    def _is_time_to_refresh(self) -> Optional[str]:
        """
        Check if current time is within allowed window (grace period) of any scheduled time.
        
        Returns:
            Matched time string if it's time to refresh, None otherwise
        """
        now = datetime.now()
        
        # Check each scheduled time
        for scheduled_time in self.scheduled_times:
            # Skip if already executed today
            if scheduled_time in self._executed_times_today:
                continue
                
            try:
                # Parse scheduled time
                hour, minute = map(int, scheduled_time.split(':'))
                
                # Create datetime for today at scheduled time
                scheduled_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Calculate window end (scheduled time + grace period)
                window_end = scheduled_dt + timedelta(minutes=self.GRACE_PERIOD_MINUTES)
                
                # Check if current time is within the window [scheduled, scheduled + grace]
                # This handles cases where the machine was asleep or busy at the exact minute
                if scheduled_dt <= now <= window_end:
                    # Log if this is a catch-up (not exact minute)
                    if now.minute != minute:
                        self._log(f"Catching up missed schedule: {scheduled_time} (Current: {now.strftime('%H:%M')})", "INFO")
                    return scheduled_time
                    
            except (ValueError, AttributeError):
                continue
        
        return None
    
    def _calculate_next_run_time(self) -> datetime:
        """
        Calculate the next scheduled execution time (earliest upcoming time).
        
        Returns:
            DateTime object representing next run
        """
        now = datetime.now()
        
        next_times = []
        for time_str in self.scheduled_times:
            # Parse scheduled time
            hour, minute = map(int, time_str.split(':'))
            
            # Create datetime for today at scheduled time
            scheduled_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If scheduled time has passed today or already executed, schedule for tomorrow
            if now >= scheduled_today or time_str in self._executed_times_today:
                scheduled_next = scheduled_today + timedelta(days=1)
            else:
                scheduled_next = scheduled_today
            
            next_times.append(scheduled_next)
        
        # Return the earliest time
        return min(next_times) if next_times else now
    
    def _execute_scheduled_refresh(self) -> None:
        """
        Execute the scheduled refresh operation.
        
        Calls the refresh callback if provided, otherwise logs a warning.
        """
        try:
            if self.refresh_callback:
                self._log("Triggering scheduled refresh", "INFO")
                
                # Placeholder: UI signal for refresh started
                # ui_signal_scheduled_refresh_started.emit()
                
                # Execute callback
                self.refresh_callback()
                
                self._log("Scheduled refresh completed", "SUCCESS")
                
                # Placeholder: UI signal for refresh completed
                # ui_signal_scheduled_refresh_completed.emit()
            else:
                self._log("No refresh callback defined - skipping execution", "WARNING")
        
        except Exception as e:
            error_msg = f"Error during scheduled refresh: {str(e)}"
            self._log(error_msg, "ERROR")
            
            # Placeholder: UI signal for refresh error
            # ui_signal_scheduled_refresh_error.emit(str(e))
    
    def _validate_time_format(self, time_str: str) -> bool:
        """
        Validate time string format.
        
        Args:
            time_str: Time string to validate
        
        Returns:
            True if valid HH:MM format (24-hour), False otherwise
        """
        # Pattern: HH:MM with 00-23 hours and 00-59 minutes
        pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
        
        if not re.match(pattern, time_str):
            return False
        
        try:
            hour, minute = map(int, time_str.split(':'))
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False
    
    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message using the callback or stdout.
        
        Args:
            message: Log message
            level: Log level (INFO, DEBUG, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [SCHEDULER] [{level}] {message}"
        
        if self.log_callback:
            try:
                self.log_callback(message, level)
            except Exception:
                # Fallback to stdout if callback fails
                print(formatted_message)
        else:
            # No callback - use stdout
            print(formatted_message)
    
    def __repr__(self) -> str:
        """String representation of RefreshScheduler."""
        status = "running" if self._running else "stopped"
        times_str = ", ".join(self.scheduled_times)
        return f"RefreshScheduler(times=[{times_str}], status={status})"
    
    def __del__(self):
        """Cleanup: ensure thread is stopped when object is destroyed."""
        if self._running:
            self.stop()


# Test/Demo code (for standalone testing)
if __name__ == "__main__":
    import sys
    
    print("=== RefreshScheduler Test ===\n")
    
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
    
    # Define a mock refresh callback
    def mock_refresh():
        print("\n" + "="*60)
        print("🔄 EXECUTING SCHEDULED REFRESH!")
        print("="*60)
        print("This is where the Excel refresh would be triggered.")
        print("="*60 + "\n")
    
    # Get test time (default: 1 minute from now for quick testing)
    if len(sys.argv) > 1:
        test_time = sys.argv[1]
    else:
        # Schedule for 1 minute from now
        future_time = datetime.now() + timedelta(minutes=1)
        test_time = future_time.strftime("%H:%M")
        print(f"No time specified. Using 1 minute from now: {test_time}")
    
    print(f"Test scheduled time: {test_time}\n")
    
    # Create scheduler
    scheduler = RefreshScheduler(
        scheduled_times=[test_time],
        refresh_callback=mock_refresh,
        log_callback=console_logger
    )
    
    print(f"Scheduler: {scheduler}\n")
    
    # Test time validation
    print("Testing time validation...")
    print(f"Valid '14:30': {scheduler._validate_time_format('14:30')}")
    print(f"Valid '09:05': {scheduler._validate_time_format('09:05')}")
    print(f"Invalid '25:00': {scheduler._validate_time_format('25:00')}")
    print(f"Invalid '12:60': {scheduler._validate_time_format('12:60')}")
    print(f"Invalid 'abc': {scheduler._validate_time_format('abc')}")
    print()
    
    # Start scheduler
    print("Starting scheduler...")
    scheduler.start()
    
    # Display next run time
    next_run = scheduler.get_next_run_time()
    if next_run:
        print(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test status
    print(f"Is running: {scheduler.is_running()}")
    print(f"Scheduled time: {scheduler.get_scheduled_time()}")
    print()
    
    # Keep running for testing
    print("Scheduler is now running in the background.")
    print("It will trigger at the scheduled time.")
    print("Press Ctrl+C to stop...")
    print()
    
    try:
        # Wait for scheduled time (or until interrupted)
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Stopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped.")
    
    print("\n=== Test Complete ===")
