"""
Emergency Resource Allocation System - Main Entry Point.

This is the main entry point for the Emergency Resource Allocation System.
It initializes the system and starts the application.

Author: [2418298]
Date: April 2025
"""

import os
import sys
import argparse
from src.emergency_system import EmergencySystem


def main():
    """
    Main entry point for the application.
    
    Parses command line arguments, initializes the system,
    and starts the application.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Emergency Resource Allocation System')
    parser.add_argument('--demo', action='store_true', help='Load demo data on startup')
    parser.add_argument('--load', type=str, help='Load system state from file')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--log-file', type=str, default='logs/system_log.txt', help='Path to log file')
    args = parser.parse_args()
    
    # Configure system
    config = {
        "log_to_console": True,
        "log_to_file": True,
        "log_file": args.log_file,
        "data_directory": "data/",
        "use_colors": not args.no_color,
        "allocation_params": {
            "auto_reallocate": True,
            "prioritize_proximity": True,
            "max_allocation_time": 30  # seconds
        }
    }
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(args.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Initialize the system
    system = EmergencySystem(config)
    
    # Load state if requested
    if args.load:
        if not system.load_state(args.load):
            print(f"Error loading state from {args.load}")
            sys.exit(1)
    
    # Load demo data if requested
    if args.demo:
        system.add_sample_data()
    
    # Run the system
    system.run()


if __name__ == "__main__":
    main()