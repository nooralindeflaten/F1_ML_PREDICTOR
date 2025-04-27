import pandas as pd
from pathlib import Path
import fastf1
# Enable cache for fastf1
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')

def merge_laps_for_session(laps_df, gaps_df):

    # Force times to be timedelta
    laps_df['LapStartTime'] = pd.to_timedelta(laps_df['LapStartTime'])
    gaps_df['Time'] = pd.to_timedelta(gaps_df['Time'])

    # Merge keys

    # Correct sorting
    merged_df = []
    # Merge
    drivers = laps_df['DriverNumber'].unique()
    
    print(f"🚗 Starting merging by driver")
    for driver in drivers:
        driver_laps = laps_df[laps_df['DriverNumber'] == driver].copy()
        driver_gaps = gaps_df[gaps_df['Driver'] == driver].copy()

        driver_laps = driver_laps.sort_values('LapStartTime').reset_index(drop=True)
        try:
            driver_gaps = driver_gaps.sort_values('Time').reset_index(drop=True)
            merged_driver = pd.merge_asof(
                left=driver_laps,
                right=driver_gaps[['Time','Position','GapToLeader', 'IntervalToPositionAhead']],
                left_on='LapStartTime',
                right_on='Time',
                direction='nearest'
            )
            merged_df.append(merged_driver)
        except Exception as e:
            print(f"❌ Error merging laps and gaps for driver {driver}: {e}")
        
    return pd.concat(merged_df, ignore_index=True)

def merge_laps_with_gaps(laps_df, gaps_df):
    """
    Merge laps and gap timing data across all sessions considering year, round, session_type.

    Args:
        laps_df (pd.DataFrame): Clean laps data (laps_with_weather_monaco)
        gaps_df (pd.DataFrame): Timing gaps data (timing_gaps_monaco)

    Returns:
        merged_df (pd.DataFrame)
    """

    merged_sessions = []

    
    # Group by year, round, session_type
    sessions = laps_df[['year', 'round', 'session_type']].drop_duplicates()

    for _, row in sessions.iterrows():
        year = row['year']
        round_ = row['round']
        session = row['session_type']
        print(f"Merging laps and gaps for {year} {round_} {session}")

        session_laps = laps_df[
            (laps_df['year'] == year) &
            (laps_df['round'] == round_) &
            (laps_df['session_type'] == session)
        ].copy()

        session_gaps = gaps_df[
            (gaps_df['year'] == year) &
            (gaps_df['round'] == round_) &
            (gaps_df['session_type'] == session)
        ].copy()

        if session_laps.empty or session_gaps.empty:
            continue
        
        print(f"💾 Loading session laps and gaps for merging")
        merged = merge_laps_for_session(session_laps, session_gaps)
        merged_sessions.append(merged)
        print(f"✅ Merged laps and gaps for {year} {round_} {session}: {merged.shape[0]} rows")
    
    return pd.concat(merged_sessions, ignore_index=True)

def batch_monaco_laps_with_gaps():
    # Load existing processed data
    laps_path = Path("/Users/nooralindeflaten/f1_ML_predictor/data/processed/laps_with_weather_monaco.pkl")
    gaps_path = Path("/Users/nooralindeflaten/f1_ML_predictor/data/processed/monaco_timing_gaps.pkl")
    
    print(f"Loading laps from: {laps_path}")
    laps_df = pd.read_pickle(laps_path)
    
    print(f"Loading gaps from: {gaps_path}")
    gaps_df = pd.read_pickle(gaps_path)
    
    # Merge laps and gaps
    print("Merging laps with gaps...")
    merged_laps = merge_laps_with_gaps(laps_df, gaps_df)
    
    print(f"Merged dataset shape: {merged_laps}")
    
    # Save new dataset
    output_path = Path("/Users/nooralindeflaten/f1_ML_predictor/data/processed/laps_with_weather_gaps_monaco.pkl")
    merged_laps.to_pickle(output_path)
    
    print(f"✅ Saved merged laps+weather+gaps dataset to {output_path}")

if __name__ == "__main__":
    batch_monaco_laps_with_gaps()
