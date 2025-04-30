"""
Unit tests for the models module.

This module contains tests for the Incident and Resource classes,
validating their functionality and behavior under various conditions.
"""

import unittest
import datetime
from src.models.incident import Incident, IncidentType, IncidentStatus
from src.models.resource import Resource, ResourceType, ResourceStatus


class TestIncident(unittest.TestCase):
    """
    Test cases for the Incident class.
    
    These tests validate the core functionality of the Incident class,
    including creating incidents, updating properties, and calculating
    urgency scores.
    """
    
    def setUp(self):
        """Set up test fixtures for incident tests."""
        # Create a standard test incident
        self.incident = Incident(
            id=1,
            incident_type=IncidentType.FIRE,
            location="Zone 3",
            priority=2,
            required_resources=["FIRE_TRUCK", "AMBULANCE"],
            details="Building on fire",
            affected_people=5,
            special_factors=["children"]
        )
    
    def test_incident_creation(self):
        """Test that incidents are created with the correct attributes."""
        self.assertEqual(self.incident.id, 1)
        self.assertEqual(self.incident.incident_type, IncidentType.FIRE)
        self.assertEqual(self.incident.location, "Zone 3")
        self.assertEqual(self.incident.priority, 2)
        self.assertEqual(self.incident.required_resources, ["FIRE_TRUCK", "AMBULANCE"])
        self.assertEqual(self.incident.status, IncidentStatus.REPORTED)
        self.assertEqual(self.incident.details, "Building on fire")
        self.assertEqual(self.incident.affected_people, 5)
        self.assertEqual(self.incident.special_factors, ["children"])
        
        # Check that history is created
        self.assertEqual(len(self.incident.history), 1)
        self.assertEqual(self.incident.history[0]["description"], "Incident reported")
    
    def test_update_priority(self):
        """Test updating incident priority."""
        old_urgency = self.incident.urgency_score
        self.incident.update_priority(1)  # Higher priority (lower number)
        
        self.assertEqual(self.incident.priority, 1)
        self.assertGreater(self.incident.urgency_score, old_urgency)
        
        # Check that history is updated
        self.assertEqual(len(self.incident.history), 2)
        self.assertIn("Priority changed", self.incident.history[1]["description"])
    
    def test_update_status(self):
        """Test updating incident status."""
        self.incident.update_status(IncidentStatus.ASSIGNED)
        self.assertEqual(self.incident.status, IncidentStatus.ASSIGNED)
        
        # Test updating with string status name
        self.incident.update_status("PARTIAL")
        self.assertEqual(self.incident.status, IncidentStatus.PARTIAL)
        
        # Test invalid status
        with self.assertRaises(ValueError):
            self.incident.update_status("INVALID_STATUS")
            
        # Check that history is updated
        self.assertEqual(len(self.incident.history), 3)
    
    def test_urgency_calculation(self):
        """Test urgency score calculation."""
        # Calculate baseline score
        base_urgency = self.incident.urgency_score
        
        # Create a similar incident with higher priority
        high_priority = Incident(
            id=2,
            incident_type=IncidentType.FIRE,
            location="Zone 3",
            priority=1,  # Higher priority
            required_resources=["FIRE_TRUCK", "AMBULANCE"],
            affected_people=5,
            special_factors=["children"]
        )
        
        # Create a similar incident with more people affected
        more_people = Incident(
            id=3,
            incident_type=IncidentType.FIRE,
            location="Zone 3",
            priority=2,
            required_resources=["FIRE_TRUCK", "AMBULANCE"],
            affected_people=10,  # More people
            special_factors=["children"]
        )
        
        # Create a similar incident with more special factors
        more_factors = Incident(
            id=4,
            incident_type=IncidentType.FIRE,
            location="Zone 3",
            priority=2,
            required_resources=["FIRE_TRUCK", "AMBULANCE"],
            affected_people=5,
            special_factors=["children", "elderly", "hazardous_materials"]  # More factors
        )
        
        # Verify that each factor increases urgency
        self.assertGreater(high_priority.urgency_score, base_urgency)
        self.assertGreater(more_people.urgency_score, base_urgency)
        self.assertGreater(more_factors.urgency_score, base_urgency)
    
    def test_add_remove_resource(self):
        """Test adding and removing resources from an incident."""
        # Create a test resource
        resource = Resource("FT1", ResourceType.FIRE_TRUCK, "Zone 2")
        
        # Add resource to incident
        self.incident.add_resource(resource)
        self.assertEqual(len(self.incident.assigned_resources), 1)
        self.assertEqual(self.incident.status, IncidentStatus.PARTIAL)  # Status updated
        
        # Add a second resource to satisfy all requirements
        resource2 = Resource("AM1", ResourceType.AMBULANCE, "Zone 1")
        self.incident.add_resource(resource2)
        self.assertEqual(len(self.incident.assigned_resources), 2)
        self.assertEqual(self.incident.status, IncidentStatus.ASSIGNED)  # Fully resourced
        
        # Remove a resource
        self.incident.remove_resource("FT1")
        self.assertEqual(len(self.incident.assigned_resources), 1)
        self.assertEqual(self.incident.status, IncidentStatus.PARTIAL)  # Partially resourced
        
        # Remove the last resource
        self.incident.remove_resource("AM1")
        self.assertEqual(len(self.incident.assigned_resources), 0)
        self.assertEqual(self.incident.status, IncidentStatus.REPORTED)  # No resources


