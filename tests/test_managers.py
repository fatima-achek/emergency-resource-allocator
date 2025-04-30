"""
Unit tests for the managers module.

This module contains tests for the IncidentManager and ResourceManager classes,
validating their functionality for managing collections of incidents and resources.
"""

import unittest
from unittest.mock import patch

from src.models.incident import Incident, IncidentType, IncidentStatus
from src.models.resource import Resource, ResourceType, ResourceStatus
from src.managers.incident_manager import IncidentManager
from src.managers.resource_manager import ResourceManager


class TestIncidentManager(unittest.TestCase):
    """
    Test cases for the IncidentManager class.
    
    These tests verify that the incident manager correctly handles adding,
    retrieving, updating, and filtering incidents.
    """
    
    def setUp(self):
        """Set up test fixtures for incident manager tests."""
        self.manager = IncidentManager()
        
        # Add some test incidents
        self.fire_incident = self.manager.add_incident(
            incident_type=IncidentType.FIRE,
            location="Zone 1",
            priority=1,
            required_resources=["FIRE_TRUCK", "AMBULANCE"],
            details="Building on fire",
            affected_people=5,
            special_factors=["children"]
        )
        
        self.medical_incident = self.manager.add_incident(
            incident_type=IncidentType.MEDICAL,
            location="Zone 2",
            priority=2,
            required_resources=["AMBULANCE", "MEDICAL_TEAM"],
            details="Heart attack",
            affected_people=1,
            special_factors=["elderly"]
        )
        
        self.traffic_incident = self.manager.add_incident(
            incident_type=IncidentType.TRAFFIC,
            location="Zone 1",
            priority=3,
            required_resources=["POLICE_UNIT", "AMBULANCE"],
            details="Car accident",
            affected_people=2,
            special_factors=["multi_vehicle"]
        )
    
    def test_add_incident(self):
        """Test adding incidents to the manager."""
        # Check that incidents were added correctly
        self.assertEqual(len(self.manager.incidents), 3)
        
        # Add one more incident
        hazmat_incident = self.manager.add_incident(
            incident_type="HAZMAT",  # Test string type
            location="Zone 3",
            priority=1,
            required_resources=["HAZMAT_UNIT", "FIRE_TRUCK"]
        )
        
        # Check that the new incident was added
        self.assertEqual(len(self.manager.incidents), 4)
        self.assertIn(hazmat_incident.id, self.manager.incidents)
        self.assertEqual(hazmat_incident.incident_type, IncidentType.HAZMAT)
    
    def test_get_incident(self):
        """Test retrieving an incident by ID."""
        # Get an incident by ID
        incident = self.manager.get_incident(self.fire_incident.id)
        
        # Check that the correct incident was retrieved
        self.assertEqual(incident, self.fire_incident)
        
        # Try getting a non-existent incident
        non_existent = self.manager.get_incident(999)
        self.assertIsNone(non_existent)
    
    def test_update_incident(self):
        """Test updating an incident."""
        # Update the fire incident
        updated = self.manager.update_incident(
            self.fire_incident.id,
            priority=2,
            location="Zone 4",
            affected_people=10
        )
        
        # Check that the incident was updated
        self.assertEqual(updated.priority, 2)
        self.assertEqual(updated.location, "Zone 4")
        self.assertEqual(updated.affected_people, 10)
        
        # Try updating a non-existent incident
        non_existent = self.manager.update_incident(999, priority=1)
        self.assertIsNone(non_existent)
    
    def test_remove_incident(self):
        """Test removing an incident."""
        # Remove the traffic incident
        result = self.manager.remove_incident(self.traffic_incident.id)
        
        # Check that the incident was removed
        self.assertTrue(result)
        self.assertEqual(len(self.manager.incidents), 2)
        self.assertNotIn(self.traffic_incident.id, self.manager.incidents)
        
        # Try removing a non-existent incident
        result = self.manager.remove_incident(999)
        self.assertFalse(result)
    
    def test_get_all_incidents(self):
        """Test retrieving all incidents."""
        incidents = self.manager.get_all_incidents()
        
        # Check that all incidents were retrieved
        self.assertEqual(len(incidents), 3)
        self.assertIn(self.fire_incident, incidents)
        self.assertIn(self.medical_incident, incidents)
        self.assertIn(self.traffic_incident, incidents)
    
    def test_get_active_incidents(self):
        """Test retrieving active incidents."""
        # All incidents are active by default
        active = self.manager.get_active_incidents()
        self.assertEqual(len(active), 3)
        
        # Mark one incident as resolved
        self.fire_incident.update_status(IncidentStatus.RESOLVED)
        
        # Check that only active incidents are retrieved
        active = self.manager.get_active_incidents()
        self.assertEqual(len(active), 2)
        self.assertNotIn(self.fire_incident, active)
    
    def test_get_incidents_by_priority(self):
        """Test filtering incidents by priority."""
        # Get priority 1 incidents
        priority_1 = self.manager.get_incidents_by_priority(1)
        self.assertEqual(len(priority_1), 1)
        self.assertEqual(priority_1[0], self.fire_incident)
        
        # Get priority 2 incidents
        priority_2 = self.manager.get_incidents_by_priority(2)
        self.assertEqual(len(priority_2), 1)
        self.assertEqual(priority_2[0], self.medical_incident)
    
    def test_get_incidents_by_type(self):
        """Test filtering incidents by type."""
        # Get fire incidents
        fire = self.manager.get_incidents_by_type(IncidentType.FIRE)
        self.assertEqual(len(fire), 1)
        self.assertEqual(fire[0], self.fire_incident)
        
        # Get medical incidents
        medical = self.manager.get_incidents_by_type("MEDICAL")  # Test string type
        self.assertEqual(len(medical), 1)
        self.assertEqual(medical[0], self.medical_incident)
    
    def test_get_incidents_by_location(self):
        """Test filtering incidents by location."""
        # Get Zone 1 incidents
        zone_1 = self.manager.get_incidents_by_location("Zone 1")
        self.assertEqual(len(zone_1), 2)
        self.assertIn(self.fire_incident, zone_1)
        self.assertIn(self.traffic_incident, zone_1)
        
        # Get Zone 2 incidents
        zone_2 = self.manager.get_incidents_by_location("Zone 2")
        self.assertEqual(len(zone_2), 1)
        self.assertEqual(zone_2[0], self.medical_incident)
    
    def test_get_incidents_requiring_resource(self):
        """Test filtering incidents by required resource."""
        # Get incidents requiring ambulance
        ambulance_incidents = self.manager.get_incidents_requiring_resource("AMBULANCE")
        self.assertEqual(len(ambulance_incidents), 3)  # All test incidents need ambulance
        
        # Get incidents requiring fire truck
        fire_truck_incidents = self.manager.get_incidents_requiring_resource("FIRE_TRUCK")
        self.assertEqual(len(fire_truck_incidents), 1)
        self.assertEqual(fire_truck_incidents[0], self.fire_incident)
    
    def test_mark_incident_resolved(self):
        """Test marking an incident as resolved."""
        # Mark the fire incident as resolved
        result = self.manager.mark_incident_resolved(self.fire_incident.id)
        
        # Check that the incident was marked as resolved
        self.assertTrue(result)
        self.assertEqual(self.fire_incident.status, IncidentStatus.RESOLVED)
        
        # Try marking a non-existent incident
        result = self.manager.mark_incident_resolved(999)
        self.assertFalse(result)
    
    def test_mark_incident_cancelled(self):
        """Test marking an incident as cancelled."""
        # Mark the medical incident as cancelled
        result = self.manager.mark_incident_cancelled(self.medical_incident.id)
        
        # Check that the incident was marked as cancelled
        self.assertTrue(result)
        self.assertEqual(self.medical_incident.status, IncidentStatus.CANCELLED)
        
        # Try marking a non-existent incident
        result = self.manager.mark_incident_cancelled(999)
        self.assertFalse(result)
    
    def test_get_highest_priority_incidents(self):
        """Test retrieving the highest priority incidents."""
        # Add a few more incidents with different priorities
        self.manager.add_incident(
            incident_type=IncidentType.RESCUE,
            location="Zone 3",
            priority=1,  # High priority
            required_resources=["RESCUE_TEAM"]
        )
        
        self.manager.add_incident(
            incident_type=IncidentType.OTHER,
            location="Zone 4",
            priority=5,  # Low priority
            required_resources=["POLICE_UNIT"]
        )
        
        # Get top 2 highest priority incidents
        highest = self.manager.get_highest_priority_incidents(2)
        
        # Check that the correct incidents were retrieved
        self.assertEqual(len(highest), 2)
        self.assertTrue(all(i.priority <= 2 for i in highest))  # All should be priority 1 or 2


