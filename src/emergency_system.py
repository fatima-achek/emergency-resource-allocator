"""
Emergency Resource Allocation System.

This is the main module that integrates all components of the system.
It initializes the managers, dispatcher, and user interface, and provides
methods for saving and loading the system state.
"""

import os
import json
import pickle
import datetime
from typing import Dict, List, Any, Optional

from src.models.incident import Incident, IncidentType, IncidentStatus
from src.models.resource import Resource, ResourceType, ResourceStatus
from src.managers.incident_manager import IncidentManager
from src.managers.resource_manager import ResourceManager
from src.algorithms.dispatcher import Dispatcher
from src.utils.logger import SystemLogger
from src.interface.console_ui import ConsoleUI


class EmergencySystem:
    """
    Main system class that integrates all components and manages the system lifecycle.
    
    The EmergencySystem class initializes and coordinates all components of the
    emergency resource allocation system. It handles system startup, shutdown,
    and state persistence.
    
    Attributes:
        incident_manager: Manager for incidents
        resource_manager: Manager for resources
        logger: System logger
        dispatcher: Resource allocation dispatcher
        ui: User interface
        config: System configuration
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the emergency system with default or provided configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        # Set default configuration if none provided
        self.config = config or {
            "log_to_console": True,
            "log_to_file": True,
            "log_file": "logs/system_log.txt",
            "data_directory": "data/",
            "use_colors": True,
            "allocation_params": {
                "auto_reallocate": True,
                "prioritize_proximity": True,
                "max_allocation_time": 30  # seconds
            }
        }
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.config["data_directory"]):
            os.makedirs(self.config["data_directory"])
        
        # Initialize system logger
        self.logger = SystemLogger(
            console_output=self.config["log_to_console"],
            file_output=self.config["log_to_file"],
            log_file=self.config["log_file"]
        )
        
        # Log system startup
        self.logger.log_info("Emergency Resource Allocation System starting up")
        
        # Initialize managers
        self.incident_manager = IncidentManager()
        self.resource_manager = ResourceManager()
        
        # Initialize dispatcher with managers
        self.dispatcher = Dispatcher(self.incident_manager, self.resource_manager, self.logger)
        
        # Initialize user interface
        self.ui = ConsoleUI(self)
        
        self.logger.log_info("System initialized successfully")
    
    def run(self):
        """
        Run the main system loop.
        
        This method starts the user interface and runs until the user exits.
        """
        self.logger.log_info("System main loop started")
        self.ui.run()
        self.logger.log_info("System shutting down")
    
    def add_sample_data(self):
        """
        Add sample incidents and resources for testing.
        
        This method creates a set of incidents and resources for demonstration
        and testing purposes.
        """
        self.logger.log_info("Adding sample data to system")
        
        # Add sample resources
        resources = [
            ("AMBULANCE", "Zone 1", ["advanced_life_support"]),
            ("AMBULANCE", "Zone 3", ["basic_life_support"]),
            ("FIRE_TRUCK", "Zone 2", ["ladder", "pump"]),
            ("FIRE_TRUCK", "Zone 4", ["hazmat"]),
            ("POLICE_UNIT", "Zone 1", []),
            ("POLICE_UNIT", "Zone 3", []),
            ("RESCUE_TEAM", "Zone 2", ["water_rescue"]),
            ("HAZMAT_UNIT", "Zone 5", []),
            ("MEDICAL_TEAM", "Zone 3", ["trauma"]),
            ("HELICOPTER", "Zone 1", [])
        ]
        
        for resource_type, location, capabilities in resources:
            self.resource_manager.add_resource(resource_type, location, capabilities)
            
        # Add sample incidents
        incidents = [
            ("FIRE", "Zone 2", 1, ["FIRE_TRUCK", "AMBULANCE"], "Building on fire", 5, ["children"]),
            ("MEDICAL", "Zone 3", 2, ["AMBULANCE", "MEDICAL_TEAM"], "Heart attack", 1, ["elderly"]),
            ("TRAFFIC", "Zone 1", 3, ["POLICE_UNIT", "AMBULANCE"], "Car accident", 2, ["multi_vehicle"]),
            ("HAZMAT", "Zone 5", 1, ["HAZMAT_UNIT", "FIRE_TRUCK"], "Chemical spill", 0, ["hazardous_materials"]),
            ("RESCUE", "Zone 4", 2, ["RESCUE_TEAM", "HELICOPTER"], "Person trapped", 1, [])
        ]
        
        for inc_type, location, priority, resources, details, affected, factors in incidents:
            self.incident_manager.add_incident(inc_type, location, priority, resources, details, affected, factors)
            
        self.logger.log_info(f"Added {len(resources)} sample resources and {len(incidents)} sample incidents")
    
    def save_state(self, filename: str = "system_state.pkl") -> bool:
        """
        Save the current system state to a file.
        
        This method serializes the current system state, including all incidents,
        resources, and allocations, to a file for later restoration.
        
        Args:
            filename: Name of the file to save to
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        filepath = os.path.join(self.config["data_directory"], filename)
        
        try:
            # Create a state dictionary with all the system data
            state = {
                "incidents": self.incident_manager.incidents,
                "resources": self.resource_manager.resources,
                "allocation_map": self.dispatcher.allocation_map,
                "timestamp": datetime.datetime.now()
            }
            
            # Save using pickle
            with open(filepath, 'wb') as f:
                pickle.dump(state, f)
                
            self.logger.log_info(f"System state saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error saving system state: {e}")
            return False
    
    def load_state(self, filename: str = "system_state.pkl") -> bool:
        """
        Load a previously saved system state from a file.
        
        This method deserializes a previously saved system state, restoring
        all incidents, resources, and allocations.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            bool: True if load was successful, False otherwise
        """
        filepath = os.path.join(self.config["data_directory"], filename)
        
        if not os.path.exists(filepath):
            self.logger.log_error(f"State file {filepath} does not exist")
            return False
            
        try:
            # Load using pickle
            with open(filepath, 'rb') as f:
                state = pickle.load(f)
                
            # Restore state
            self.incident_manager.incidents = state["incidents"]
            self.resource_manager.resources = state["resources"]
            self.dispatcher.allocation_map = state["allocation_map"]
            
            # Re-initialize dispatcher priority queue
            self.dispatcher.priority_queue.clear_queue()
            for incident in self.incident_manager.get_all_incidents():
                if incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]:
                    self.dispatcher.priority_queue.add_incident(incident)
                    
            self.logger.log_info(f"System state loaded from {filepath}")
            self.logger.log_info(f"Loaded {len(self.incident_manager.incidents)} incidents and " +
                               f"{len(self.resource_manager.resources)} resources")
                               
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error loading system state: {e}")
            return False
    
    def export_system_report(self, filename: str = "system_report.txt") -> bool:
        """
        Export a comprehensive system report to a file.
        
        This method generates a detailed report of the current system state,
        including all incidents, resources, allocations, and system statistics.
        
        Args:
            filename: Name of the file to export to
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        filepath = os.path.join(self.config["data_directory"], filename)
        
        try:
            with open(filepath, 'w') as f:
                # Report header
                f.write("="*80 + "\n")
                f.write("EMERGENCY RESOURCE ALLOCATION SYSTEM - SYSTEM REPORT\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                # System overview
                f.write("SYSTEM OVERVIEW\n")
                f.write("-"*80 + "\n")
                
                incidents = self.incident_manager.get_all_incidents()
                resources = self.resource_manager.get_all_resources()
                
                active_incidents = [i for i in incidents if i.status not in 
                                   [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]]
                                   
                available_resources = self.resource_manager.get_available_resources()
                
                f.write(f"Total Incidents: {len(incidents)}\n")
                f.write(f"Active Incidents: {len(active_incidents)}\n")
                f.write(f"Total Resources: {len(resources)}\n")
                f.write(f"Available Resources: {len(available_resources)}\n")
                f.write(f"Allocated Incidents: {len(self.dispatcher.allocation_map)}\n\n")
                
                # Incident summary
                f.write("INCIDENT SUMMARY\n")
                f.write("-"*80 + "\n")
                
                # Incidents by type
                incidents_by_type = {}
                for incident in incidents:
                    type_name = incident.incident_type.name
                    if type_name not in incidents_by_type:
                        incidents_by_type[type_name] = 0
                    incidents_by_type[type_name] += 1
                    
                f.write("Incidents by Type:\n")
                for type_name, count in incidents_by_type.items():
                    f.write(f"  {type_name}: {count}\n")
                    
                # Incidents by priority
                incidents_by_priority = {}
                for incident in incidents:
                    priority = incident.priority
                    if priority not in incidents_by_priority:
                        incidents_by_priority[priority] = 0
                    incidents_by_priority[priority] += 1
                    
                f.write("\nIncidents by Priority:\n")
                for priority in sorted(incidents_by_priority.keys()):
                    f.write(f"  Priority {priority}: {incidents_by_priority[priority]}\n")
                    
                # Incidents by status
                incidents_by_status = {}
                for incident in incidents:
                    status = incident.status.name
                    if status not in incidents_by_status:
                        incidents_by_status[status] = 0
                    incidents_by_status[status] += 1
                    
                f.write("\nIncidents by Status:\n")
                for status, count in incidents_by_status.items():
                    f.write(f"  {status}: {count}\n")
                
                f.write("\n")
                
                # Resource summary
                f.write("RESOURCE SUMMARY\n")
                f.write("-"*80 + "\n")
                
                # Resources by type
                resources_by_type = {}
                for resource in resources:
                    type_name = resource.resource_type.name
                    if type_name not in resources_by_type:
                        resources_by_type[type_name] = 0
                    resources_by_type[type_name] += 1
                    
                f.write("Resources by Type:\n")
                for type_name, count in resources_by_type.items():
                    f.write(f"  {type_name}: {count}\n")
                    
                # Resources by status
                resources_by_status = {}
                for resource in resources:
                    status = resource.status.name
                    if status not in resources_by_status:
                        resources_by_status[status] = 0
                    resources_by_status[status] += 1
                    
                f.write("\nResources by Status:\n")
                for status, count in resources_by_status.items():
                    f.write(f"  {status}: {count}\n")
                    
                # Resources by location
                resources_by_location = {}
                for resource in resources:
                    location = resource.location
                    if location not in resources_by_location:
                        resources_by_location[location] = 0
                    resources_by_location[location] += 1
                    
                f.write("\nResources by Location:\n")
                for location, count in sorted(resources_by_location.items()):
                    f.write(f"  {location}: {count}\n")
                
                f.write("\n")
                
                # Allocation summary
                f.write("ALLOCATION SUMMARY\n")
                f.write("-"*80 + "\n")
                
                if not self.dispatcher.allocation_map:
                    f.write("No resources currently allocated.\n\n")
                else:
                    for incident_id, resources in self.dispatcher.allocation_map.items():
                        incident = self.incident_manager.get_incident(incident_id)
                        
                        if incident:
                            f.write(f"Incident #{incident_id} - {incident.incident_type.value} at {incident.location}\n")
                            f.write(f"  Priority: {incident.priority}, Urgency Score: {incident.urgency_score:.2f}\n")
                            f.write(f"  Status: {incident.status.value}\n")
                            f.write(f"  Required Resources: {', '.join(incident.required_resources)}\n")
                            f.write("  Assigned Resources:\n")
                            
                            for resource in resources:
                                f.write(f"    - {resource.resource_type.value} {resource.id} from {resource.location}\n")
                                f.write(f"      Status: {resource.status.value}\n")
                                
                            f.write("\n")
                
                # System performance
                f.write("SYSTEM PERFORMANCE\n")
                f.write("-"*80 + "\n")
                
                # Calculate response statistics
                total_response_time = 0
                response_times = []
                
                for incident in incidents:
                    if incident.history and len(incident.history) >= 2:
                        reported_time = incident.history[0]["timestamp"]
                        
                        # Find first assignment time
                        assigned_time = None
                        for entry in incident.history[1:]:
                            if "assigned" in entry["description"].lower():
                                assigned_time = entry["timestamp"]
                                break
                                
                        if assigned_time:
                            response_time = (assigned_time - reported_time).total_seconds() / 60  # minutes
                            total_response_time += response_time
                            response_times.append(response_time)
                
                if response_times:
                    avg_response_time = total_response_time / len(response_times)
                    max_response_time = max(response_times)
                    min_response_time = min(response_times)
                    
                    f.write(f"Average Response Time: {avg_response_time:.2f} minutes\n")
                    f.write(f"Maximum Response Time: {max_response_time:.2f} minutes\n")
                    f.write(f"Minimum Response Time: {min_response_time:.2f} minutes\n")
                else:
                    f.write("No response time data available.\n")
                
                f.write("\n")
                
                # Recent system logs
                f.write("RECENT SYSTEM LOGS\n")
                f.write("-"*80 + "\n")
                
                recent_logs = self.logger.get_recent_logs(20)
                for log in recent_logs:
                    f.write(log + "\n")
                    
            self.logger.log_info(f"System report exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error exporting system report: {e}")
            return False
    
    def reset(self) -> None:
        """
        Reset the system to its initial state.
        
        This method clears all incidents, resources, and allocations,
        effectively resetting the system.
        """
        self.logger.log_warning("Resetting system to initial state")
        
        # Confirm with user via UI
        confirm = input("Are you sure you want to reset the system? This will delete all data. (y/n): ")
        if confirm.lower() != 'y':
            self.logger.log_info("System reset cancelled")
            return
            
        # Re-initialize managers and dispatcher
        self.incident_manager = IncidentManager()
        self.resource_manager = ResourceManager()
        self.dispatcher = Dispatcher(self.incident_manager, self.resource_manager, self.logger)
        
        self.logger.log_info("System reset complete")