import fastf1
import pandas as pd
import os
import argparse

# Enable FastF1 cache
fastf1.Cache.enable_cache('data/cache')

# ---------------------- Configuration ----------------------
SESSIONS_BY_TYPE = {
    'R': 'races',
    'Q': 'qualifying',
    'S': 'sprint',
    'FP1': 'practice/FP1',
    'FP2': 'practice/FP2',
    'FP3': 'practice/FP3'
}

YEARS_AND_ROUNDS = {
    #2018: 21,
    #2019: 21,
    #2020: 17,
    #2021: 22,
    #2022: 22,
    2023: 22,
}

DATAFRAMES_TO_EXTRACT = [
    'laps',
    'results',
    'weather_data',
    'race_control_messages',
    'session_status',
    'track_status'
]
# -----------------------------------------------------------

def save_dataframe(df: pd.DataFrame, name: str, folder: str, year: int, rnd: int):
    if df is None or df.empty:
        print(f"[!] Skipping empty or missing: {name}")
        return
    folder_path = os.path.join('data/raw/telemetry', folder, str(year))
    os.makedirs(folder_path, exist_ok=True)
    filename = f"{name}_{year}_{rnd}.csv"
    df.to_csv(os.path.join(folder_path, filename), index=False)
    print(f"[✓] Saved {name} to {folder}/{year}/{filename}")

def extract_session_data(year: int, round_number: int, session_type: str):
    print(f"\n📦 Fetching {session_type} session {year} - Round {round_number}")
    try:
        session = fastf1.get_session(year, round_number, session_type)
        session.load()

        for attr in DATAFRAMES_TO_EXTRACT:
            try:
                data = getattr(session, attr, None)
                if isinstance(data, pd.DataFrame):
                    folder = SESSIONS_BY_TYPE[session_type]
                    save_dataframe(data, attr, folder, year, round_number)
                else:
                    print(f"[!] {attr} is not a DataFrame")
            except Exception as e:
                print(f"[X] Failed to extract {attr}: {e}")
    except Exception as e:
        print(f"[X] Failed to load session: {e}")

def main(session_type: str):
    if session_type not in SESSIONS_BY_TYPE:
        print(f"❌ Invalid session type '{session_type}'")
        print(f"Valid types: {list(SESSIONS_BY_TYPE.keys())}")
        return
    for year, max_round in YEARS_AND_ROUNDS.items():
        for rnd in range(1, max_round + 1):
            extract_session_data(year, rnd, session_type)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', required=True, help="Session type: R, Q, S, FP1, FP2, FP3")
    args = parser.parse_args()
    main(args.type.upper())