class TestResourceManager(unittest.TestCase):
    """
    Test cases for the ResourceManager class.
    
    These tests verify that the resource manager correctly handles adding,
    retrieving, updating, and filtering resources.
    """
    
    def setUp(self):
        """Set up test fixtures for resource manager tests."""
        self.manager = ResourceManager()
        
        # Add some test resources
        self.ambulance = self.manager.add_resource(
            resource_type=ResourceType.AMBULANCE,
            location="Zone 1",
            capabilities=["advanced_life_support"]
        )
        
        self.fire_truck = self.manager.add_resource(
            resource_type=ResourceType.FIRE_TRUCK,
            location="Zone 2",
            capabilities=["ladder", "pump"]
        )
        
        self.police_unit = self.manager.add_resource(
            resource_type=ResourceType.POLICE_UNIT,
            location="Zone 1"
        )
    
    def test_add_resource(self):
        """Test adding resources to the manager."""
        # Check that resources were added correctly
        self.assertEqual(len(self.manager.resources), 3)
        
        # Add one more resource
        hazmat_unit = self.manager.add_resource(
            resource_type="HAZMAT_UNIT",  # Test string type
            location="Zone 3",
            capabilities=["chemical_containment"]
        )
        
        # Check that the new resource was added
        self.assertEqual(len(self.manager.resources), 4)
        self.assertIn(hazmat_unit.id, self.manager.resources)
        self.assertEqual(hazmat_unit.resource_type, ResourceType.HAZMAT_UNIT)
        
        # Check that ID was auto-generated with correct prefix
        self.assertTrue(hazmat_unit.id.startswith("HA"))
    
    def test_get_resource(self):
        """Test retrieving a resource by ID."""
        # Get a resource by ID
        resource = self.manager.get_resource(self.ambulance.id)
        
        # Check that the correct resource was retrieved
        self.assertEqual(resource, self.ambulance)
        
        # Try getting a non-existent resource
        non_existent = self.manager.get_resource("NONEXISTENT")
        self.assertIsNone(non_existent)
    
    def test_update_resource(self):
        """Test updating a resource."""
        # Update the ambulance
        updated = self.manager.update_resource(
            self.ambulance.id,
            location="Zone 4",
            status=ResourceStatus.MAINTENANCE
        )
        
        # Check that the resource was updated
        self.assertEqual(updated.location, "Zone 4")
        self.assertEqual(updated.status, ResourceStatus.MAINTENANCE)
        
        # Try updating a non-existent resource
        non_existent = self.manager.update_resource("NONEXISTENT", location="Zone 5")
        self.assertIsNone(non_existent)
    
    def test_remove_resource(self):
        """Test removing a resource."""
        # Remove the police unit
        result = self.manager.remove_resource(self.police_unit.id)
        
        # Check that the resource was removed
        self.assertTrue(result)
        self.assertEqual(len(self.manager.resources), 2)
        self.assertNotIn(self.police_unit.id, self.manager.resources)
        
        # Try removing a non-existent resource
        result = self.manager.remove_resource("NONEXISTENT")
        self.assertFalse(result)
    
    def test_get_all_resources(self):
        """Test retrieving all resources."""
        resources = self.manager.get_all_resources()
        
        # Check that all resources were retrieved
        self.assertEqual(len(resources), 3)
        self.assertIn(self.ambulance, resources)
        self.assertIn(self.fire_truck, resources)
        self.assertIn(self.police_unit, resources)
    
    def test_get_available_resources(self):
        """Test retrieving available resources."""
        # All resources are available by default
        available = self.manager.get_available_resources()
        self.assertEqual(len(available), 3)
        
        # Mark one resource as out of service
        self.ambulance.mark_out_of_service("Maintenance")
        
        # Check that only available resources are retrieved
        available = self.manager.get_available_resources()
        self.assertEqual(len(available), 2)
        self.assertNotIn(self.ambulance, available)
    
    def test_get_resources_by_type(self):
        """Test filtering resources by type."""
        # Get ambulances
        ambulances = self.manager.get_resources_by_type(ResourceType.AMBULANCE)
        self.assertEqual(len(ambulances), 1)
        self.assertEqual(ambulances[0], self.ambulance)
        
        # Get fire trucks
        fire_trucks = self.manager.get_resources_by_type("FIRE_TRUCK")  # Test string type
        self.assertEqual(len(fire_trucks), 1)
        self.assertEqual(fire_trucks[0], self.fire_truck)
    
    def test_get_resources_by_location(self):
        """Test filtering resources by location."""
        # Get Zone 1 resources
        zone_1 = self.manager.get_resources_by_location("Zone 1")
        self.assertEqual(len(zone_1), 2)
        self.assertIn(self.ambulance, zone_1)
        self.assertIn(self.police_unit, zone_1)
        
        # Get Zone 2 resources
        zone_2 = self.manager.get_resources_by_location("Zone 2")
        self.assertEqual(len(zone_2), 1)
        self.assertEqual(zone_2[0], self.fire_truck)
    
    def test_get_resources_by_capability(self):
        """Test filtering resources by capability."""
        # Get resources with advanced life support
        als_resources = self.manager.get_resources_by_capability("advanced_life_support")
        self.assertEqual(len(als_resources), 1)
        self.assertEqual(als_resources[0], self.ambulance)
        
        # Get resources with ladder capability
        ladder_resources = self.manager.get_resources_by_capability("ladder")
        self.assertEqual(len(ladder_resources), 1)
        self.assertEqual(ladder_resources[0], self.fire_truck)
        
        # Get resources with non-existent capability
        non_existent = self.manager.get_resources_by_capability("non_existent")
        self.assertEqual(len(non_existent), 0)
    
    def test_get_resources_for_incident_type(self):
        """Test getting resources suitable for an incident type."""
        # Get resources for fire incident
        fire_resources = self.manager.get_resources_for_incident_type(IncidentType.FIRE)
        
        # Should return fire trucks and command units
        self.assertIn(ResourceType.FIRE_TRUCK, fire_resources)
        self.assertEqual(len(fire_resources[ResourceType.FIRE_TRUCK]), 1)
        self.assertEqual(fire_resources[ResourceType.FIRE_TRUCK][0], self.fire_truck)
        
        # Get resources for medical incident
        medical_resources = self.manager.get_resources_for_incident_type("MEDICAL")  # Test string type
        
        # Should return ambulances and medical teams
        self.assertIn(ResourceType.AMBULANCE, medical_resources)
        self.assertEqual(len(medical_resources[ResourceType.AMBULANCE]), 1)
        self.assertEqual(medical_resources[ResourceType.AMBULANCE][0], self.ambulance)
    
    def test_get_nearest_resources(self):
        """Test finding the nearest resources to a location."""
        # Add more ambulances in different zones
        ambulance2 = self.manager.add_resource(
            resource_type=ResourceType.AMBULANCE,
            location="Zone 3"
        )
        
        ambulance3 = self.manager.add_resource(
            resource_type=ResourceType.AMBULANCE,
            location="Zone 5"
        )
        
        # Get nearest ambulance to Zone 2
        nearest = self.manager.get_nearest_resources("Zone 2", ResourceType.AMBULANCE, 1)
        
        # Should be the ambulance in Zone 1 (closer than Zone 3 or Zone 5)
        self.assertEqual(len(nearest), 1)
        self.assertEqual(nearest[0], self.ambulance)
        
        # Get 2 nearest ambulances to Zone 4
        nearest_two = self.manager.get_nearest_resources("Zone 4", ResourceType.AMBULANCE, 2)
        
        # Should return 2 ambulances in order of proximity
        self.assertEqual(len(nearest_two), 2)
        # Zone order proximity to Zone 4: Zone 3, Zone 5
        self.assertEqual(nearest_two[0], ambulance2)  # Zone 3
        self.assertEqual(nearest_two[1], ambulance3)  # Zone 5
    
    def test_mark_resource_out_of_service(self):
        """Test marking a resource as out of service."""
        # Mark the ambulance as out of service
        result = self.manager.mark_resource_out_of_service(self.ambulance.id, "Maintenance")
        
        # Check that the resource was marked as out of service
        self.assertTrue(result)
        self.assertEqual(self.ambulance.status, ResourceStatus.OUT_OF_SERVICE)
        
        # Try marking a non-existent resource
        result = self.manager.mark_resource_out_of_service("NONEXISTENT")
        self.assertFalse(result)
    
    def test_mark_resource_in_service(self):
        """Test marking a resource as back in service."""
        # First mark it out of service
        self.ambulance.mark_out_of_service("Maintenance")
        
        # Now mark it back in service
        result = self.manager.mark_resource_in_service(self.ambulance.id)
        
        # Check that the resource was marked as available
        self.assertTrue(result)
        self.assertEqual(self.ambulance.status, ResourceStatus.AVAILABLE)
        
        # Try with a resource that's not out of service
        result = self.manager.mark_resource_in_service(self.fire_truck.id)
        self.assertFalse(result)
        
        # Try with a non-existent resource
        result = self.manager.mark_resource_in_service("NONEXISTENT")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()