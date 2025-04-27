import pandas as pd
import pickle
from pathlib import Path
import fastf1

fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')
# Your cache folder
CACHE_BASE = Path("/Users/nooralindeflaten/f1_ML_predictor/data/cache/")

# Monaco-specific settings
MONACO_YEARS = [2018, 2019, 2021, 2022, 2023]
ROUND_MAP = {
    2018: 6,
    2019: 6,
    2021: 5,
    2022: 7,
    2023: 6
}
SESSION_TYPES = ['Practice_1', 'Practice_2', 'Practice_3', 'Qualifying', 'Race']
SESSION_NAMES = {
    'Practice_1': 'FP1',
    'Practice_2': 'FP2',
    'Practice_3': 'FP3',
    'Qualifying': 'Q',
    'Race': 'R'
}

def find_session_folder(year, session_type):
    year_folder = CACHE_BASE / str(year)
    race_folders = list(year_folder.glob("*Monaco_Grand_Prix"))

    if not race_folders:
        print(f"❌ No Monaco race folder for {year}")
        return None

    for race_folder in race_folders:
        # Match subfolders that CONTAIN the session_type like "Practice_1", "Race", etc
        session_folders = list(race_folder.glob(f"*{session_type}*"))
        if session_folders:
            return session_folders[0]

    print(f"⚠️ No session {session_type} found for Monaco {year}")
    return None

def extract_gap_data_direct(year, round_number, session_type, session_name):
    session_folder = find_session_folder(year, session_type)
    if session_folder is None:
        return None

    file_path = session_folder / "_extended_timing_data.ff1pkl"

    if not file_path.exists():
        print(f"⚠️ No _extended_timing_data for {year} {session_type}")
        return None

    try:
        print(f"Loading timing data for {year} {session_type} from {file_path}")
        with open(file_path, 'rb') as f:
            timing_data = pickle.load(f)

        gap_data = timing_data['data'][1]  # second part = gap data
        print(f"Loaded gap data for {year} {session_type}: {gap_data.shape} rows")
        gap_data['year'] = year
        gap_data['round'] = round_number
        gap_data['session_type'] = session_name

        return gap_data
    except Exception as e:
        print(f"❌ Failed to load timing data for {year} {session_type}: {e}")
        return None

def batch_monaco_gaps():
    all_gap_data = []

    for year in MONACO_YEARS:
        round_number = ROUND_MAP[year]
        for session_type in SESSION_TYPES:
            session_name = SESSION_NAMES[session_type]
            gap_df = extract_gap_data_direct(year, round_number, session_type,session_name)
            if gap_df is not None:
                all_gap_data.append(gap_df)

    if all_gap_data:
        combined_df = pd.concat(all_gap_data, ignore_index=True)
        combined_df.to_pickle("/Users/nooralindeflaten/f1_ML_predictor/data/processed/monaco_timing_gaps.pkl")
        print(f"✅ Saved combined Monaco timing gaps: {combined_df.shape} rows!")
    else:
        print("⚠️ No gap data found, nothing saved.")

def inspect_data():
    """
    Inspect the data
    """
    gap_data = pd.read_pickle("/Users/nooralindeflaten/f1_ML_predictor/data/processed/monaco_timing_gaps.pkl")
    print(gap_data.head())
    print(gap_data.info())
    print(gap_data.describe())
    
if __name__ == "__main__":
    inspect_data()
