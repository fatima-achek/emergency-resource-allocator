"""
Dispatcher Module for Emergency Resource Allocation System.

This module contains the Dispatcher class, which implements the core allocation
algorithm for assigning resources to incidents. It handles both initial allocation
and reallocation when higher priority incidents arise.
"""

import datetime
from typing import List, Dict, Any, Tuple, Optional, Set

from src.models.incident import Incident, IncidentStatus
from src.models.resource import Resource, ResourceStatus
from src.algorithms.priority_queue import IncidentPriorityQueue


class Dispatcher:
    """
    The Dispatcher class handles resource allocation decisions.
    
    The dispatcher is responsible for assigning resources to incidents based on
    priority, proximity, and availability. It also handles reallocation when
    higher priority incidents arise.
    
    Attributes:
        incident_manager: Reference to the system's incident manager
        resource_manager: Reference to the system's resource manager
        priority_queue: Queue of incidents prioritized by urgency
        allocation_map: Current mapping of incident IDs to assigned resources
        logger: Logger for recording allocation decisions
    """
    
    def __init__(self, incident_manager, resource_manager, logger=None):
        """
        Initialize the dispatcher with necessary dependencies.
        
        Args:
            incident_manager: Reference to the incident manager
            resource_manager: Reference to the resource manager
            logger: Optional logger for recording allocation decisions
        """
        self.incident_manager = incident_manager
        self.resource_manager = resource_manager
        self.priority_queue = IncidentPriorityQueue()
        self.allocation_map = {}  # Maps incident IDs to list of assigned resources
        self.logger = logger
        
        # Initialize the priority queue with existing incidents
        for incident in self.incident_manager.get_all_incidents():
            if incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]:
                self.priority_queue.add_incident(incident)
    
    def _log(self, message: str) -> None:
        """
        Log a message if a logger is available.
        
        Args:
            message: The message to log
        """
        if self.logger:
            self.logger.log_action(message)
        print(f"[Dispatcher] {message}")
    
    def allocate_resources(self, recalculate_all: bool = False) -> Dict[int, List[Resource]]:
        """
        Allocate resources to incidents based on priority and availability.
        
        This is the main allocation algorithm that assigns available resources
        to incidents based on their priority, required resource types, and proximity.
        
        Args:
            recalculate_all: Whether to recalculate all allocations (default: False)
            
        Returns:
            dict: Mapping of incident IDs to list of assigned resources
        """
        self._log("Starting resource allocation...")
        
        # Clear existing allocations if doing a full recalculation
        if recalculate_all:
            self._log("Performing full reallocation of all resources")
            # Release all resources and clear allocation map
            for resources in self.allocation_map.values():
                for resource in resources:
                    resource.release()
                    resource.mark_available()
            self.allocation_map = {}
        
        # Get all active incidents sorted by priority
        # We'll use our priority queue to get incidents in urgency order
        active_incidents = []
        while not self.priority_queue.is_empty():
            incident = self.priority_queue.pop_highest_priority()
            if incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]:
                active_incidents.append(incident)
        
        # Re-add incidents to the queue (since we removed them above)
        for incident in active_incidents:
            self.priority_queue.add_incident(incident)
            
        self._log(f"Processing {len(active_incidents)} active incidents")
            
        # Allocate resources to each incident in priority order
        for incident in active_incidents:
            # Skip incidents that already have resources unless we're recalculating all
            if incident.id in self.allocation_map and not recalculate_all:
                continue
                
            # Skip resolved or cancelled incidents
            if incident.status in [IncidentStatus.RESOLVED, IncidentStatus.CANCELLED]:
                continue
                
            self._log(f"Allocating resources for Incident #{incident.id} (Priority: {incident.priority}, "
                     f"Urgency: {incident.urgency_score:.2f})")
            
            # Get available resources
            available_resources = self.resource_manager.get_available_resources()
            
            # Find suitable resources for this incident
            suitable_resources = self._find_suitable_resources(
                incident, 
                available_resources
            )
            
            if suitable_resources:
                # We found suitable resources, assign them
                self._log(f"Found {len(suitable_resources)} suitable resources for Incident #{incident.id}")
                self._assign_resources_to_incident(incident, suitable_resources)
            else:
                # No suitable resources available, try reallocation
                self._log(f"No suitable resources available for Incident #{incident.id}")
                self._try_reallocation(incident)
        
        return self.allocation_map
    
    def _find_suitable_resources(self, incident: Incident, available_resources: List[Resource]) -> List[Resource]:
        """
        Find suitable resources for an incident based on type, proximity, and availability.
        
        This method implements the logic for matching resources to incidents based on:
        1. Required resource types
        2. Proximity (travel time)
        3. Resource capabilities
        
        Args:
            incident: The incident needing resources
            available_resources: List of currently available resources
            
        Returns:
            list: List of suitable resources
        """
        suitable_resources = []
        
        # Group available resources by type
        resources_by_type = {}
        for resource in available_resources:
            resource_type = resource.resource_type.name
            if resource_type not in resources_by_type:
                resources_by_type[resource_type] = []
            resources_by_type[resource_type].append(resource)
        
        # For each required resource type, find the best resource
        for required_type in incident.required_resources:
            if required_type in resources_by_type and resources_by_type[required_type]:
                # Find the closest resource of this type
                best_resource = min(
                    resources_by_type[required_type],
                    key=lambda r: r.calculate_response_time(incident.location)
                )
                
                # Add to our suitable resources list
                suitable_resources.append(best_resource)
                
                # Remove from available list to avoid double-assignment
                resources_by_type[required_type].remove(best_resource)
            else:
                # If we can't find one of the required types, we don't have suitable resources
                self._log(f"  Missing required resource type: {required_type}")
                return []
        
        return suitable_resources
    
    def _assign_resources_to_incident(self, incident: Incident, resources: List[Resource]) -> None:
        """
        Assign resources to an incident and update allocation map.
        
        Args:
            incident: The incident to assign resources to
            resources: List of resources to assign
        """
        # Update allocation map
        self.allocation_map[incident.id] = resources
        
        # Assign each resource to the incident
        for resource in resources:
            resource.assign_to_incident(incident.id)
            incident.add_resource(resource)
            self._log(f"  Assigned {resource.resource_type.value} {resource.id} to Incident #{incident.id}")
        
        # Update incident status
        if len(resources) >= len(incident.required_resources):
            incident.update_status(IncidentStatus.ASSIGNED)
        else:
            incident.update_status(IncidentStatus.PARTIAL)
    
    def _try_reallocation(self, critical_incident: Incident) -> bool:
        """
        Try to reallocate resources from lower priority incidents.
        
        This is the core reallocation algorithm that handles the case when a high-priority
        incident needs resources but none are available. It identifies lower priority incidents
        that have resources that could be reassigned.
        
        Args:
            critical_incident: The high-priority incident needing resources
            
        Returns:
            bool: True if reallocation was successful, False otherwise
        """
        self._log(f"Attempting to reallocate resources for critical Incident #{critical_incident.id}")
        
        # Find lower priority incidents with resources we can reassign
        potential_resources = []
        
        for incident_id, resources in self.allocation_map.items():
            # Skip the incident we're trying to allocate for
            if incident_id == critical_incident.id:
                continue
                
            incident = self.incident_manager.get_incident(incident_id)
            
            # Only reallocate from lower priority incidents
            # Compare urgency scores rather than simple priority levels
            if incident.urgency_score < critical_incident.urgency_score:
                for resource in resources:
                    # Check if this resource's type is one we need
                    if resource.resource_type.name in critical_incident.required_resources:
                        potential_resources.append((resource, incident))
        
        # Sort potential resources by incident urgency (ascending) 
        # so we take from least urgent incidents first
        potential_resources.sort(key=lambda x: x[1].urgency_score)
        
        # Try to find one resource of each required type
        reallocated_resources = []
        needed_types = set(critical_incident.required_resources)
        
        for resource, source_incident in potential_resources:
            resource_type = resource.resource_type.name
            
            # If we still need this type of resource
            if resource_type in needed_types:
                # Reallocate this resource
                self._log(f"  Reallocating {resource.resource_type.value} {resource.id} from "
                         f"Incident #{source_incident.id} (Priority: {source_incident.priority}, "
                         f"Urgency: {source_incident.urgency_score:.2f}) "
                         f"to critical Incident #{critical_incident.id} (Priority: {critical_incident.priority}, "
                         f"Urgency: {critical_incident.urgency_score:.2f})")
                
                # Remove from source incident
                source_incident.remove_resource(resource.id)
                self.allocation_map[source_incident.id].remove(resource)
                
                # If source incident now has no resources, update status and allocation map
                if not self.allocation_map[source_incident.id]:
                    source_incident.update_status(IncidentStatus.REPORTED)
                    del self.allocation_map[source_incident.id]
                else:
                    # Otherwise, update to PARTIAL status
                    source_incident.update_status(IncidentStatus.PARTIAL)
                
                # Release resource from current incident
                resource.release()
                resource.mark_available()  # Make it available for immediate reassignment
                
                # Add to our reallocated resources list
                reallocated_resources.append(resource)
                
                # Remove this type from our needed types
                needed_types.remove(resource_type)
                
                # If we've found all needed types, we're done
                if not needed_types:
                    break
        
        # If we found resources for all needed types
        if not needed_types:
            # Assign reallocated resources to critical incident
            self._assign_resources_to_incident(critical_incident, reallocated_resources)
            return True
        else:
            # We couldn't find all needed resources
            self._log(f"  Could not find all needed resources for Incident #{critical_incident.id}. "
                     f"Still missing: {', '.join(needed_types)}")
            
            # Return any resources we've already reallocated to their original incidents
            for resource in reallocated_resources:
                # Find original incident
                for incident_id, incident_resources in self.allocation_map.items():
                    for incident_resource in incident_resources:
                        if incident_resource.id == resource.id:
                            incident = self.incident_manager.get_incident(incident_id)
                            self._log(f"  Returning {resource.resource_type.value} {resource.id} "
                                     f"to Incident #{incident.id}")
                            break
            
            return False
    
    def handle_new_incident(self, incident: Incident) -> bool:
        """
        Handle a newly added incident.
        
        This method adds the incident to the priority queue and attempts
        to allocate resources to it immediately.
        
        Args:
            incident: The new incident
            
        Returns:
            bool: True if resources were allocated successfully, False otherwise
        """
        # Add to priority queue
        self.priority_queue.add_incident(incident)
        
        # Get available resources
        available_resources = self.resource_manager.get_available_resources()
        
        # Find suitable resources
        suitable_resources = self._find_suitable_resources(incident, available_resources)
        
        if suitable_resources:
            # We found suitable resources, assign them
            self._assign_resources_to_incident(incident, suitable_resources)
            return True
        else:
            # Check if this is a high priority incident that needs reallocation
            if incident.priority <= 2:  # Priority 1 or 2 is considered high
                return self._try_reallocation(incident)
            else:
                # Lower priority, just queue it for later
                self._log(f"No immediate resources for Incident #{incident.id}, queued for later allocation")
                return False
    
    def handle_incident_update(self, incident: Incident) -> None:
        """
        Handle an updated incident.
        
        This method updates the incident in the priority queue and
        might trigger reallocation if the priority changed significantly.
        
        Args:
            incident: The updated incident
        """
        # Update in priority queue
        self.priority_queue.update_priority(incident)
        
        # If priority increased significantly, consider reallocation
        if incident.priority <= 2 and incident.id not in self.allocation_map:
            self._try_reallocation(incident)
    
    def handle_resource_update(self, resource: Resource) -> None:
        """
        Handle an updated resource.
        
        This method might trigger reallocation if a resource became
        available or unavailable.
        
        Args:
            resource: The updated resource
        """
        # If resource became available, try to allocate it
        if resource.status == ResourceStatus.AVAILABLE:
            # Try to allocate to highest priority incident
            highest_priority = self.priority_queue.peek_highest_priority()
            if highest_priority and highest_priority.id not in self.allocation_map:
                self.handle_new_incident(highest_priority)
        
        # If resource became unavailable, need to update allocations
        elif resource.status in [ResourceStatus.OUT_OF_SERVICE, ResourceStatus.MAINTENANCE]:
            # Check if this resource was assigned to an incident
            for incident_id, resources in list(self.allocation_map.items()):
                if resource in resources:
                    # Remove from allocation
                    incident = self.incident_manager.get_incident(incident_id)
                    incident.remove_resource(resource.id)
                    self.allocation_map[incident_id].remove(resource)
                    
                    # If no resources left, update incident status
                    if not self.allocation_map[incident_id]:
                        del self.allocation_map[incident_id]
                        incident.update_status(IncidentStatus.REPORTED)
                        
                        # Try to find new resources
                        self.handle_new_incident(incident)
                    else:
                        # Otherwise, update to PARTIAL status
                        incident.update_status(IncidentStatus.PARTIAL)
    
    def get_allocation_summary(self) -> str:
        """
        Get a summary of the current resource allocations.
        
        Returns:
            str: Multi-line summary of all current allocations
        """
        if not self.allocation_map:
            return "No resources currently allocated."
            
        # Generate summary
        summary_lines = ["Current Resource Allocations:"]
        
        for incident_id, resources in self.allocation_map.items():
            incident = self.incident_manager.get_incident(incident_id)
            
            # Only show if we have the incident and resources
            if incident and resources:
                resources_str = ", ".join([f"{r.resource_type.value} {r.id}" for r in resources])
                summary_lines.append(f"Incident #{incident_id} ({incident.incident_type.value}, "
                                   f"Priority {incident.priority}): {resources_str}")
        
        return "\n".join(summary_lines)