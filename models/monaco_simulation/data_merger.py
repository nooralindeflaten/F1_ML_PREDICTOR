import pandas as pd
import fastf1
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')  # Enable cache for faster data loading

def merge_laps_for_session(laps_df, gaps_df):
    # Fix Driver IDs
    laps_df['DriverID'] = laps_df['DriverNumber']
    gaps_df['DriverID'] = gaps_df['Driver']

    # Force times to be timedelta
    laps_df['LapStartTime'] = pd.to_timedelta(laps_df['LapStartTime'])
    gaps_df['Time'] = pd.to_timedelta(gaps_df['Time'])

    # Merge keys
    merge_keys = ['DriverID']

    # Correct sorting
    laps_df = laps_df.sort_values(by=merge_keys + ['LapStartTime']).reset_index(drop=True)
    gaps_df = gaps_df.sort_values(by=merge_keys + ['Time']).reset_index(drop=True)

    # Merge
    merged_df = pd.merge_asof(
        left=laps_df,
        right=gaps_df[['DriverID','Time', 'GapToLeader', 'IntervalToPositionAhead']],
        by=merge_keys,
        left_on='LapStartTime',
        right_on='Time',
        direction='nearest',
        tolerance=pd.Timedelta(seconds=5)
    )

    return merged_df

def merge_laps_with_gaps(laps_df, gaps_df):
    merged_df = []

    # Find all unique (year, round, session_type) combinations
    sessions = laps_df[['year', 'round', 'session_type']].drop_duplicates()

    for _, row in sessions.iterrows():
        year, round_, session = row['year'], row['round'], row['session_type']

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

        if not session_laps.empty and not session_gaps.empty:
            merged_session = merge_laps_for_session(session_laps, session_gaps)
            merged_df.append(merged_session)

    return pd.concat(merged_df, ignore_index=True) if merged_df else pd.DataFrame()
