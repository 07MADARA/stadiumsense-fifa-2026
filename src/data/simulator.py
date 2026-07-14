import random
import time
from typing import Dict, List, Any

# Represents the stadium zones and base capacities
STADIUM_ZONES = {
    "Gate A (North)": {"capacity": 500, "type": "entry"},
    "Gate B (South)": {"capacity": 500, "type": "entry"},
    "Gate C (East)": {"capacity": 400, "type": "entry"},
    "Gate D (West)": {"capacity": 400, "type": "entry"},
    "Concourse Level 1": {"capacity": 2000, "type": "concourse"},
    "Concourse Level 2": {"capacity": 1500, "type": "concourse"},
    "Food Court A": {"capacity": 300, "type": "concessions"},
    "Food Court B": {"capacity": 250, "type": "concessions"},
    "Restrooms North": {"capacity": 100, "type": "restroom"},
    "Restrooms South": {"capacity": 120, "type": "restroom"},
}

def generate_telemetry_data() -> Dict[str, Any]:
    """
    Simulates real-time IoT sensor data across the stadium.
    Returns a dictionary containing crowd density metrics.
    """
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    zones_data: List[Dict[str, Any]] = []
    
    # Simulate a scenario where one gate and one food court are suddenly busy
    event_spike = random.choice(list(STADIUM_ZONES.keys()))

    for zone, info in STADIUM_ZONES.items():
        base_occupancy = random.uniform(0.3, 0.6) # Base 30-60% full
        
        # Add a spike to simulate an issue
        if zone == event_spike:
            base_occupancy = random.uniform(0.85, 1.1) # 85-110% full (bottleneck)
            
        current_count = int(info["capacity"] * base_occupancy)
        density_percentage = round((current_count / info["capacity"]) * 100, 1)
        
        status = "Normal"
        if density_percentage > 90:
            status = "Critical Bottleneck"
        elif density_percentage > 75:
            status = "Warning - High Density"
            
        zones_data.append({
            "zone_name": zone,
            "zone_type": info["type"],
            "current_occupancy": current_count,
            "max_capacity": info["capacity"],
            "density_percentage": density_percentage,
            "status": status
        })
        
    return {
        "timestamp": timestamp,
        "event": "FIFA World Cup 2026",
        "stadium_zones": zones_data
    }

if __name__ == "__main__":
    import json
    print(json.dumps(generate_telemetry_data(), indent=2))
