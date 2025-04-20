import fastf1
import pandas as pd
import os

# Enable FastF1 cache
fastf1.Cache.enable_cache('data/cache')

# --- Configuration ---
DATA_FOLDER = 'data/raw/telemetry/races/2023'
YEAR = 2023

# DataFrames to extract – remove 'laps' here if already saved
DATAFRAMES_TO_EXTRACT = [
    'results',
    'weather_data',
    'race_control_messages',
    'session_status',
    'track_status',
    'car_data',       # Will be handled as callable
    'pos_data',
]

def save_dataframe(df: pd.DataFrame, name: str, year: int, rnd: int):
    if df is None or df.empty:
        print(f"[!] Skipping empty or missing: {name}")
        return
    
    os.makedirs(DATA_FOLDER, exist_ok=True)
    filename = f"{name}_{year}_{rnd}.csv"
    filepath = os.path.join(DATA_FOLDER, filename)

    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"[↩️] File exists, skipping: {filepath}")
        return

    df.to_csv(filepath, index=False)
    print(f"[✓] Saved {name} to {filepath}")

def main(year: int, round_number: int):
    print(f"\n📦 Fetching race session {year} - Round {round_number}")
    session = fastf1.get_session(year, round_number, 'R')
    session.load()

    for attr in DATAFRAMES_TO_EXTRACT:
        try:
            data = getattr(session, attr, None)

            # Special handling for callable attributes like car_data and pos_data
            if callable(data):
                data = data()
            elif hasattr(data, 'get_car_data'):  # object-like wrapper
                data = data

            if isinstance(data, pd.DataFrame):
                save_dataframe(data, attr, year, round_number)
            else:
                print(f"[!] {attr} is not a DataFrame")

        except Exception as e:
            print(f"[X] Failed to extract {attr} from round {round_number}: {e}")

if __name__ == "__main__":
    race_rounds_per_year = {
        2018: 21,
        2019: 21,
        2020: 17,
        2021: 22,
        2022: 22,
        2023: 22
    }

    rounds = race_rounds_per_year[YEAR]

    for rnd in range(1, rounds + 1):
        try:
            main(YEAR, rnd)
        except Exception as e:
            print(f"❌ Failed to handle round {rnd}: {e}")

