"""
Incident Model for Emergency Resource Allocation System.

This module defines the Incident class and related enums to represent
emergency incidents within the system. Each incident has attributes such as
type, location, priority, and required resources, as well as methods to
update its status and calculate its urgency score.
"""

import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class IncidentType(Enum):
    """
    Types of emergency incidents.
    
    Each incident type represents a different kind of emergency situation
    that would require specific types of resources and handling.
    """
    FIRE = "Fire emergency"
    MEDICAL = "Medical emergency"
    TRAFFIC = "Traffic accident"
    HAZMAT = "Hazardous materials"
    RESCUE = "Rescue operation"
    DISASTER = "Natural disaster"
    OTHER = "Other emergency"


class IncidentStatus(Enum):
    """
    Possible statuses for an incident.
    
    These statuses track the lifecycle of an incident from initial reporting
    through resource assignment to resolution.
    """
    REPORTED = "Reported - Waiting for resources"
    ASSIGNED = "Resources assigned"
    PARTIAL = "Partially resourced"
    IN_PROGRESS = "In progress"
    RESOLVED = "Resolved"
    CANCELLED = "Cancelled"


class Incident:
    """
    Class representing an emergency incident that requires resources.
    
    The Incident class is a core part of the system, representing emergency
    situations that need resources. It tracks not just basic information about
    the incident but also calculates a sophisticated urgency score that helps
    prioritize resource allocation.
    
    Attributes:
        id (int): Unique identifier for the incident
        incident_type (IncidentType): Type of emergency
        location (str): Location of the incident (e.g. "Zone 3")
        priority (int): Priority level from 1 (highest) to 5 (lowest)
        required_resources (list): List of resource types needed
        status (IncidentStatus): Current status of the incident
        timestamp (datetime): When the incident was reported
        details (str): Additional details about the incident
        affected_people (int): Estimated number of people affected
        special_factors (list): Special considerations like "children", "elderly", etc.
        assigned_resources (list): Resources currently assigned to this incident
        urgency_score (float): Calculated score based on multiple factors
    """
    
    def __init__(self, id: int, incident_type: Any, location: str, priority: int, 
                 required_resources: List[str], details: str = "", 
                 affected_people: int = 0, special_factors: Optional[List[str]] = None):
        """
        Initialize a new incident with the specified parameters.
        
        Args:
            id: Unique identifier for the incident
            incident_type: Type of emergency (can be string or IncidentType enum)
            location: Location of the incident (e.g. "Zone 3")
            priority: Priority level from 1 (highest) to 5 (lowest)
            required_resources: List of resource types needed
            details: Additional details about the incident
            affected_people: Estimated number of people affected
            special_factors: Special considerations like "children", "elderly", etc.
        """
        # Basic identification and classification
        self.id = id
        
        # Convert string to enum if needed
        self.incident_type = incident_type if isinstance(incident_type, IncidentType) else IncidentType[incident_type]
        
        self.location = location
        self.priority = priority
        self.required_resources = required_resources
        
        # Status tracking
        self.status = IncidentStatus.REPORTED
        self.timestamp = datetime.datetime.now()
        
        # Additional details that affect priority calculation
        self.details = details
        self.affected_people = affected_people
        self.special_factors = special_factors or []
        
        # Resource tracking
        self.assigned_resources = []
        
        # Calculate initial urgency score based on all factors
        self.urgency_score = self.calculate_urgency_score()
        
        # For tracking how the incident changes over time
        self.history = [{
            "timestamp": self.timestamp,
            "status": self.status,
            "description": "Incident reported",
            "urgency_score": self.urgency_score
        }]
    
    def update_priority(self, new_priority: int):
        """
        Update the incident's priority level and recalculate urgency score.
        
        Args:
            new_priority: New priority level (1-5)
            
        Returns:
            self: For method chaining
        """
        old_priority = self.priority
        self.priority = new_priority
        self.urgency_score = self.calculate_urgency_score()
        
        # Record the change in history
        self._record_change(f"Priority changed from {old_priority} to {new_priority}")
        
        return self
    
    def update_status(self, new_status: Any):
        """
        Update the incident's status.
        
        Args:
            new_status: New status (can be string name or IncidentStatus enum)
            
        Returns:
            self: For method chaining
            
        Raises:
            ValueError: If the status is invalid
        """
        # Handle string status names
        if isinstance(new_status, str) and new_status in [s.name for s in IncidentStatus]:
            old_status = self.status
            self.status = IncidentStatus[new_status]
            self._record_change(f"Status changed from {old_status.value} to {self.status.value}")
        # Handle enum values
        elif isinstance(new_status, IncidentStatus):
            old_status = self.status
            self.status = new_status
            self._record_change(f"Status changed from {old_status.value} to {self.status.value}")
        else:
            raise ValueError(f"Invalid status: {new_status}")
            
        return self
    
    def add_resource(self, resource):
        """
        Associate a resource with this incident.
        
        Args:
            resource: The resource object to assign
            
        Returns:
            self: For method chaining
        """
        self.assigned_resources.append(resource)
        
        # Update status based on resource assignment
        if len(self.assigned_resources) >= len(self.required_resources):
            self.update_status(IncidentStatus.ASSIGNED)
        elif self.assigned_resources:
            self.update_status(IncidentStatus.PARTIAL)
            
        self._record_change(f"Resource {resource.id} assigned to incident")
        
        return self
    
    def remove_resource(self, resource_id: str):
        """
        Remove a resource from this incident.
        
        Args:
            resource_id: ID of the resource to remove
            
        Returns:
            self: For method chaining
        """
        # Filter out the resource with the matching ID
        old_count = len(self.assigned_resources)
        self.assigned_resources = [r for r in self.assigned_resources if r.id != resource_id]
        
        # If a resource was actually removed...
        if len(self.assigned_resources) < old_count:
            self._record_change(f"Resource {resource_id} removed from incident")
            
            # Update status based on remaining resources
            if not self.assigned_resources:
                self.update_status(IncidentStatus.REPORTED)
            elif len(self.assigned_resources) < len(self.required_resources):
                self.update_status(IncidentStatus.PARTIAL)
                
        return self
    
    def _record_change(self, description: str):
        """
        Record a change to the incident in the history.
        
        Args:
            description: Description of what changed
        """
        self.history.append({
            "timestamp": datetime.datetime.now(),
            "status": self.status,
            "description": description,
            "urgency_score": self.urgency_score
        })
    
    def calculate_urgency_score(self) -> float:
        """
        Calculate an urgency score based on multiple factors.
        
        This provides a more nuanced priority ranking than just the basic level.
        The score considers incident type, priority level, affected people,
        special factors, and time waiting.
        
        Returns:
            float: The calculated urgency score (higher = more urgent)
        """
        # Start with base score from priority (1-5 maps to 80-0)
        # Priority 1 = 80, Priority 5 = 0
        score = 100 - (self.priority * 20)
        
        # Adjust for incident type severity
        # Different types of incidents have different base urgency levels
        type_weights = {
            IncidentType.FIRE: 15,         # Fires can spread rapidly
            IncidentType.MEDICAL: 20,      # Medical emergencies are often life-threatening
            IncidentType.TRAFFIC: 10,      # Traffic accidents vary in severity
            IncidentType.HAZMAT: 25,       # Hazardous materials pose wide threats
            IncidentType.RESCUE: 20,       # Rescue operations are often time-critical
            IncidentType.DISASTER: 30,     # Natural disasters affect many people
            IncidentType.OTHER: 5          # Other emergencies vary widely
        }
        score += type_weights.get(self.incident_type, 0)
        
        # Adjust for number of people affected
        # More people affected = higher urgency, but cap the bonus
        if self.affected_people > 0:
            score += min(20, self.affected_people * 2)  # Cap at +20
        
        # Adjust for special factors that might increase urgency
        special_factor_weights = {
            "children": 15,               # Children are vulnerable
            "elderly": 10,                # Elderly may need special assistance
            "disabled": 10,               # Disabled people may need extra help
            "hazardous_materials": 15,    # Hazmat situations can escalate
            "public_building": 5,         # Public buildings affect more people
            "multi_vehicle": 5            # Multi-vehicle accidents are complex
        }
        
        for factor in self.special_factors:
            score += special_factor_weights.get(factor, 0)
        
        # Adjust for time waiting - incidents get more urgent as they wait
        # This prevents low-priority incidents from being ignored indefinitely
        time_waiting = (datetime.datetime.now() - self.timestamp).total_seconds() / 60  # minutes
        score += min(10, time_waiting / 10)  # Up to +10 for waiting (1 point per 10 minutes, max 10)
        
        return score
    
    def __str__(self) -> str:
        """
        Get string representation of the incident for basic display.
        
        Returns:
            str: Basic string representation
        """
        return (f"Incident #{self.id}: {self.incident_type.value} at {self.location} "
                f"(Priority: {self.priority}, Status: {self.status.value})")
    
    def get_details(self) -> str:
        """
        Get detailed information about the incident for comprehensive display.
        
        Returns:
            str: Multi-line string with all incident details
        """
        # Format required resources list
        resources_str = ", ".join(self.required_resources)
        
        # Format assigned resources list
        assigned_str = ", ".join([r.id for r in self.assigned_resources]) if self.assigned_resources else "None"
        
        # Calculate waiting time
        time_waiting = (datetime.datetime.now() - self.timestamp).total_seconds() / 60  # minutes
        
        # Build detailed string
        return (
            f"Incident #{self.id}\n"
            f"Type: {self.incident_type.value}\n"
            f"Location: {self.location}\n"
            f"Priority: {self.priority} (Urgency Score: {self.urgency_score:.2f})\n"
            f"Status: {self.status.value}\n"
            f"Reported: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({int(time_waiting)} minutes ago)\n"
            f"Required Resources: {resources_str}\n"
            f"Assigned Resources: {assigned_str}\n"
            f"People Affected: {self.affected_people}\n"
            f"Special Factors: {', '.join(self.special_factors) if self.special_factors else 'None'}\n"
            f"Details: {self.details}"
        )