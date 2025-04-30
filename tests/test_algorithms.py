"""
Unit tests for the algorithms module.

This module contains tests for the Dispatcher and PriorityQueue classes,
validating their functionality and behavior under various conditions.
"""

import unittest
from unittest.mock import MagicMock, patch
import datetime

from src.models.incident import Incident, IncidentType, IncidentStatus
from src.models.resource import Resource, ResourceType, ResourceStatus
from src.algorithms.dispatcher import Dispatcher
from src.algorithms.priority_queue import IncidentPriorityQueue


class TestPriorityQueue(unittest.TestCase):
    """
    Test cases for the IncidentPriorityQueue class.
    
    These tests verify that the priority queue correctly prioritizes incidents
    based on urgency scores and handles operations like adding, removing, and
    updating incidents correctly.
    """
    
    def setUp(self):
        """Set up test fixtures for priority queue tests."""
        self.queue = IncidentPriorityQueue()
        
        # Create test incidents with different priorities
        self.high_priority = Incident(
            id=1,
            incident_type=IncidentType.FIRE,
            location="Zone 1",
            priority=1,
            required_resources=["FIRE_TRUCK"],
            affected_people=10,
            special_factors=["children"]
        )
        
        self.medium_priority = Incident(
            id=2,
            incident_type=IncidentType.MEDICAL,
            location="Zone 2",
            priority=3,
            required_resources=["AMBULANCE"],
            affected_people=1
        )
        
        self.low_priority = Incident(
            id=3,
            incident_type=IncidentType.TRAFFIC,
            location="Zone 3",
            priority=5,
            required_resources=["POLICE_UNIT"]
        )
    
    def test_add_incident(self):
        """Test adding incidents to the queue."""
        # Add incidents
        self.queue.add_incident(self.high_priority)
        self.queue.add_incident(self.medium_priority)
        self.queue.add_incident(self.low_priority)
        
        # Check queue size
        self.assertEqual(len(self.queue), 3)
    
    def test_pop_highest_priority(self):
        """Test that incidents are popped in correct priority order."""
        # Add incidents in a non-priority order
        self.queue.add_incident(self.medium_priority)
        self.queue.add_incident(self.low_priority)
        self.queue.add_incident(self.high_priority)
        
        # Pop them and verify order
        first = self.queue.pop_highest_priority()
        second = self.queue.pop_highest_priority()
        third = self.queue.pop_highest_priority()
        
        # Should come out in priority order (highest first)
        self.assertEqual(first.id, self.high_priority.id)
        self.assertEqual(second.id, self.medium_priority.id)
        self.assertEqual(third.id, self.low_priority.id)
    
    def test_update_priority(self):
        """Test updating an incident's priority in the queue."""
        # Add incidents
        self.queue.add_incident(self.high_priority)
        self.queue.add_incident(self.low_priority)
        
        # Change priority of low priority incident to make it highest
        self.low_priority.update_priority(1)
        self.queue.update_priority(self.low_priority)
        
        # Verify the updated incident is now highest priority
        highest = self.queue.pop_highest_priority()
        self.assertEqual(highest.id, self.low_priority.id)
    
    def test_remove_incident(self):
        """Test removing an incident from the queue."""
        # Add incidents
        self.queue.add_incident(self.high_priority)
        self.queue.add_incident(self.medium_priority)
        self.queue.add_incident(self.low_priority)
        
        # Remove medium priority incident
        self.queue.remove_incident(self.medium_priority.id)
        
        # Check size
        self.assertEqual(len(self.queue), 2)
        
        # Pop incidents and verify medium is not there
        first = self.queue.pop_highest_priority()
        second = self.queue.pop_highest_priority()
        self.assertEqual(first.id, self.high_priority.id)
        self.assertEqual(second.id, self.low_priority.id)
        
        # Queue should now be empty
        self.assertTrue(self.queue.is_empty())
    
    def test_peek_highest_priority(self):
        """Test peeking at the highest priority incident without removing it."""
        self.queue.add_incident(self.high_priority)
        self.queue.add_incident(self.medium_priority)
        
        # Peek should show highest priority incident
        highest = self.queue.peek_highest_priority()
        self.assertEqual(highest.id, self.high_priority.id)
        
        # Queue size should remain unchanged
        self.assertEqual(len(self.queue), 2)
    
    def test_get_all_incidents(self):
        """Test getting all incidents in priority order."""
        self.queue.add_incident(self.low_priority)
        self.queue.add_incident(self.high_priority)
        self.queue.add_incident(self.medium_priority)
        
        # Get all incidents
        all_incidents = self.queue.get_all_incidents()
        
        # Should be in priority order
        self.assertEqual(len(all_incidents), 3)
        self.assertEqual(all_incidents[0].id, self.high_priority.id)
        self.assertEqual(all_incidents[1].id, self.medium_priority.id)
        self.assertEqual(all_incidents[2].id, self.low_priority.id)


