"""
Priority Queue implementation for Emergency Resource Allocation System.

This module provides a specialized priority queue for emergency incidents
that prioritizes incidents based on urgency scores. It uses the heapq module
from the Python standard library for efficient priority queue operations.

The IncidentPriorityQueue ensures that the most urgent incidents are always
processed first, which is crucial for emergency response scenarios.
"""

import heapq
import datetime
from typing import List, Dict, Any, Tuple, Optional


class IncidentPriorityQueue:
    """
    A priority queue specifically designed for emergency incidents.
    
    This class uses Python's heapq module to maintain a priority queue where
    incidents with higher urgency (lower priority number or higher urgency score)
    are processed first.
    
    Attributes:
        _queue (list): The internal priority queue storing incident tuples
        _entry_finder (dict): Dictionary mapping incident IDs to their entries in the queue
        _REMOVED (object): Marker for removed incidents
        _counter (int): Unique sequence count for tie-breaking
    """
    
    def __init__(self):
        """
        Initialize an empty priority queue for incidents.
        
        Sets up the internal data structures needed to efficiently manage
        incident priorities.
        """
        # The main priority queue - will contain tuples of:
        # (-urgency_score, time_added, counter, incident_id, incident_obj)
        self._queue = []
        
        # Dictionary for O(1) lookups and updates - maps incident_id to entry
        self._entry_finder = {}
        
        # Sentinel for marking incidents as removed
        self._REMOVED = object()
        
        # Counter for tie-breaking when urgency scores are equal
        self._counter = 0

    def add_incident(self, incident):
        """
        Add an incident to the priority queue.
        
        Args:
            incident: The incident object to add
            
        Returns:
            None
            
        Note:
            If an incident with the same ID already exists, it will be updated.
            The queue prioritizes by:
            1. Urgency score (higher score = higher priority)
            2. Time added (earlier = higher priority)
            3. Unique counter (for stability)
        """
        # Check if we're updating an existing incident
        if incident.id in self._entry_finder:
            self.remove_incident(incident.id)
        
        # Negative urgency score because heapq is a min-heap but we want highest urgency first
        # The more urgent an incident, the higher its urgency_score should be
        priority = -incident.urgency_score
        
        # Increment counter for stable sorting when priorities are equal
        self._counter += 1
        
        # Create the entry tuple (priority, time, counter, id, incident)
        entry = [priority, datetime.datetime.now(), self._counter, incident.id, incident]
        
        # Store reference in our entry finder
        self._entry_finder[incident.id] = entry
        
        # Add to the heap
        heapq.heappush(self._queue, entry)
        
        # Log the addition for debugging
        print(f"Added incident #{incident.id} to priority queue with urgency score {incident.urgency_score}")

    def remove_incident(self, incident_id):
        """
        Mark an incident as removed from the queue.
        
        This doesn't actually remove the item from the heap (which would be O(n)),
        but marks it as removed so it will be skipped when popping.
        
        Args:
            incident_id: The ID of the incident to remove
            
        Returns:
            True if the incident was found and removed, False otherwise
        """
        entry = self._entry_finder.pop(incident_id, None)
        
        if entry is None:
            return False  # Not found
            
        # Mark as removed by replacing the incident object with our sentinel
        entry[-1] = self._REMOVED
        return True

    def pop_highest_priority(self):
        """
        Remove and return the highest priority incident.
        
        Returns:
            The highest priority incident, or None if the queue is empty
        """
        while self._queue:
            # Get the highest priority item
            priority, time_added, counter, incident_id, incident = heapq.heappop(self._queue)
            
            # If it's not our removal sentinel, return it
            if incident is not self._REMOVED:
                del self._entry_finder[incident_id]
                return incident
                
        # Queue is empty
        return None

    def update_priority(self, incident):
        """
        Update the priority of an existing incident.
        
        This is implemented as a remove followed by an add operation.
        
        Args:
            incident: The incident with updated priority
            
        Returns:
            True if the incident was found and updated, False otherwise
        """
        if self.remove_incident(incident.id):
            self.add_incident(incident)
            return True
        return False

    def peek_highest_priority(self) -> Optional[Any]:
        """
        Return the highest priority incident without removing it.
        
        Returns:
            The highest priority incident, or None if the queue is empty
        """
        # Find the first non-removed entry
        for entry in self._queue:
            priority, time_added, counter, incident_id, incident = entry
            if incident is not self._REMOVED:
                return incident
        return None

    def is_empty(self) -> bool:
        """
        Check if the queue has any non-removed incidents.
        
        Returns:
            True if the queue is empty, False otherwise
        """
        # Check if we have any entries that aren't removed
        return all(incident is self._REMOVED for _, _, _, _, incident in self._queue)

    def __len__(self) -> int:
        """
        Get the number of incidents in the queue.
        
        Returns:
            The count of non-removed incidents
        """
        return len(self._entry_finder)

    def get_all_incidents(self) -> List[Any]:
        """
        Get all incidents currently in the queue, sorted by priority.
        
        Returns:
            A list of all incidents in priority order
        """
        # Return all non-removed incidents, sorted by priority
        result = []
        for incident_id, entry in self._entry_finder.items():
            priority, time_added, counter, _, incident = entry
            
            if incident is not self._REMOVED:
                result.append(incident)
                
        # Sort by priority (remember priority is negative urgency score)
        return sorted(result, key=lambda inc: -inc.urgency_score)