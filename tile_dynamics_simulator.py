import random
import time
from datetime import datetime, timedelta

def random_recent_timestamp_ms(days: int) -> int:
    """Returns a random timestamp in milliseconds from the last `days` days."""
    now = datetime.utcnow()
    past = now - timedelta(days=days)
    random_seconds = random.randint(0, int((now - past).total_seconds()))
    dt = past + timedelta(seconds=random_seconds)
    return int(dt.timestamp() * 1000)  # milliseconds

def simulate_tile_dynamics(tiles_map):
    print("simulate_tile_dynamics...")
    try:
        # random Dynamics
        event_to_dynamic = {
            'flood': 'FLOOD',
            'construction': 'CONSTRUCTION',
            'maintenance': 'MAINTENANCE',
            'emergency': 'EMERGENCY',
            'public_event': 'PUBLIC_EVENT',
            'closure': 'CLOSURE',
            'demo': 'DEMO',
            'police': 'POLICE'
        }
        event_pool = list(event_to_dynamic.keys())
        for tile_id in tiles_map.keys():
            num_events = random.choices([0, 1, 2], weights=[0.997, 0.002, 0.001])[0]
            chosen_events = random.sample(event_pool, num_events)
            dynamics = [{'type': event_to_dynamic[event], 'timestamp': random_recent_timestamp_ms(7)} for event in chosen_events]
            tiles_map[tile_id]['dynamics'] = dynamics
    except Exception as e:
        print(f"Error simulate_tile_dynamics: {e}")
