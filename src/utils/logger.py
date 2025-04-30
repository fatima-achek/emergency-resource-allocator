"""
Logger Module for Emergency Resource Allocation System.

This module provides the SystemLogger class for recording and tracking
system activities, decisions, and errors. It supports different log levels
and both console and file output.
"""

import datetime
import os
from enum import Enum
from typing import List, Dict, Any, Optional


class LogLevel(Enum):
    """
    Log levels for the system logger.
    
    Different log levels indicate the importance and type of the logged message.
    """
    INFO = "INFO"       # General information
    WARNING = "WARNING" # Potential issues
    ERROR = "ERROR"     # Errors that don't stop operation
    CRITICAL = "CRITICAL"  # Serious errors that might stop operation
    ACTION = "ACTION"   # User and system actions
    ALLOCATION = "ALLOCATION"  # Resource allocation decisions


class SystemLogger:
    """
    Logger for recording system activities and decisions.
    
    The SystemLogger records all significant events in the system, including
    user actions, system operations, resource allocations, and errors.
    It supports different log levels and can output to both console and file.
    
    Attributes:
        log_entries (list): List of log entries
        console_output (bool): Whether to print logs to console
        file_output (bool): Whether to write logs to file
        log_file (str): Path to the log file
        min_console_level (LogLevel): Minimum level to display in console
    """
    
    def __init__(self, console_output: bool = True, file_output: bool = True, 
                 log_file: str = "system_log.txt", min_console_level: LogLevel = LogLevel.INFO):
        """
        Initialize the system logger.
        
        Args:
            console_output: Whether to print logs to console
            file_output: Whether to write logs to file
            log_file: Path to the log file
            min_console_level: Minimum level to display in console
        """
        self.log_entries = []
        self.console_output = console_output
        self.file_output = file_output
        self.log_file = log_file
        self.min_console_level = min_console_level
        
        # Create log directory if needed
        if file_output:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Add header to log file if it's new
            if not os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write(f"=== Emergency Resource Allocation System Log ===\n")
                    f.write(f"Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO) -> None:
        """
        Log a message with the specified level.
        
        Args:
            message: The message to log
            level: The log level
        """
        timestamp = datetime.datetime.now()
        
        # Create log entry
        entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        
        # Add to log entries
        self.log_entries.append(entry)
        
        # Format for output
        formatted = self._format_entry(entry)
        
        # Console output if enabled and level is sufficient
        if self.console_output and level.value >= self.min_console_level.value:
            print(formatted)
        
        # File output if enabled
        if self.file_output:
            with open(self.log_file, 'a') as f:
                f.write(formatted + "\n")
    
    def _format_entry(self, entry: Dict[str, Any]) -> str:
        """
        Format a log entry for output.
        
        Args:
            entry: The log entry to format
            
        Returns:
            str: Formatted log entry
        """
        timestamp_str = entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        level_str = entry["level"].value
        message = entry["message"]
        
        return f"[{timestamp_str}] [{level_str}] {message}"
    
    def log_info(self, message: str) -> None:
        """
        Log an info message.
        
        Args:
            message: The message to log
        """
        self.log(message, LogLevel.INFO)
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
        """
        self.log(message, LogLevel.WARNING)
    
    def log_error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: The message to log
        """
        self.log(message, LogLevel.ERROR)
    
    def log_critical(self, message: str) -> None:
        """
        Log a critical error message.
        
        Args:
            message: The message to log
        """
        self.log(message, LogLevel.CRITICAL)
    
    def log_action(self, message: str) -> None:
        """
        Log a user or system action.
        
        Args:
            message: The message to log
        """
        self.log(message, LogLevel.ACTION)
    
    def log_allocation(self, message: str) -> None:
        """
        Log a resource allocation decision.
        
        Args:
            message: The message to log
        """
        self.log(message, LogLevel.ALLOCATION)
    
    def get_recent_logs(self, count: int = 10, level: Optional[LogLevel] = None) -> List[str]:
        """
        Get recent log entries.
        
        Args:
            count: Number of entries to retrieve
            level: Optional filter by log level
            
        Returns:
            list: List of formatted log entries
        """
        # Filter by level if specified
        if level:
            entries = [e for e in self.log_entries if e["level"] == level]
        else:
            entries = self.log_entries
        
        # Get most recent entries
        recent = entries[-count:] if count < len(entries) else entries
        
        # Format and return
        return [self._format_entry(entry) for entry in recent]
    
    def get_logs_by_level(self, level: LogLevel) -> List[str]:
        """
        Get all log entries with the specified level.
        
        Args:
            level: The log level to filter by
            
        Returns:
            list: List of formatted log entries
        """
        entries = [e for e in self.log_entries if e["level"] == level]
        return [self._format_entry(entry) for entry in entries]
    
    def export_logs(self, output_file: str) -> bool:
        """
        Export all logs to a file.
        
        Args:
            output_file: Path to export file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            with open(output_file, 'w') as f:
                f.write(f"=== Emergency Resource Allocation System Log Export ===\n")
                f.write(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Entries: {len(self.log_entries)}\n\n")
                
                for entry in self.log_entries:
                    f.write(self._format_entry(entry) + "\n")
            
            return True
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return False
    
    def clear_logs(self) -> None:
        """
        Clear all log entries.
        """
        self.log_entries = []
        
        # Add log cleared entry
        self.log_action("Log entries cleared")