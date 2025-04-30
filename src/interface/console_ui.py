"""
Console User Interface for Emergency Resource Allocation System.

This module provides a text-based user interface for interacting with the
emergency resource allocation system. It handles user input and displays
formatted output for managing incidents and resources.
"""

import os
import datetime
import time
from typing import List, Dict, Any, Tuple, Optional, Callable

from src.models.incident import Incident, IncidentType, IncidentStatus
from src.models.resource import Resource, ResourceType, ResourceStatus


class ConsoleUI:
    """
    Console-based user interface for the emergency resource allocation system.
    
    This class provides methods for displaying menus, formatting output,
    and handling user input for the emergency resource allocation system.
    
    Attributes:
        system: Reference to the main system
        incident_manager: Reference to the incident manager
        resource_manager: Reference to the resource manager
        dispatcher: Reference to the dispatcher
        logger: Reference to the system logger
    """
    
    def __init__(self, system):
        """
        Initialize the console UI.
        
        Args:
            system: Reference to the main system
        """
        self.system = system
        self.incident_manager = system.incident_manager
        self.resource_manager = system.resource_manager
        self.dispatcher = system.dispatcher
        self.logger = system.logger
        
        # ANSI color codes for colorful output
        self.COLORS = {
            'RESET': '\033[0m',
            'BOLD': '\033[1m',
            'RED': '\033[91m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'BLUE': '\033[94m',
            'MAGENTA': '\033[95m',
            'CYAN': '\033[96m',
            'WHITE': '\033[97m',
        }
        
        # Priority color mapping
        self.PRIORITY_COLORS = {
            1: self.COLORS['RED'],     # Highest priority
            2: self.COLORS['MAGENTA'],
            3: self.COLORS['YELLOW'],
            4: self.COLORS['BLUE'],
            5: self.COLORS['GREEN'],   # Lowest priority
        }
        
        # Check if terminal supports colors
        self.use_colors = os.name == 'posix' or 'ANSICON' in os.environ
    
    def clear_screen(self) -> None:
        """
        Clear the console screen.
        """
        # Check platform and clear screen accordingly
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def color_text(self, text: str, color_code: str) -> str:
        """
        Apply color to text if terminal supports it.
        
        Args:
            text: The text to color
            color_code: The color code to apply
            
        Returns:
            str: Colored text if supported, original text otherwise
        """
        if self.use_colors:
            return f"{color_code}{text}{self.COLORS['RESET']}"
        return text
    
    def display_header(self, title: str) -> None:
        """
        Display a header with the given title.
        
        Args:
            title: The title to display
        """
        print("\n" + "="*70)
        print(self.color_text(f"  {title.upper()}", self.COLORS['BOLD']))
        print("="*70)
    
    def display_menu(self) -> None:
        """
        Display the main menu of the system.
        """
        self.clear_screen()
        
        # Current system time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Display header
        print("\n" + "="*70)
        print(self.color_text("  EMERGENCY RESOURCE ALLOCATION SYSTEM", self.COLORS['BOLD'] + self.COLORS['BLUE']))
        print("="*70)
        print(f"  Current Time: {current_time}")
        print("-"*70)
        
        # Incident and resource counts
        num_incidents = len(self.incident_manager.get_all_incidents())
        num_active = len([i for i in self.incident_manager.get_all_incidents() 
                         if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]])
        num_resources = len(self.resource_manager.get_all_resources())
        num_available = len(self.resource_manager.get_available_resources())
        
        print(f"  Active Incidents: {self.color_text(str(num_active), self.COLORS['RED'])} / {num_incidents} total")
        print(f"  Available Resources: {self.color_text(str(num_available), self.COLORS['GREEN'])} / {num_resources} total")
        print("-"*70)
        
        # Menu options
        print("  1. Manage Incidents")
        print("  2. Manage Resources")
        print("  3. Perform Resource Allocation")
        print("  4. View System Status")
        print("  5. Advanced Options")
        print("  6. System Settings")
        print("  0. Exit System")
        print("-"*70)
    
    def display_incidents_menu(self) -> None:
        """
        Display the incidents management menu.
        """
        self.clear_screen()
        self.display_header("Incident Management")
        
        print("  1. Add New Incident")
        print("  2. Update Incident")
        print("  3. View All Incidents")
        print("  4. View Active Incidents")
        print("  5. View Incident Details")
        print("  6. Mark Incident as Resolved")
        print("  7. Cancel Incident")
        print("  0. Return to Main Menu")
        print("-"*70)
    
    def display_resources_menu(self) -> None:
        """
        Display the resources management menu.
        """
        self.clear_screen()
        self.display_header("Resource Management")
        
        print("  1. Add New Resource")
        print("  2. Update Resource Status")
        print("  3. Update Resource Location")
        print("  4. View All Resources")
        print("  5. View Available Resources")
        print("  6. View Resource Details")
        print("  7. Mark Resource Out of Service")
        print("  8. Mark Resource Back in Service")
        print("  0. Return to Main Menu")
        print("-"*70)
    
    def display_allocation_menu(self) -> None:
        """
        Display the resource allocation menu.
        """
        self.clear_screen()
        self.display_header("Resource Allocation")
        
        print("  1. Perform Auto Allocation")
        print("  2. View Current Allocations")
        print("  3. Manually Assign Resource")
        print("  4. Release Resource")
        print("  5. Reallocate All Resources")
        print("  0. Return to Main Menu")
        print("-"*70)
    
    def display_system_status_menu(self) -> None:
        """
        Display the system status menu.
        """
        self.clear_screen()
        self.display_header("System Status")
        
        print("  1. View System Overview")
        print("  2. View Incident Summary")
        print("  3. View Resource Summary")
        print("  4. View Allocation Map")
        print("  5. View Recent Activity Logs")
        print("  6. Generate System Report")
        print("  0. Return to Main Menu")
        print("-"*70)
    
    def display_advanced_menu(self) -> None:
        """
        Display the advanced options menu.
        """
        self.clear_screen()
        self.display_header("Advanced Options")
        
        print("  1. Run Simulation Scenario")
        print("  2. Load Sample Data")
        print("  3. Save System State")
        print("  4. Load System State")
        print("  5. Analyze System Performance")
        print("  6. Export System Logs")
        print("  0. Return to Main Menu")
        print("-"*70)
    
    def display_settings_menu(self) -> None:
        """
        Display the system settings menu.
        """
        self.clear_screen()
        self.display_header("System Settings")
        
        print("  1. Toggle Color Output")
        print("  2. Change Allocation Algorithm Parameters")
        print("  3. Configure Logging Options")
        print("  4. Reset System")
        print("  0. Return to Main Menu")
        print("-"*70)
    
    def get_user_choice(self, prompt: str = "Enter your choice: ", 
                        valid_options: Optional[List[str]] = None) -> str:
        """
        Get user input with validation.
        
        Args:
            prompt: The prompt to display
            valid_options: List of valid input options
            
        Returns:
            str: The user's validated input
        """
        while True:
            choice = input(prompt).strip()
            
            if valid_options is None or choice in valid_options:
                return choice
            
            print(self.color_text(f"Invalid option. Please try again.", self.COLORS['RED']))
    
    def display_incidents(self, incidents: List[Incident], show_header: bool = True) -> None:
        """
        Display a formatted table of incidents.
        
        Args:
            incidents: List of incidents to display
            show_header: Whether to show the table header
        """
        if show_header:
            self.display_header("Incidents")
        
        if not incidents:
            print("  No incidents to display.")
            return
        
        # Define column widths
        col_widths = {
            'id': 4,
            'type': 12,
            'location': 10,
            'priority': 10,
            'status': 15,
            'time': 10,
            'resources': 25
        }
        
        # Print header row
        print(f"\n  {'ID':<{col_widths['id']}} {'Type':<{col_widths['type']}} "
              f"{'Location':<{col_widths['location']}} {'Priority':<{col_widths['priority']}} "
              f"{'Status':<{col_widths['status']}} {'Time Ago':<{col_widths['time']}} "
              f"{'Resources':<{col_widths['resources']}}")
        
        print("  " + "-"*(sum(col_widths.values()) + len(col_widths) - 1))
        
        # Sort incidents by priority and then by timestamp
        sorted_incidents = sorted(incidents, key=lambda x: (x.priority, x.timestamp))
        
        # Print each incident
        for incident in sorted_incidents:
            # Calculate time since report
            time_ago = datetime.datetime.now() - incident.timestamp
            minutes_ago = int(time_ago.total_seconds() / 60)
            time_str = f"{minutes_ago}m ago"
            
            # Get assigned resources
            if incident.assigned_resources:
                resources_str = ", ".join([r.id for r in incident.assigned_resources])
                if len(resources_str) > col_widths['resources'] - 3:
                    resources_str = resources_str[:col_widths['resources'] - 5] + "..."
            else:
                resources_str = "None"
            
            # Format with color for priority
            priority_str = f"P{incident.priority}"
            priority_colored = self.color_text(priority_str, self.PRIORITY_COLORS[incident.priority])
            
            # Status color coding
            status_color = self.COLORS['GREEN']
            if incident.status == IncidentStatus.REPORTED:
                status_color = self.COLORS['RED']
            elif incident.status == IncidentStatus.PARTIAL:
                status_color = self.COLORS['YELLOW']
            elif incident.status == IncidentStatus.ASSIGNED:
                status_color = self.COLORS['BLUE']
            
            status_colored = self.color_text(incident.status.value, status_color)
            
            # Print formatted row
            print(f"  {incident.id:<{col_widths['id']}} "
                  f"{incident.incident_type.name[:col_widths['type']]:<{col_widths['type']}} "
                  f"{incident.location[:col_widths['location']]:<{col_widths['location']}} "
                  f"{priority_colored:<{col_widths['priority']}} "
                  f"{status_colored:<{col_widths['status']}} "
                  f"{time_str:<{col_widths['time']}} "
                  f"{resources_str:<{col_widths['resources']}}")
    
    def display_resources(self, resources: List[Resource], show_header: bool = True) -> None:
        """
        Display a formatted table of resources.
        
        Args:
            resources: List of resources to display
            show_header: Whether to show the table header
        """
        if show_header:
            self.display_header("Resources")
        
        if not resources:
            print("  No resources to display.")
            return
        
        # Define column widths
        col_widths = {
            'id': 8,
            'type': 15,
            'location': 10,
            'status': 20,
            'incident': 10,
            'time': 10
        }
        
        # Print header row
        print(f"\n  {'ID':<{col_widths['id']}} {'Type':<{col_widths['type']}} "
              f"{'Location':<{col_widths['location']}} {'Status':<{col_widths['status']}} "
              f"{'Incident':<{col_widths['incident']}} {'Time in Status':<{col_widths['time']}}")
        
        print("  " + "-"*(sum(col_widths.values()) + len(col_widths) - 1))
        
        # Sort resources by type and then by status
        sorted_resources = sorted(resources, key=lambda x: (x.resource_type.name, x.status.name))
        
        # Print each resource
        for resource in sorted_resources:
            # Calculate time in current status
            time_in_status = datetime.datetime.now() - resource.last_status_change
            minutes = int(time_in_status.total_seconds() / 60)
            time_str = f"{minutes}m"
            
            # Status color coding
            status_color = self.COLORS['RED']
            if resource.status == ResourceStatus.AVAILABLE:
                status_color = self.COLORS['GREEN']
            elif resource.status == ResourceStatus.ASSIGNED:
                status_color = self.COLORS['YELLOW']
            elif resource.status == ResourceStatus.EN_ROUTE or resource.status == ResourceStatus.ON_SCENE:
                status_color = self.COLORS['BLUE']
            
            status_colored = self.color_text(resource.status.value[:17] + "..." if len(resource.status.value) > 20 else resource.status.value, status_color)
            
            # Incident display
            incident_str = str(resource.current_incident) if resource.current_incident else "None"
            
            # Print formatted row
            print(f"  {resource.id:<{col_widths['id']}} "
                  f"{resource.resource_type.name[:col_widths['type']]:<{col_widths['type']}} "
                  f"{resource.location[:col_widths['location']]:<{col_widths['location']}} "
                  f"{status_colored:<{col_widths['status']}} "
                  f"{incident_str:<{col_widths['incident']}} "
                  f"{time_str:<{col_widths['time']}}")
    
    def add_incident(self) -> None:
        """
        Handle user input to add a new incident.
        """
        self.clear_screen()
        self.display_header("Add New Incident")
        
        # Display incident types
        print("\nIncident Types:")
        for i, incident_type in enumerate(IncidentType):
            print(f"  {i+1}. {incident_type.name} - {incident_type.value}")
        
        # Get incident type
        type_choice = int(self.get_user_choice("\nSelect incident type (1-7): ", 
                                              [str(i) for i in range(1, 8)]))
        incident_type = list(IncidentType)[type_choice - 1]
        
        # Get location
        location = input("\nEnter incident location (e.g., Zone 3): ").strip()
        
        # Get priority
        priority = int(self.get_user_choice("\nEnter priority (1-5, where 1 is highest): ", 
                                           ["1", "2", "3", "4", "5"]))
        
        # Get required resources
        print("\nResource Types:")
        for i, resource_type in enumerate(ResourceType):
            print(f"  {i+1}. {resource_type.name} - {resource_type.value}")
        
        resources_input = input("\nEnter required resource types (comma-separated numbers, e.g., 1,3,4): ").strip()
        resource_choices = [int(x.strip()) for x in resources_input.split(",")]
        required_resources = [list(ResourceType)[choice - 1].name for choice in resource_choices]
        
        # Get affected people
        affected_people = int(input("\nEnter number of people affected (0 if unknown): ").strip() or "0")
        
        # Get special factors
        print("\nSpecial Factors (select all that apply):")
        special_factors = [
            "children", "elderly", "disabled", "hazardous_materials", 
            "public_building", "multi_vehicle"
        ]
        
        for i, factor in enumerate(special_factors):
            print(f"  {i+1}. {factor}")
        
        factors_input = input("\nEnter special factors (comma-separated numbers, or 0 for none): ").strip()
        
        if factors_input == "0":
            selected_factors = []
        else:
            factor_choices = [int(x.strip()) for x in factors_input.split(",")]
            selected_factors = [special_factors[choice - 1] for choice in factor_choices]
        
        # Get additional details
        details = input("\nEnter additional details (optional): ").strip()
        
        # Create the incident
        incident = self.incident_manager.add_incident(
            incident_type, location, priority, required_resources,
            details, affected_people, selected_factors
        )
        
        print(f"\n{self.color_text('Success:', self.COLORS['GREEN'])} New incident created with ID #{incident.id}")
        print(f"Urgency Score: {incident.urgency_score:.2f}")
        
        # Ask about immediate allocation
        allocate = self.get_user_choice("\nAttempt to allocate resources now? (y/n): ", ["y", "n"])
        if allocate.lower() == "y":
            success = self.dispatcher.handle_new_incident(incident)
            if success:
                print(f"\n{self.color_text('Resources allocated successfully!', self.COLORS['GREEN'])}")
            else:
                print(f"\n{self.color_text('Not enough resources available for immediate allocation.', self.COLORS['YELLOW'])}")
                print("The incident has been queued for allocation when resources become available.")
        
        input("\nPress Enter to continue...")
    
    def add_resource(self) -> None:
        """
        Handle user input to add a new resource.
        """
        self.clear_screen()
        self.display_header("Add New Resource")
        
        # Display resource types
        print("\nResource Types:")
        for i, resource_type in enumerate(ResourceType):
            print(f"  {i+1}. {resource_type.name} - {resource_type.value}")
        
        # Get resource type
        type_choice = int(self.get_user_choice("\nSelect resource type (1-8): ", 
                                              [str(i) for i in range(1, 9)]))
        resource_type = list(ResourceType)[type_choice - 1]
        
        # Get location
        location = input("\nEnter resource location (e.g., Zone 3): ").strip()
        
        # Get capabilities
        capabilities_input = input("\nEnter special capabilities (comma-separated, or leave blank): ").strip()
        capabilities = [cap.strip() for cap in capabilities_input.split(",")] if capabilities_input else []
        
        # Create the resource
        resource = self.resource_manager.add_resource(resource_type, location, capabilities)
        
        print(f"\n{self.color_text('Success:', self.COLORS['GREEN'])} New resource created with ID {resource.id}")
        
        input("\nPress Enter to continue...")
    
    def view_incident_details(self) -> None:
        """
        Display detailed information about a specific incident.
        """
        self.clear_screen()
        self.display_header("Incident Details")
        
        # Get all incidents
        incidents = self.incident_manager.get_all_incidents()
        
        if not incidents:
            print("No incidents in the system.")
            input("\nPress Enter to continue...")
            return
        
        # Display brief list of incidents
        self.display_incidents(incidents)
        
        # Get incident ID
        id_input = input("\nEnter incident ID to view details (or 0 to cancel): ").strip()
        
        if id_input == "0":
            return
        
        try:
            incident_id = int(id_input)
            incident = self.incident_manager.get_incident(incident_id)
            
            if not incident:
                print(f"{self.color_text('Error:', self.COLORS['RED'])} Incident not found.")
                input("\nPress Enter to continue...")
                return
            
            # Display detailed information
            self.clear_screen()
            self.display_header(f"Details for Incident #{incident.id}")
            
            print(incident.get_details())
            
            # Show incident history
            print("\nIncident History:")
            for i, entry in enumerate(incident.history):
                timestamp = entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                print(f"  {i+1}. [{timestamp}] {entry['description']}")
            
            input("\nPress Enter to continue...")
            
        except ValueError:
            print(f"{self.color_text('Error:', self.COLORS['RED'])} Invalid incident ID.")
            input("\nPress Enter to continue...")
    
    def view_resource_details(self) -> None:
        """
        Display detailed information about a specific resource.
        """
        self.clear_screen()
        self.display_header("Resource Details")
        
        # Get all resources
        resources = self.resource_manager.get_all_resources()
        
        if not resources:
            print("No resources in the system.")
            input("\nPress Enter to continue...")
            return
        
        # Display brief list of resources
        self.display_resources(resources)
        
        # Get resource ID
        id_input = input("\nEnter resource ID to view details (or 0 to cancel): ").strip()
        
        if id_input == "0":
            return
        
        resource = self.resource_manager.get_resource(id_input)
        
        if not resource:
            print(f"{self.color_text('Error:', self.COLORS['RED'])} Resource not found.")
            input("\nPress Enter to continue...")
            return
        
        # Display detailed information
        self.clear_screen()
        self.display_header(f"Details for Resource {resource.id}")
        
        print(resource.get_details())
        
        # Show resource history
        print("\nResource History:")
        for i, entry in enumerate(resource.history):
            timestamp = entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {i+1}. [{timestamp}] {entry['status'].value} - {entry['description']}")
        
        input("\nPress Enter to continue...")
    
    def view_allocation_map(self) -> None:
        """
        Display the current resource allocation map.
        """
        self.clear_screen()
        self.display_header("Resource Allocation Map")
        
        allocation_map = self.dispatcher.allocation_map
        
        if not allocation_map:
            print("No resources currently allocated.")
            input("\nPress Enter to continue...")
            return
        
        # For each incident with allocations
        for incident_id, resources in allocation_map.items():
            incident = self.incident_manager.get_incident(incident_id)
            
            if not incident:
                continue
                
            # Display incident info with priority color
            priority_color = self.PRIORITY_COLORS[incident.priority]
            print(f"\n{self.color_text(f'Incident #{incident.id}:', priority_color)} "
                  f"{incident.incident_type.value} at {incident.location} "
                  f"(Priority: {incident.priority}, Status: {incident.status.value})")
            
            # Display assigned resources
            print("  Assigned Resources:")
            for resource in resources:
                print(f"    - {resource.resource_type.value} {resource.id} from {resource.location}")
                print(f"      Status: {resource.status.value}")
                
                # If resource is en route or on scene, show response time
                if resource.status in [ResourceStatus.EN_ROUTE, ResourceStatus.ASSIGNED]:
                    response_time = resource.calculate_response_time(incident.location)
                    print(f"      Estimated response time: {response_time} minutes")
        
        input("\nPress Enter to continue...")
    
    def perform_allocation(self) -> None:
        """
        Perform automatic resource allocation.
        """
        self.clear_screen()
        self.display_header("Automatic Resource Allocation")
        
        # Check if there are any incidents and resources
        if not self.incident_manager.get_all_incidents():
            print("No incidents in the system to allocate resources to.")
            input("\nPress Enter to continue...")
            return
            
        if not self.resource_manager.get_all_resources():
            print("No resources in the system to allocate.")
            input("\nPress Enter to continue...")
            return
        
        print("Starting automatic resource allocation...\n")
        
        # Get pre-allocation status
        pre_allocated = len(self.dispatcher.allocation_map)
        pre_unallocated = len([i for i in self.incident_manager.get_all_incidents() 
                             if i.status == IncidentStatus.REPORTED])
        
        # Run the allocation algorithm
        self.dispatcher.allocate_resources()
        
        # Get post-allocation status
        post_allocated = len(self.dispatcher.allocation_map)
        post_unallocated = len([i for i in self.incident_manager.get_all_incidents() 
                              if i.status == IncidentStatus.REPORTED])
        
        # Display results
        print(f"Allocation complete!\n")
        print(f"Incidents with resources before: {pre_allocated}")
        print(f"Incidents with resources after:  {post_allocated}")
        print(f"Waiting incidents before: {pre_unallocated}")
        print(f"Waiting incidents after:  {post_unallocated}")
        
        # Ask to view allocation map
        view_map = self.get_user_choice("\nView allocation map? (y/n): ", ["y", "n"])
        if view_map.lower() == "y":
            self.view_allocation_map()
        else:
            input("\nPress Enter to continue...")
    
    def run(self) -> None:
        """
        Main loop for the console UI.
        """
        running = True
        
        while running:
            self.display_menu()
            choice = self.get_user_choice("Enter your choice (0-6): ", [str(i) for i in range(7)])
            
            if choice == "0":
                running = False
            elif choice == "1":
                self.run_incidents_menu()
            elif choice == "2":
                self.run_resources_menu()
            elif choice == "3":
                self.run_allocation_menu()
            elif choice == "4":
                self.run_system_status_menu()
            elif choice == "5":
                self.run_advanced_menu()
            elif choice == "6":
                self.run_settings_menu()
        
        # Exit message
        self.clear_screen()
        print("\n" + "="*70)
        print(self.color_text("  THANK YOU FOR USING THE EMERGENCY RESOURCE ALLOCATION SYSTEM", 
                             self.COLORS['BOLD'] + self.COLORS['GREEN']))
        print("="*70 + "\n")
    
    def run_incidents_menu(self) -> None:
        """
        Run the incidents management menu loop.
        """
        while True:
            self.display_incidents_menu()
            choice = self.get_user_choice("Enter your choice (0-7): ", [str(i) for i in range(8)])
            
            if choice == "0":
                break
            elif choice == "1":
                self.add_incident()
            elif choice == "2":
                # Update incident implementation
                pass
            elif choice == "3":
                # View all incidents
                self.clear_screen()
                incidents = self.incident_manager.get_all_incidents()
                self.display_incidents(incidents)
                input("\nPress Enter to continue...")
            elif choice == "4":
                # View active incidents
                self.clear_screen()
                active = [i for i in self.incident_manager.get_all_incidents() 
                         if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]]
                self.display_incidents(active)
                input("\nPress Enter to continue...")
            elif choice == "5":
                self.view_incident_details()
            elif choice == "6":
                # Mark incident as resolved implementation
                pass
            elif choice == "7":
                # Cancel incident implementation
                pass
    
    def run_resources_menu(self) -> None:
        """
        Run the resources management menu loop.
        """
        while True:
            self.display_resources_menu()
            choice = self.get_user_choice("Enter your choice (0-8): ", [str(i) for i in range(9)])
            
            if choice == "0":
                break
            elif choice == "1":
                self.add_resource()
            elif choice == "2":
                # Update resource status implementation
                pass
            elif choice == "3":
                # Update resource location implementation
                pass
            elif choice == "4":
                # View all resources
                self.clear_screen()
                resources = self.resource_manager.get_all_resources()
                self.display_resources(resources)
                input("\nPress Enter to continue...")
            elif choice == "5":
                # View available resources
                self.clear_screen()
                available = self.resource_manager.get_available_resources()
                self.display_resources(available)
                input("\nPress Enter to continue...")
            elif choice == "6":
                self.view_resource_details()
            elif choice == "7":
                # Mark resource out of service implementation
                pass
            elif choice == "8":
                # Mark resource back in service implementation
                pass
    
    def run_allocation_menu(self) -> None:
        """
        Run the resource allocation menu loop.
        """
        while True:
            self.display_allocation_menu()
            choice = self.get_user_choice("Enter your choice (0-5): ", [str(i) for i in range(6)])
            
            if choice == "0":
                break
            elif choice == "1":
                self.perform_allocation()
            elif choice == "2":
                self.view_allocation_map()
            elif choice == "3":
                # Manually assign resource implementation
                pass
            elif choice == "4":
                # Release resource implementation
                pass
            elif choice == "5":
                # Reallocate all resources implementation
                pass
    
    def run_system_status_menu(self) -> None:
        """
        Run the system status menu loop.
        """
        while True:
            self.display_system_status_menu()
            choice = self.get_user_choice("Enter your choice (0-6): ", [str(i) for i in range(7)])
            
            if choice == "0":
                break
            # Other options implementations
    
    def run_advanced_menu(self) -> None:
        """
        Run the advanced options menu loop.
        """
        while True:
            self.display_advanced_menu()
            choice = self.get_user_choice("Enter your choice (0-6): ", [str(i) for i in range(7)])
            
            if choice == "0":
                break
            # Other options implementations
    
    def run_settings_menu(self) -> None:
        """
        Run the system settings menu loop.
        """
        while True:
            self.display_settings_menu()
            choice = self.get_user_choice("Enter your choice (0-4): ", [str(i) for i in range(5)])
            
            if choice == "0":
                break
            # Other options implementations