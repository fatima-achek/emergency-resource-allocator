"""
Sample Scenarios for Emergency Resource Allocation System.

This module provides sample data for testing and demonstration purposes.
It contains predefined incidents and resources that can be loaded into the system.
"""

from src.models.incident import IncidentType
from src.models.resource import ResourceType


def load_sample_data(emergency_system):
    """
    Load sample data into the emergency system.
    
    Args:
        emergency_system: The emergency system to load data into
    """
    # Add sample resources
    resources = [
        # Ambulances
        {
            "resource_type": ResourceType.AMBULANCE,
            "location": "Zone 1",
            "capabilities": ["advanced_life_support"]
        },
        {
            "resource_type": ResourceType.AMBULANCE,
            "location": "Zone 3",
            "capabilities": ["basic_life_support"]
        },
        {
            "resource_type": ResourceType.AMBULANCE,
            "location": "Zone 5",
            "capabilities": ["advanced_life_support", "pediatric"]
        },
        
        # Fire Trucks
        {
            "resource_type": ResourceType.FIRE_TRUCK,
            "location": "Zone 2",
            "capabilities": ["ladder", "pump"]
        },
        {
            "resource_type": ResourceType.FIRE_TRUCK,
            "location": "Zone 4",
            "capabilities": ["hazmat", "pump"]
        },
        
        # Police Units
        {
            "resource_type": ResourceType.POLICE_UNIT,
            "location": "Zone 1",
            "capabilities": []
        },
        {
            "resource_type": ResourceType.POLICE_UNIT,
            "location": "Zone 3",
            "capabilities": ["k9"]
        },
        
        # Specialized Units
        {
            "resource_type": ResourceType.RESCUE_TEAM,
            "location": "Zone 2",
            "capabilities": ["water_rescue", "rope_rescue"]
        },
        {
            "resource_type": ResourceType.HAZMAT_UNIT,
            "location": "Zone 5",
            "capabilities": ["chemical", "biological"]
        },
        {
            "resource_type": ResourceType.MEDICAL_TEAM,
            "location": "Zone 3",
            "capabilities": ["trauma", "triage"]
        },
        {
            "resource_type": ResourceType.HELICOPTER,
            "location": "Zone 1",
            "capabilities": ["night_vision", "medical_transport"]
        },
        {
            "resource_type": ResourceType.COMMAND_UNIT,
            "location": "Zone 3",
            "capabilities": ["communications", "coordination"]
        }
    ]
    
    # Add resources to the system
    for resource_data in resources:
        emergency_system.resource_manager.add_resource(
            resource_type=resource_data["resource_type"],
            location=resource_data["location"],
            capabilities=resource_data.get("capabilities", [])
        )
    
    # Add sample incidents
    incidents = [
        # High priority incidents
        {
            "incident_type": IncidentType.FIRE,
            "location": "Zone 2",
            "priority": 1,
            "required_resources": ["FIRE_TRUCK", "AMBULANCE"],
            "details": "Apartment building on fire with people trapped",
            "affected_people": 15,
            "special_factors": ["children", "elderly"]
        },
        {
            "incident_type": IncidentType.MEDICAL,
            "location": "Zone 1",
            "priority": 1,
            "required_resources": ["AMBULANCE", "MEDICAL_TEAM"],
            "details": "Multiple casualty incident at shopping mall",
            "affected_people": 8,
            "special_factors": ["children"]
        },
        {
            "incident_type": IncidentType.HAZMAT,
            "location": "Zone 5",
            "priority": 1,
            "required_resources": ["HAZMAT_UNIT", "FIRE_TRUCK"],
            "details": "Chemical spill at industrial facility",
            "affected_people": 3,
            "special_factors": ["hazardous_materials"]
        },
        
        # Medium priority incidents
        {
            "incident_type": IncidentType.TRAFFIC,
            "location": "Zone 3",
            "priority": 3,
            "required_resources": ["POLICE_UNIT", "AMBULANCE"],
            "details": "Multi-vehicle accident on highway",
            "affected_people": 4,
            "special_factors": ["multi_vehicle"]
        },
        {
            "incident_type": IncidentType.RESCUE,
            "location": "Zone 4",
            "priority": 2,
            "required_resources": ["RESCUE_TEAM", "AMBULANCE"],
            "details": "Person trapped in collapsed structure",
            "affected_people": 1,
            "special_factors": []
        },
        
        # Low priority incidents
        {
            "incident_type": IncidentType.FIRE,
            "location": "Zone 3",
            "priority": 4,
            "required_resources": ["FIRE_TRUCK"],
            "details": "Small brush fire, no structures threatened",
            "affected_people": 0,
            "special_factors": []
        },
        {
            "incident_type": IncidentType.MEDICAL,
            "location": "Zone 2",
            "priority": 3,
            "required_resources": ["AMBULANCE"],
            "details": "Elderly patient with difficulty breathing",
            "affected_people": 1,
            "special_factors": ["elderly"]
        },
        {
            "incident_type": IncidentType.OTHER,
            "location": "Zone 1",
            "priority": 5,
            "required_resources": ["POLICE_UNIT"],
            "details": "Noise complaint from residential area",
            "affected_people": 0,
            "special_factors": []
        }
    ]
    
    # Add incidents to the system
    for incident_data in incidents:
        emergency_system.incident_manager.add_incident(
            incident_type=incident_data["incident_type"],
            location=incident_data["location"],
            priority=incident_data["priority"],
            required_resources=incident_data["required_resources"],
            details=incident_data.get("details", ""),
            affected_people=incident_data.get("affected_people", 0),
            special_factors=incident_data.get("special_factors", [])
        )
    
    # Log the data loading
    emergency_system.logger.log_info(f"Loaded {len(resources)} sample resources and {len(incidents)} sample incidents")
    
    return len(resources), len(incidents)


