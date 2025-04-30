"""
Resource Model for Emergency Resource Allocation System.

This module defines the Resource class and related enums to represent
emergency resources such as ambulances, fire trucks, etc. Each resource 
has attributes such as type, location, and status, as well as methods to
update its status and calculate response times.
"""

import datetime
import math
from enum import Enum
from typing import List, Optional, Dict, Any, Union


class ResourceType(Enum):
    """
    Types of emergency resources.
    
    Each resource type represents a different kind of emergency response unit
    with specific capabilities and uses.
    """
    AMBULANCE = "Ambulance"
    FIRE_TRUCK = "Fire Truck"
    POLICE_UNIT = "Police Unit"
    RESCUE_TEAM = "Rescue Team"
    HAZMAT_UNIT = "Hazardous Materials Unit"
    MEDICAL_TEAM = "Medical Response Team"
    HELICOPTER = "Emergency Helicopter"
    COMMAND_UNIT = "Command and Control Unit"


class ResourceStatus(Enum):
    """
    Possible statuses for a resource.
    
    These statuses track the lifecycle of a resource from availability
    through assignment to an incident and back.
    """
    AVAILABLE = "Available for assignment"
    ASSIGNED = "Assigned to incident"
    EN_ROUTE = "En route to incident"
    ON_SCENE = "On scene at incident"
    RETURNING = "Returning to base"
    OUT_OF_SERVICE = "Out of service"
    MAINTENANCE = "Under maintenance"