class TestResource(unittest.TestCase):
    """
    Test cases for the Resource class.
    
    These tests validate the core functionality of the Resource class,
    including creating resources, updating status, and calculating response times.
    """
    
    def setUp(self):
        """Set up test fixtures for resource tests."""
        # Create a standard test resource
        self.resource = Resource(
            id="AM123",
            resource_type=ResourceType.AMBULANCE,
            location="Zone 3",
            capabilities=["advanced_life_support"]
        )
    
    def test_resource_creation(self):
        """Test that resources are created with the correct attributes."""
        self.assertEqual(self.resource.id, "AM123")
        self.assertEqual(self.resource.resource_type, ResourceType.AMBULANCE)
        self.assertEqual(self.resource.location, "Zone 3")
        self.assertEqual(self.resource.status, ResourceStatus.AVAILABLE)
        self.assertEqual(self.resource.capabilities, ["advanced_life_support"])
        
        # Check that history is created
        self.assertEqual(len(self.resource.history), 1)
        self.assertEqual(self.resource.history[0]["description"], "Initial status")
    
    def test_status_lifecycle(self):
        """Test the full lifecycle of resource status changes."""
        # Initially available
        self.assertEqual(self.resource.status, ResourceStatus.AVAILABLE)
        
        # Assign to incident
        self.assertTrue(self.resource.assign_to_incident(1))
        self.assertEqual(self.resource.status, ResourceStatus.ASSIGNED)
        self.assertEqual(self.resource.current_incident, 1)
        
        # Mark as en route
        self.assertTrue(self.resource.mark_en_route())
        self.assertEqual(self.resource.status, ResourceStatus.EN_ROUTE)
        
        # Mark as on scene
        self.assertTrue(self.resource.mark_on_scene())
        self.assertEqual(self.resource.status, ResourceStatus.ON_SCENE)
        
        # Release from incident
        self.assertTrue(self.resource.release())
        self.assertEqual(self.resource.status, ResourceStatus.RETURNING)
        self.assertIsNone(self.resource.current_incident)
        
        # Mark as available again
        self.assertTrue(self.resource.mark_available())
        self.assertEqual(self.resource.status, ResourceStatus.AVAILABLE)
        
        # Mark out of service
        self.resource.mark_out_of_service("Maintenance required")
        self.assertEqual(self.resource.status, ResourceStatus.OUT_OF_SERVICE)
        
        # Check that history is updated
        self.assertEqual(len(self.resource.history), 7)
    
    def test_status_validation(self):
        """Test that status transitions are properly validated."""
        # Cannot mark as en route if not assigned
        self.assertFalse(self.resource.mark_en_route())
        
        # Cannot mark as on scene if not en route
        self.assertFalse(self.resource.mark_on_scene())
        
        # Cannot mark as available if not returning
        self.assertFalse(self.resource.mark_available())
        
        # Cannot release if not assigned, en route, or on scene
        self.assertFalse(self.resource.release())
    
    def test_location_update(self):
        """Test updating resource location."""
        self.resource.update_location("Zone 5")
        self.assertEqual(self.resource.location, "Zone 5")
        
        # Check that history is updated
        self.assertEqual(len(self.resource.history), 2)
        self.assertIn("Location changed", self.resource.history[1]["description"])
    
    def test_response_time_calculation(self):
        """Test calculation of response times between locations."""
        # Same zone should have minimal response time
        same_zone_time = self.resource.calculate_response_time("Zone 3")
        
        # Adjacent zone should have moderate response time
        adjacent_zone_time = self.resource.calculate_response_time("Zone 4")
        
        # Distant zone should have longer response time
        distant_zone_time = self.resource.calculate_response_time("Zone 8")
        
        # Verify response times increase with distance
        self.assertLess(same_zone_time, adjacent_zone_time)
        self.assertLess(adjacent_zone_time, distant_zone_time)
        
        # Non-numeric zone should return default response time
        non_numeric_time = self.resource.calculate_response_time("Central District")
        self.assertEqual(non_numeric_time, 15)  # Default time


if __name__ == '__main__':
    unittest.main()