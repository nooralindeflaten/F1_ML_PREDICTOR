import fastf1
import pandas as pd
import os
from tqdm import tqdm

# Enable FastF1 cache if still useful
fastf1.Cache.enable_cache('data/cache')

def fetch_and_save_telemetry(year, round_number):
    filename = f'data/raw/telemetry/laps_{year}_r{round_number}.csv'
    if os.path.exists(filename):
        print(f"⏩ Skipping {filename}, already exists")
        return

    try:
        session = fastf1.get_session(year, round_number, 'R')
        print(f"Calling session load for {year} round {round_number}")
        session.load()
        print(f"Call complete")
        laps = session.laps
        if laps.empty:
            print(f"⚠️ No lap data for {year} Round {round_number}")
            return

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        laps.to_csv(filename, index=False)
        print(f"✅ Saved: {filename}")

    except Exception as e:
        print(f"❌ Failed for {year} Round {round_number}: {e}")

if __name__ == '__main__':
    race_df = pd.read_csv('data/processed/race_results_clean.csv')
    races = race_df[['season', 'round']].drop_duplicates()

    print(f"📦 Fetching telemetry for {len(races)} races...")
    for _, row in tqdm(races.iterrows(), total=len(races)):
        fetch_and_save_telemetry(row['season'], row['round'])