class Resource:
    """
    Class representing an emergency resource that can be assigned to incidents.
    
    Resources are the units that respond to incidents, such as ambulances,
    fire trucks, and specialized teams. This class tracks their status,
    location, and assignment history.
    
    Attributes:
        id (str): Unique identifier for the resource
        resource_type (ResourceType): Type of resource
        location (str): Current location of the resource
        status (ResourceStatus): Current status of the resource
        current_incident (int): ID of incident resource is assigned to, if any
        capabilities (list): Special capabilities this resource has
        last_status_change (datetime): When status was last updated
        history (list): Record of status changes and assignments
    """
    
    def __init__(self, id: str, resource_type: Any, location: str, 
                 capabilities: Optional[List[str]] = None):
        """
        Initialize a new resource with the specified parameters.
        
        Args:
            id: Unique identifier for the resource
            resource_type: Type of resource (can be string or ResourceType enum)
            location: Current location of the resource
            capabilities: Special capabilities this resource has
        """
        # Basic identification and classification
        self.id = id
        
        # Convert string to enum if needed
        self.resource_type = resource_type if isinstance(resource_type, ResourceType) else ResourceType[resource_type]
        
        self.location = location
        
        # Status tracking
        self.status = ResourceStatus.AVAILABLE
        self.current_incident = None
        
        # Additional details
        self.capabilities = capabilities or []
        self.last_status_change = datetime.datetime.now()
        
        # Track assignment history and status changes
        self.history = []
        
        # Record initial status
        self._record_status_change("Initial status")
    
    def assign_to_incident(self, incident_id: int) -> bool:
        """
        Assign this resource to an incident.
        
        Args:
            incident_id: The ID of the incident to assign to
            
        Returns:
            bool: True if assignment was successful, False otherwise
        """
        # Can only assign if currently available or returning
        if self.status == ResourceStatus.AVAILABLE or self.status == ResourceStatus.RETURNING:
            self.current_incident = incident_id
            self.status = ResourceStatus.ASSIGNED
            self._record_status_change(f"Assigned to incident #{incident_id}")
            return True
        else:
            # Resource is not available for assignment
            return False
    
    def mark_en_route(self) -> bool:
        """
        Mark resource as en route to the incident.
        
        Returns:
            bool: True if status was updated, False otherwise
        """
        if self.status == ResourceStatus.ASSIGNED:
            self.status = ResourceStatus.EN_ROUTE
            self._record_status_change(f"En route to incident #{self.current_incident}")
            return True
        else:
            # Can only mark as en route if currently assigned
            return False
    
    def mark_on_scene(self) -> bool:
        """
        Mark resource as arrived on scene at the incident.
        
        Returns:
            bool: True if status was updated, False otherwise
        """
        if self.status == ResourceStatus.EN_ROUTE:
            self.status = ResourceStatus.ON_SCENE
            self._record_status_change(f"On scene at incident #{self.current_incident}")
            return True
        else:
            # Can only mark as on scene if currently en route
            return False
    
    def release(self) -> bool:
        """
        Release resource from current incident and mark as returning.
        
        Returns:
            bool: True if resource was successfully released, False otherwise
        """
        if self.status in [ResourceStatus.ASSIGNED, ResourceStatus.EN_ROUTE, ResourceStatus.ON_SCENE]:
            previous_incident = self.current_incident
            self.status = ResourceStatus.RETURNING
            self.current_incident = None
            self._record_status_change(f"Released from incident #{previous_incident}")
            return True
        else:
            # Resource is not assigned to an incident
            return False
    
    def mark_available(self) -> bool:
        """
        Mark resource as available again after returning.
        
        Returns:
            bool: True if status was updated, False otherwise
        """
        if self.status == ResourceStatus.RETURNING:
            self.status = ResourceStatus.AVAILABLE
            self._record_status_change("Marked available")
            return True
        else:
            # Can only mark as available if currently returning
            return False
    
    def mark_out_of_service(self, reason: str = "") -> 'Resource':
        """
        Mark resource as out of service.
        
        Args:
            reason: Reason for taking resource out of service
            
        Returns:
            self: For method chaining
        """
        self.status = ResourceStatus.OUT_OF_SERVICE
        self._record_status_change(f"Marked out of service: {reason}")
        return self
    
    def mark_in_maintenance(self) -> 'Resource':
        """
        Mark resource as in maintenance.
        
        Returns:
            self: For method chaining
        """
        self.status = ResourceStatus.MAINTENANCE
        self._record_status_change("In maintenance")
        return self
    
    def update_location(self, new_location: str) -> 'Resource':
        """
        Update the resource's location.
        
        Args:
            new_location: New location for the resource
            
        Returns:
            self: For method chaining
        """
        old_location = self.location
        self.location = new_location
        self._record_status_change(f"Location changed from {old_location} to {new_location}")
        return self
    
    def _record_status_change(self, description: str) -> None:
        """
        Record status change in history.
        
        This private method maintains a log of all changes to the resource's
        status, which is useful for auditing and analysis.
        
        Args:
            description: Description of what changed
        """
        self.last_status_change = datetime.datetime.now()
        self.history.append({
            "timestamp": self.last_status_change,
            "status": self.status,
            "description": description
        })
    
    def calculate_response_time(self, incident_location: str) -> int:
        """
        Calculate estimated response time to an incident location.
        
        This is a simplified version using zone distance as a proxy.
        In a real-world scenario, this would use actual geographical data,
        traffic conditions, and other factors.
        
        Args:
            incident_location: Location of the incident
            
        Returns:
            int: Estimated response time in minutes
        """
        # Simple location format: "Zone X"
        # Extract zone numbers and calculate simple distance
        try:
            # Handle numeric zones
            if "Zone" in self.location and "Zone" in incident_location:
                current_zone = int(self.location.split("Zone ")[1])
                target_zone = int(incident_location.split("Zone ")[1])
                zone_distance = abs(current_zone - target_zone)
                
                # Assume 5 minutes per zone difference for travel time
                minutes = 5 * zone_distance
                
                # Add 2 minutes if resource is not already available (preparation time)
                if self.status != ResourceStatus.AVAILABLE:
                    minutes += 2
                
                return minutes
            else:
                # If zones aren't numeric, return a default value
                return 15  # Default 15 minutes response time
        except:
            # If any error in calculation, return default
            return 15
    
    def __str__(self) -> str:
        """
        Get string representation of the resource for basic display.
        
        Returns:
            str: Basic string representation
        """
        return (f"{self.resource_type.value} {self.id} at {self.location} - "
                f"{self.status.value}")
    
    def get_details(self) -> str:
        """
        Get detailed information about the resource for comprehensive display.
        
        Returns:
            str: Multi-line string with all resource details
        """
        # Calculate time in current status
        time_in_status = (datetime.datetime.now() - self.last_status_change).total_seconds() / 60  # minutes
        
        # Build detailed string
        details = (
            f"{self.resource_type.value} (ID: {self.id})\n"
            f"Status: {self.status.value}\n"
            f"Location: {self.location}\n"
            f"Time in current status: {int(time_in_status)} minutes\n"
        )
        
        # Add incident assignment if applicable
        if self.current_incident:
            details += f"Assigned to: Incident #{self.current_incident}\n"
        
        # Add capabilities if available
        if self.capabilities:
            capabilities_str = ", ".join(self.capabilities)
            details += f"Special capabilities: {capabilities_str}\n"
        
        return details