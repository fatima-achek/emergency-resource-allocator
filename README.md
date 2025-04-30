# Emergency Resource Allocation System

## Overview

The Emergency Resource Allocation System is a sophisticated console-based application designed to help emergency coordinators effectively manage incidents and allocate resources in emergency scenarios. The system prioritizes incidents based on a complex urgency calculation, matches available resources with incidents, and can dynamically reallocate resources when higher-priority incidents arise.

## Features

- **Advanced Incident Management**: Log, update, and track emergency incidents with detailed information including location, type, priority, affected people, and special factors.
- **Resource Tracking**: Manage emergency resources such as ambulances, fire trucks, and specialized teams with real-time status and location updates.
- **Smart Allocation Algorithm**: Automatically assign resources to incidents based on priority, proximity, and resource type matching.
- **Dynamic Reallocation**: Reassign resources from lower-priority incidents when critical emergencies arise.
- **Detailed Reporting**: Generate comprehensive reports on system status, incident resolution, and resource utilization.
- **User-Friendly Console Interface**: Easy-to-use text-based interface with color-coding for priorities and statuses.

## System Architecture

The system follows a modular object-oriented design with the following key components:

- **Models**: Core data structures for incidents and resources
- **Managers**: Business logic for managing collections of incidents and resources
- **Algorithms**: The dispatcher and priority queue for resource allocation
- **Interface**: User interface components for interacting with the system
- **Utilities**: Supporting functionality such as logging

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python packages (see requirements.txt)

### Installation

1. Clone this repository or unzip the project files to your local machine
2. Navigate to the project directory
3. Install required dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

Run the application with:

```bash
python main.py
```

#### Command Line Options

- `--demo`: Load sample incidents and resources on startup
- `--load filename`: Load a previously saved system state
- `--no-color`: Disable colored output
- `--log-file path`: Specify a custom log file location

Example:

```bash
python main.py --demo --log-file logs/my_session.log
```

## Usage Guide

### Adding Incidents

1. Select "Manage Incidents" from the main menu
2. Choose "Add New Incident"
3. Follow the prompts to enter incident details:
   - Type of emergency
   - Location
   - Priority level
   - Required resources
   - Affected people
   - Special factors

### Adding Resources

1. Select "Manage Resources" from the main menu
2. Choose "Add New Resource"
3. Follow the prompts to enter resource details:
   - Resource type
   - Current location
   - Special capabilities

### Allocating Resources

1. Select "Perform Resource Allocation" from the main menu
2. Choose "Perform Auto Allocation"
3. Review the allocation results
4. View the allocation map to see how resources have been assigned

### Viewing System Status

1. Select "View System Status" from the main menu
2. Choose from various options to view incidents, resources, and allocations

## Design Decisions

### Priority Scoring System

The system uses a sophisticated urgency scoring algorithm that considers:

- Base priority level
- Incident type severity
- Number of people affected
- Special factors (e.g., children, elderly, hazardous materials)
- Time since reporting

This ensures a fair and effective allocation of resources based on multiple factors, not just a simple priority level.

### Resource Matching

The resource allocation algorithm matches resources to incidents based on:

- Required resource types
- Proximity (calculated response time)
- Resource availability
- Special capabilities

### Reallocation Strategy

When critical incidents arrive with no available resources, the system:

1. Identifies lower-priority incidents with needed resources
2. Calculates the impact of reallocation
3. Reassigns resources from the lowest-impact incidents
4. Updates all affected incidents' statuses

## Project Structure

```
emergency-resource-allocator/
├── main.py                      # Application entry point
├── src/                         # Source code
│   ├── models/                  # Data models
│   │   ├── incident.py          # Incident class
│   │   └── resource.py          # Resource class
│   ├── managers/                # Business logic
│   │   ├── incident_manager.py  # Incident management
│   │   └── resource_manager.py  # Resource management
│   ├── algorithms/              # Allocation algorithms
│   │   ├── dispatcher.py        # Main allocation logic
│   │   └── priority_queue.py    # Priority queue implementation
│   ├── interface/               # User interface
│   │   └── console_ui.py        # Console interface
│   ├── utils/                   # Utilities
│   │   └── logger.py            # Logging system
│   └── emergency_system.py      # Main system class
├── tests/                       # Unit and integration tests
├── data/                        # Sample data and saved states
├── logs/                        # System logs
└── requirements.txt             # Project dependencies
```

## Testing

The system includes comprehensive tests for:

- Unit tests for individual components
- Integration tests for interactions between components
- System tests for end-to-end functionality

Run the tests with:

```bash
python -m unittest discover tests
```

## Future Enhancements

- Geographical mapping integration for more accurate location-based allocation
- Machine learning for predictive resource positioning
- Web-based user interface
- Mobile application for field reporting
- Real-time notifications and alerts
- Historical data analysis and visualization

## Author

[2418298]

---

*This project is the final assessment for Software Development 1 Module, April 2025.*