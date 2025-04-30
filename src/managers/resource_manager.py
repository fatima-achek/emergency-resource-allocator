"""
Resource Manager for Emergency Resource Allocation System.

This module expands on the basic resource management functionality.
It provides methods for adding, updating, retrieving, and filtering resources.
"""

from typing import List, Dict, Any, Optional, Union
from src.models.resource import Resource, ResourceType, ResourceStatus
from src.models.incident import IncidentType


class ResourceManager:
    """
    Class for managing all emergency resources in the system.
    
    The ResourceManager maintains a collection of all resources and provides
    methods for adding, updating, retrieving, and filtering resources based on
    various criteria.
    
    Attributes:
        resources (dict): Dictionary of resources by ID
        next_id (int): Counter for auto-generating resource IDs
    """
    
    def __init__(self):
        """Initialize the resource manager with an empty resource collection."""
        self.resources = {}  # Dictionary of resources by ID
        self.next_id = 1000  # Starting ID for auto-generation
    
    def add_resource(self, resource_type: Union[str, ResourceType], 
                    location: str, 
                    capabilities: Optional[List[str]] = None, 
                    resource_id: Optional[str] = None) -> Resource:
        """
        Add a new resource to the system.
        
        Args:
            resource_type: Type of resource (string or ResourceType enum)
            location: Current location of the resource
            capabilities: Special capabilities of the resource
            resource_id: Optional ID (auto-generated if not provided)
            
        Returns:
            Resource: The newly created resource
        """
        # Auto-generate ID if not provided
        if resource_id is None:
            # Get prefix from resource type
            if isinstance(resource_type, str):
                prefix = resource_type[:2].upper()
            else:
                prefix = resource_type.name[:2]
                
            resource_id = f"{prefix}{self.next_id}"
            self.next_id += 1
        
        # Create and add the resource
        resource = Resource(resource_id, resource_type, location, capabilities)
        self.resources[resource_id] = resource
        return resource
    
    def remove_resource(self, resource_id: str) -> bool:
        """
        Remove a resource from the system.
        
        Args:
            resource_id: ID of the resource to remove
            
        Returns:
            bool: True if removal was successful, False if resource not found
        """
        if resource_id in self.resources:
            del self.resources[resource_id]
            return True
        return False
    
    def update_resource(self, resource_id: str, **kwargs) -> Optional[Resource]:
        """
        Update an existing resource with new values.
        
        Args:
            resource_id: ID of the resource to update
            **kwargs: Attributes to update
            
        Returns:
            Resource: The updated resource, or None if not found
        """
        resource = self.get_resource(resource_id)
        
        if not resource:
            return None
            
        # Update attributes
        for key, value in kwargs.items():
            if key == 'status':
                if value == ResourceStatus.AVAILABLE:
                    resource.mark_available()
                elif value == ResourceStatus.OUT_OF_SERVICE:
                    resource.mark_out_of_service()
                elif value == ResourceStatus.MAINTENANCE:
                    resource.mark_in_maintenance()
            elif key == 'location':
                resource.update_location(value)
                
        return resource
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """
        Get a specific resource by ID.
        
        Args:
            resource_id: ID of the resource to retrieve
            
        Returns:
            Resource: The requested resource, or None if not found
        """
        return self.resources.get(resource_id)
    
    def get_all_resources(self) -> List[Resource]:
        """
        Get all resources in the system.
        
        Returns:
            list: All resources
        """
        return list(self.resources.values())
    
    def get_available_resources(self) -> List[Resource]:
        """
        Get all resources currently available for assignment.
        
        Returns:
            list: Available resources
        """
        return [r for r in self.resources.values() if r.status == ResourceStatus.AVAILABLE]
    
    def get_resources_by_type(self, resource_type: Union[str, ResourceType]) -> List[Resource]:
        """
        Get all resources of a specific type.
        
        Args:
            resource_type: Type to filter by
            
        Returns:
            list: Resources of the specified type
        """
        if isinstance(resource_type, str) and resource_type in [rt.name for rt in ResourceType]:
            resource_type = ResourceType[resource_type]
        
        return [r for r in self.resources.values() if r.resource_type == resource_type]
    
    def get_resources_by_location(self, location: str) -> List[Resource]:
        """
        Get all resources at a specific location.
        
        Args:
            location: Location to filter by
            
        Returns:
            list: Resources at the specified location
        """
        return [r for r in self.resources.values() if r.location == location]
    
    def get_resources_by_status(self, status: Union[str, ResourceStatus]) -> List[Resource]:
        """
        Get all resources with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            list: Resources with the specified status
        """
        if isinstance(status, str) and status in [s.name for s in ResourceStatus]:
            status = ResourceStatus[status]
        
        return [r for r in self.resources.values() if r.status == status]
    
    def get_resources_by_capability(self, capability: str) -> List[Resource]:
        """
        Get all resources with a specific capability.
        
        Args:
            capability: Capability to filter by
            
        Returns:
            list: Resources with the specified capability
        """
        return [r for r in self.resources.values() if capability in r.capabilities]
    
    def get_resources_for_incident_type(self, incident_type: Union[str, IncidentType]) -> Dict[ResourceType, List[Resource]]:
        """
        Get resources suitable for a specific incident type.
        
        Args:
            incident_type: Incident type to get resources for
            
        Returns:
            dict: Dictionary mapping resource types to lists of suitable resources
        """
        suitable_resources = {}
        
        # Define resource types needed for each incident type
        resource_mapping = {
            IncidentType.FIRE: [ResourceType.FIRE_TRUCK, ResourceType.COMMAND_UNIT],
            IncidentType.MEDICAL: [ResourceType.AMBULANCE, ResourceType.MEDICAL_TEAM],
            IncidentType.TRAFFIC: [ResourceType.POLICE_UNIT, ResourceType.AMBULANCE],
            IncidentType.HAZMAT: [ResourceType.HAZMAT_UNIT, ResourceType.FIRE_TRUCK],
            IncidentType.RESCUE: [ResourceType.RESCUE_TEAM, ResourceType.AMBULANCE],
            IncidentType.DISASTER: [ResourceType.COMMAND_UNIT, ResourceType.RESCUE_TEAM, 
                                    ResourceType.MEDICAL_TEAM, ResourceType.FIRE_TRUCK],
            IncidentType.OTHER: [ResourceType.POLICE_UNIT]
        }
        
        if isinstance(incident_type, str) and incident_type in [t.name for t in IncidentType]:
            incident_type = IncidentType[incident_type]
        
        needed_types = resource_mapping.get(incident_type, [])
        
        for resource_type in needed_types:
            suitable_resources[resource_type] = self.get_resources_by_type(resource_type)
        
        return suitable_resources
    
    def get_nearest_resources(self, location: str, resource_type: Union[str, ResourceType], count: int = 1) -> List[Resource]:
        """
        Get the nearest resources of a specific type to a location.
        
        Args:
            location: Target location
            resource_type: Type of resource to find
            count: Number of resources to return
            
        Returns:
            list: Nearest resources of the specified type
        """
        resources = self.get_resources_by_type(resource_type)
        
        # Sort by calculated response time to the location
        sorted_resources = sorted(resources, key=lambda r: r.calculate_response_time(location))
        
        return sorted_resources[:count]
    
    def mark_resource_out_of_service(self, resource_id: str, reason: str = "") -> bool:
        """
        Mark a resource as out of service.
        
        Args:
            resource_id: ID of the resource to mark
            reason: Reason for taking out of service
            
        Returns:
            bool: True if successful, False if resource not found
        """
        resource = self.get_resource(resource_id)
        
        if not resource:
            return False
            
        resource.mark_out_of_service(reason)
        return True
    
    def mark_resource_in_service(self, resource_id: str) -> bool:
        """
        Mark a resource as back in service (available).
        
        Args:
            resource_id: ID of the resource to mark
            
        Returns:
            bool: True if successful, False if resource not found or not applicable
        """
        resource = self.get_resource(resource_id)
        
        if not resource:
            return False
            
        if resource.status == ResourceStatus.OUT_OF_SERVICE or resource.status == ResourceStatus.MAINTENANCE:
            # Resource is currently out of service, make it available
            resource.status = ResourceStatus.AVAILABLE
            resource._record_status_change("Marked back in service")
            return True
        else:
            # Can't mark as in service if not out of service
            return False
    
    def __str__(self) -> str:
        """
        Get string representation of the resource manager.
        
        Returns:
            str: String representation
        """
        available = len(self.get_available_resources())
        total = len(self.resources)
        return f"Resource Manager: {available} available resources, {total} total"