def load_critical_scenario(emergency_system):
    """
    Load a critical emergency scenario with multiple high-priority incidents
    and limited resources to test the reallocation algorithm.
    
    Args:
        emergency_system: The emergency system to load data into
    """
    # Start with a clean system
    emergency_system.reset()
    
    # Add limited resources
    resources = [
        {
            "resource_type": ResourceType.AMBULANCE,
            "location": "Zone 2",
            "capabilities": ["advanced_life_support"]
        },
        {
            "resource_type": ResourceType.FIRE_TRUCK,
            "location": "Zone 3",
            "capabilities": ["ladder", "pump"]
        },
        {
            "resource_type": ResourceType.POLICE_UNIT,
            "location": "Zone 1",
            "capabilities": []
        },
        {
            "resource_type": ResourceType.HAZMAT_UNIT,
            "location": "Zone 4",
            "capabilities": ["chemical"]
        }
    ]
    
    # Add resources to the system
    for resource_data in resources:
        emergency_system.resource_manager.add_resource(
            resource_type=resource_data["resource_type"],
            location=resource_data["location"],
            capabilities=resource_data.get("capabilities", [])
        )
    
    # Add initial incidents
    initial_incidents = [
        {
            "incident_type": IncidentType.MEDICAL,
            "location": "Zone 2",
            "priority": 3,
            "required_resources": ["AMBULANCE"],
            "details": "Patient with chest pain",
            "affected_people": 1,
            "special_factors": ["elderly"]
        },
        {
            "incident_type": IncidentType.TRAFFIC,
            "location": "Zone 1",
            "priority": 3,
            "required_resources": ["POLICE_UNIT"],
            "details": "Minor traffic accident, no injuries",
            "affected_people": 2,
            "special_factors": []
        }
    ]
    
    # Add incidents to the system
    for incident_data in initial_incidents:
        emergency_system.incident_manager.add_incident(
            incident_type=incident_data["incident_type"],
            location=incident_data["location"],
            priority=incident_data["priority"],
            required_resources=incident_data["required_resources"],
            details=incident_data.get("details", ""),
            affected_people=incident_data.get("affected_people", 0),
            special_factors=incident_data.get("special_factors", [])
        )
    
    # Allocate resources to initial incidents
    emergency_system.dispatcher.allocate_resources()
    
    # Add a critical incident that will require reallocation
    critical_incident = {
        "incident_type": IncidentType.FIRE,
        "location": "Zone 3",
        "priority": 1,
        "required_resources": ["FIRE_TRUCK", "AMBULANCE"],
        "details": "Major building fire with multiple people trapped",
        "affected_people": 12,
        "special_factors": ["children", "elderly", "public_building"]
    }
    
    # Add the critical incident
    critical = emergency_system.incident_manager.add_incident(
        incident_type=critical_incident["incident_type"],
        location=critical_incident["location"],
        priority=critical_incident["priority"],
        required_resources=critical_incident["required_resources"],
        details=critical_incident.get("details", ""),
        affected_people=critical_incident.get("affected_people", 0),
        special_factors=critical_incident.get("special_factors", [])
    )
    
    # Log the scenario setup
    emergency_system.logger.log_info("Loaded critical scenario with reallocation requirements")
    
    return critical.id