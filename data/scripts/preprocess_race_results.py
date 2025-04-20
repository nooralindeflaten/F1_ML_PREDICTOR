import os
import json
import pandas as pd

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw', 'race_results')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'processed', 'race_results_clean.csv')

def flatten_race_result(result, race_info):
    driver = result['Driver']
    constructor = result['Constructor']
    fastest_lap = result.get('FastestLap', {})

    return {
        'season': race_info['season'],
        'round': race_info['round'],
        'race_name': race_info['raceName'],
        'date': race_info['date'],
        'driver_id': driver['driverId'],
        'driver_name': f"{driver['givenName']} {driver['familyName']}",
        'constructor': constructor['name'],
        'grid': int(result.get('grid', 0)),
        'position': result.get('position'),
        'position_order': int(result.get('positionOrder', -1)),
        'points': float(result.get('points', 0.0)),
        'status': result.get('status'),
        'fastest_lap_time': fastest_lap.get('Time', {}).get('time', None),
    }

def load_and_flatten_all():
    all_results = []

    for filename in sorted(os.listdir(RAW_DATA_DIR)):
        if filename.endswith('.json'):
            path = os.path.join(RAW_DATA_DIR, filename)
            with open(path, 'r') as file:
                data = json.load(file)
                races = data.get("Races") or data['MRData']['RaceTable']['Races']

                for race in races:
                    for result in race['Results']:
                        flat = flatten_race_result(result, race)
                        all_results.append(flat)

    return pd.DataFrame(all_results)

def main():
    df = load_and_flatten_all()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Saved cleaned race results to {OUTPUT_PATH}")
    print(f"🔍 Preview:\n{df.head()}")

if __name__ == "__main__":
    main()
