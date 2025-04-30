"""
Incident Manager for Emergency Resource Allocation System.

This module expands on the basic incident management functionality.
It provides methods for adding, updating, retrieving, and filtering incidents.
"""

from typing import List, Dict, Any, Optional, Union
from src.models.incident import Incident, IncidentType, IncidentStatus


class IncidentManager:
    """
    Class for managing all incidents in the system.
    
    The IncidentManager maintains a collection of all incidents and provides
    methods for adding, updating, retrieving, and filtering incidents based on
    various criteria.
    
    Attributes:
        incidents (dict): Dictionary of incidents by ID
        next_id (int): Counter for auto-generating incident IDs
    """
    
    def __init__(self):
        """Initialize the incident manager with an empty incident collection."""
        self.incidents = {}  # Dictionary of incidents by ID
        self.next_id = 1  # Starting ID for auto-generation
    
    def add_incident(self, incident_type: Union[str, IncidentType], 
                    location: str, 
                    priority: int, 
                    required_resources: List[str], 
                    details: str = "", 
                    affected_people: int = 0, 
                    special_factors: Optional[List[str]] = None, 
                    incident_id: Optional[int] = None) -> Incident:
        """
        Add a new incident to the system.
        
        Args:
            incident_type: Type of incident (string or IncidentType enum)
            location: Location of the incident
            priority: Priority level (1-5, where 1 is highest)
            required_resources: List of required resource types
            details: Additional details about the incident
            affected_people: Number of people affected
            special_factors: Special considerations
            incident_id: Optional ID (auto-generated if not provided)
            
        Returns:
            Incident: The newly created incident
        """
        # Auto-generate ID if not provided
        if incident_id is None:
            incident_id = self.next_id
            self.next_id += 1
        
        # Create and add the incident
        incident = Incident(
            incident_id, 
            incident_type, 
            location, 
            priority, 
            required_resources, 
            details, 
            affected_people, 
            special_factors
        )
        
        self.incidents[incident_id] = incident
        return incident
    
    def update_incident(self, incident_id: int, **kwargs) -> Optional[Incident]:
        """
        Update an existing incident with new values.
        
        Args:
            incident_id: ID of the incident to update
            **kwargs: Attributes to update
            
        Returns:
            Incident: The updated incident, or None if not found
        """
        incident = self.get_incident(incident_id)
        
        if not incident:
            return None
            
        # Update attributes
        for key, value in kwargs.items():
            if key == 'priority':
                incident.update_priority(value)
            elif key == 'status':
                incident.update_status(value)
            elif key in ['location', 'details', 'affected_people', 'special_factors']:
                setattr(incident, key, value)
                # Recalculate urgency score if relevant attributes changed
                incident.urgency_score = incident.calculate_urgency_score()
                
        return incident
    
    def remove_incident(self, incident_id: int) -> bool:
        """
        Remove an incident from the system.
        
        Args:
            incident_id: ID of the incident to remove
            
        Returns:
            bool: True if removal was successful, False if incident not found
        """
        if incident_id in self.incidents:
            del self.incidents[incident_id]
            return True
        return False
    
    def get_incident(self, incident_id: int) -> Optional[Incident]:
        """
        Get a specific incident by ID.
        
        Args:
            incident_id: ID of the incident to retrieve
            
        Returns:
            Incident: The requested incident, or None if not found
        """
        return self.incidents.get(incident_id)
    
    def get_all_incidents(self) -> List[Incident]:
        """
        Get all incidents in the system.
        
        Returns:
            list: All incidents
        """
        return list(self.incidents.values())
    
    def get_active_incidents(self) -> List[Incident]:
        """
        Get all active (non-resolved, non-cancelled) incidents.
        
        Returns:
            list: Active incidents
        """
        return [i for i in self.incidents.values() 
                if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]]
    
    def get_incidents_by_priority(self, priority: int) -> List[Incident]:
        """
        Get incidents with a specific priority level.
        
        Args:
            priority: Priority level to filter by
            
        Returns:
            list: Incidents with the specified priority
        """
        return [i for i in self.incidents.values() if i.priority == priority]
    
    def get_incidents_by_type(self, incident_type: Union[str, IncidentType]) -> List[Incident]:
        """
        Get incidents of a specific type.
        
        Args:
            incident_type: Type to filter by
            
        Returns:
            list: Incidents of the specified type
        """
        if isinstance(incident_type, str) and incident_type in [t.name for t in IncidentType]:
            incident_type = IncidentType[incident_type]
            
        return [i for i in self.incidents.values() if i.incident_type == incident_type]
    
    def get_incidents_by_status(self, status: Union[str, IncidentStatus]) -> List[Incident]:
        """
        Get incidents with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            list: Incidents with the specified status
        """
        if isinstance(status, str) and status in [s.name for s in IncidentStatus]:
            status = IncidentStatus[status]
            
        return [i for i in self.incidents.values() if i.status == status]
    
    def get_incidents_by_location(self, location: str) -> List[Incident]:
        """
        Get incidents at a specific location.
        
        Args:
            location: Location to filter by
            
        Returns:
            list: Incidents at the specified location
        """
        return [i for i in self.incidents.values() if i.location == location]
    
    def get_incidents_requiring_resource(self, resource_type: str) -> List[Incident]:
        """
        Get incidents that require a specific resource type.
        
        Args:
            resource_type: Resource type to filter by
            
        Returns:
            list: Incidents requiring the specified resource
        """
        return [i for i in self.incidents.values() 
                if resource_type in i.required_resources]
    
    def get_highest_priority_incidents(self, count: int = 5) -> List[Incident]:
        """
        Get the highest priority incidents.
        
        Args:
            count: Maximum number of incidents to return
            
        Returns:
            list: Highest priority incidents
        """
        # Sort by urgency score (descending) and then by timestamp (ascending)
        sorted_incidents = sorted(
            self.get_active_incidents(),
            key=lambda i: (-i.urgency_score, i.timestamp)
        )
        
        return sorted_incidents[:count]
    
    def mark_incident_resolved(self, incident_id: int) -> bool:
        """
        Mark an incident as resolved.
        
        Args:
            incident_id: ID of the incident to resolve
            
        Returns:
            bool: True if successful, False if incident not found
        """
        incident = self.get_incident(incident_id)
        
        if not incident:
            return False
            
        incident.update_status(IncidentStatus.RESOLVED)
        return True
    
    def mark_incident_cancelled(self, incident_id: int) -> bool:
        """
        Mark an incident as cancelled.
        
        Args:
            incident_id: ID of the incident to cancel
            
        Returns:
            bool: True if successful, False if incident not found
        """
        incident = self.get_incident(incident_id)
        
        if not incident:
            return False
            
        incident.update_status(IncidentStatus.CANCELLED)
        return True
    
    def __str__(self) -> str:
        """
        Get string representation of the incident manager.
        
        Returns:
            str: String representation
        """
        active = len(self.get_active_incidents())
        total = len(self.incidents)
        return f"Incident Manager: {active} active incidents, {total} total"