class TestDispatcher(unittest.TestCase):
    """
    Test cases for the Dispatcher class.
    
    These tests verify that the dispatcher correctly allocates resources to incidents
    based on priority, handles reallocation when high-priority incidents arise,
    and maintains the allocation map correctly.
    """
    
    def setUp(self):
        """Set up test fixtures for dispatcher tests."""
        # Create mock incident manager
        self.incident_manager = MagicMock()
        
        # Create mock resource manager
        self.resource_manager = MagicMock()
        
        # Create mock logger
        self.logger = MagicMock()
        
        # Create dispatcher
        self.dispatcher = Dispatcher(self.incident_manager, self.resource_manager, self.logger)
        
        # Create test incidents
        self.critical_incident = Incident(
            id=1,
            incident_type=IncidentType.FIRE,
            location="Zone 1",
            priority=1,
            required_resources=["FIRE_TRUCK", "AMBULANCE"],
            affected_people=5,
            special_factors=["children"]
        )
        
        self.medium_incident = Incident(
            id=2,
            incident_type=IncidentType.MEDICAL,
            location="Zone 2",
            priority=3,
            required_resources=["AMBULANCE"],
            affected_people=1
        )
        
        self.low_incident = Incident(
            id=3,
            incident_type=IncidentType.TRAFFIC,
            location="Zone 3",
            priority=5,
            required_resources=["POLICE_UNIT"]
        )
        
        # Create test resources
        self.fire_truck = Resource("FT1", ResourceType.FIRE_TRUCK, "Zone 2")
        self.ambulance = Resource("AM1", ResourceType.AMBULANCE, "Zone 1")
        self.police_unit = Resource("PU1", ResourceType.POLICE_UNIT, "Zone 2")
        
        # Set up mock return values
        self.incident_manager.get_all_incidents.return_value = [
            self.critical_incident, self.medium_incident, self.low_incident
        ]
        
        self.incident_manager.get_incident.side_effect = lambda id: {
            1: self.critical_incident,
            2: self.medium_incident,
            3: self.low_incident
        }.get(id)
        
        self.resource_manager.get_all_resources.return_value = [
            self.fire_truck, self.ambulance, self.police_unit
        ]
        
        self.resource_manager.get_available_resources.return_value = [
            self.fire_truck, self.ambulance, self.police_unit
        ]
    
    def test_allocate_resources(self):
        """Test basic resource allocation."""
        # Set up mock to return specific resources for each required type
        def mock_find_suitable_resources(incident, available_resources):
            if incident.id == 1:  # Critical incident
                return [self.fire_truck, self.ambulance]
            elif incident.id == 2:  # Medium incident
                return [self.ambulance]  # This will be used in reallocation test
            elif incident.id == 3:  # Low incident
                return [self.police_unit]
            return []
        
        # Patch the _find_suitable_resources method
        with patch.object(self.dispatcher, '_find_suitable_resources', side_effect=mock_find_suitable_resources):
            # Call allocate_resources
            allocation_map = self.dispatcher.allocate_resources()
            
            # Verify allocation map
            self.assertEqual(len(allocation_map), 3)
            self.assertIn(1, allocation_map)  # Critical incident
            self.assertIn(2, allocation_map)  # Medium incident
            self.assertIn(3, allocation_map)  # Low incident
            
            # Verify resource assignment
            self.assertEqual(len(allocation_map[1]), 2)  # Critical incident gets 2 resources
            self.assertEqual(len(allocation_map[2]), 1)  # Medium incident gets 1 resource
            self.assertEqual(len(allocation_map[3]), 1)  # Low incident gets 1 resource
    
    def test_reallocation(self):
        """Test reallocation of resources when a critical incident has no available resources."""
        # First, create a situation where all resources are allocated
        self.resource_manager.get_available_resources.return_value = []  # No available resources
        
        # Set up mock allocation map with medium and low priority incidents
        self.dispatcher.allocation_map = {
            2: [self.ambulance],  # Medium incident has ambulance
            3: [self.police_unit, self.fire_truck]  # Low incident has police and fire truck
        }
        
        # Critical incident needs a fire truck
        new_critical = Incident(
            id=4,
            incident_type=IncidentType.FIRE,
            location="Zone 1",
            priority=1,
            required_resources=["FIRE_TRUCK"],
            affected_people=10,
            special_factors=["children", "elderly"]
        )
        
        # Make sure this incident has higher urgency than others
        new_critical.urgency_score = 100
        self.low_incident.urgency_score = 10
        
        # Add this incident to the manager's mock
        self.incident_manager.get_incident.side_effect = lambda id: {
            1: self.critical_incident,
            2: self.medium_incident,
            3: self.low_incident,
            4: new_critical
        }.get(id)
        
        # Try reallocation
        result = self.dispatcher._try_reallocation(new_critical)
        
        # Verify reallocation happened
        self.assertTrue(result)
        
        # Verify fire truck was taken from low priority incident
        self.assertIn(4, self.dispatcher.allocation_map)  # New critical incident is in map
        self.assertIn(self.fire_truck, self.dispatcher.allocation_map[4])  # Has fire truck
        
        # Verify low priority incident still has police but not fire truck
        self.assertIn(3, self.dispatcher.allocation_map)
        self.assertIn(self.police_unit, self.dispatcher.allocation_map[3])
        self.assertNotIn(self.fire_truck, self.dispatcher.allocation_map[3])
    
    def test_handle_new_incident(self):
        """Test handling a new incident."""
        # Make a new incident
        new_incident = Incident(
            id=5,
            incident_type=IncidentType.MEDICAL,
            location="Zone 4",
            priority=2,
            required_resources=["AMBULANCE"]
        )
        
        # Set up mock to return the ambulance
        with patch.object(self.dispatcher, '_find_suitable_resources', return_value=[self.ambulance]):
            # Handle new incident
            result = self.dispatcher.handle_new_incident(new_incident)
            
            # Verify success
            self.assertTrue(result)
            
            # Verify incident was added to allocation map
            self.assertIn(5, self.dispatcher.allocation_map)
            self.assertIn(self.ambulance, self.dispatcher.allocation_map[5])
            
            # Verify resource was assigned to incident
            self.ambulance.assign_to_incident.assert_called_with(5)
    
    def test_handle_resource_update(self):
        """Test handling a resource status update."""
        # Set up a situation with an allocated resource
        self.dispatcher.allocation_map = {
            1: [self.ambulance]
        }
        
        # Make the resource unavailable
        self.ambulance.status = ResourceStatus.OUT_OF_SERVICE
        
        # Handle resource update
        self.dispatcher.handle_resource_update(self.ambulance)
        
        # Verify incident lost its resource
        self.assertNotIn(1, self.dispatcher.allocation_map)
        
        # Verify incident status was updated
        self.critical_incident.update_status.assert_called_with(IncidentStatus.REPORTED)


if __name__ == '__main__':
    unittest.main()