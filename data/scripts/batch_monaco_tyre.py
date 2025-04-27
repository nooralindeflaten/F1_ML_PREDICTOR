import pandas as pd
from pathlib import Path
import datetime as dt
import fastf1
# Enable cache for fastf1
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')

# Where to save the batched result
OUTPUT_PATH = Path("/Users/nooralindeflaten/f1_ML_predictor/data/processed/laps_with_weather_monaco.pkl")


def pre_process_laps(laps, weather):
    """
    Add weather columns and convert lap times to seconds
    Time                  timedelta64[ns] -> This is a timestamp for the lap end, it's equal to the next lap's LapStartTime
    Driver                         object x
    DriverNumber                   object x
    LapTime               timedelta64[ns] -> we chould keep this as seconds since it's the duration of a lap
    LapNumber                     float64 x
    Stint                         float64 x
    PitOutTime            timedelta64[ns] -> this is the timestamp of the pit out, so time_delta?
    PitInTime             timedelta64[ns] -> This is the timestamp of the pit in, so time_delta?
    Sector1Time           timedelta64[ns] -> we should keep this as seconds since it's the duration of sector1
    Sector2Time           timedelta64[ns] -> we should keep this as seconds since it's the duration of sector2
    Sector3Time           timedelta64[ns] -> we should keep this as seconds since it's the duration of sector3
    Sector1SessionTime    timedelta64[ns] -> this is the timestamp for the start of sector1 so time_delta?
    Sector2SessionTime    timedelta64[ns] -> this is the timestamp for the start of sector2 so time_delta?
    Sector3SessionTime    timedelta64[ns] -> this is the timestamp for the start of sector3 so time_delta?
    SpeedI1                       float64
    SpeedI2                       float64
    SpeedFL                       float64
    SpeedST                       float64
    IsPersonalBest                 object
    Compound                       object
    TyreLife                      float64
    FreshTyre                        bool
    Team                           object
    LapStartTime          timedelta64[ns] -> this is the timestamp for the start of the lap so time_delta?
    
    to find the closes weather we'll look at the lap_start time and find the closest weather row and add the columns to our data_frame
    
    To be able to easily use this data set with the fastf1 library is this the best way? Convert the data like this and save it as a pickle file or batch? 
    
    - Keeps timestamp columns as timedeltas for FastF1 compatibility
    - Converts only true durations to seconds (LapTime, Sector1/2/3Time)
    - Adds closest weather data by LapStartTime
    """

    # Ensure columns are in correct types
    laps["LapStartTime"] = pd.to_timedelta(laps["LapStartTime"])
    laps["Time"] = pd.to_timedelta(laps["Time"])
    laps["PitInTime"] = pd.to_timedelta(laps["PitInTime"])
    laps["PitOutTime"] = pd.to_timedelta(laps["PitOutTime"])
    weather["Time"] = pd.to_timedelta(weather["Time"])

    # Convert only duration columns to seconds
    duration_cols = ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]
    for col in duration_cols:
        if col in laps.columns and pd.api.types.is_timedelta64_dtype(laps[col]):
            laps[col] = laps[col].dt.total_seconds()

    # Sort both for merge_asof
    laps = laps.sort_values("LapStartTime").reset_index(drop=True)
    if weather is not None:
        weather = weather.sort_values("Time").reset_index(drop=True)

        # Merge closest weather row based on LapStartTime
        laps = pd.merge_asof(laps, weather, left_on="LapStartTime", right_on="Time", direction="nearest")

    return laps

            
def load_session_data(session_name, years, season_rounds):
    """
    Load session data for all years in a specific session type for a given track
    """
    try:
        # Load the track status data and create a mapping dictionary
        # Loop through the years and rounds
        session_data = []
        for year, round_num in zip(years, season_rounds):
            try:
                    # load the session data for the year and round
                    session = fastf1.get_session(year, round_num, session_name)
                    session.load()
                    laps = session.laps
                    weather_data = laps.get_weather_data()
                    
                    if laps.empty:
                        print(f"No laps data for {session_name} {year} round {round_num}")
                        continue
                    # Convert lap times to seconds
                    
                    processed_df = pre_process_laps(laps, weather_data)
                    # Add year and round columns
                    processed_df["year"] = year
                    processed_df["round"] = round_num
                    # Add session type column
                    processed_df["session_type"] = session_name
                    session_data.append(processed_df)
            except Exception as e:
                print(f"❌Error processing {session_name} {year} round {round_num}: {e}")
        # Combine all session data into one dataframe
        return pd.concat(session_data, ignore_index=True)
    except Exception as e:
        print(f"📈An error occurred: {e}")


def clean_lap_data(df):
    '''
    Drop NaN or 0 lap time
    When dropping pit laps, we need to check the PitInTime and PitOutTime columns
    In a lap without these values there's no value. Example:
    0 days 01:30:53.974000,VER,1,0 days 00:01:39.466000,18.0,1.0,,0 days 01:30:37.751000,0 days 00:00:29.368000,0 days 00:00:18.600000,0 days 00:00:51.498000,0 days 01:29:43.904000,0 days 01:30:02.504000,0 days 01:30:54.002000,264.0,296.0,,,False,MEDIUM,18.0,True,Red Bull Racing,0 days 01:29:14.508000,2022-04-10 05:30:14.519,1,7.0,False,,False,False
    without pit in or out time there's simply a ',' in human readable format
    
    Also drop laps with TyreLife = 0
    If lap-time was deleted lap['Deleted'] == True, we need to drop the lap
    '''
    # Check the number of rows before cleaning
    print(f"Rows before cleaning: {len(df)}")

    # Drop rows with NaN or 0 lap time
    df = df.dropna(subset=["LapTime"])
    df = df[df["LapTime"] > 0]
    
    # Check after filtering LapTime
    print(f"Rows after filtering LapTime: {len(df)}")

    # Drop laps with TyreLife = 0
    if "TyreLife" in df.columns:
        df = df[df["TyreLife"] > 0]

    # Drop laps with Deleted = True
    if "Deleted" in df.columns:
        df = df[df["Deleted"] != True]

    # Final check after all filters
    print(f"Rows after final cleaning: {len(df)}")
    
    # Filter columns
    return df

# batch all lap cleaned lap data for the sessions produced by the load_csv_data function
def batch_all_lap_data():
    # Define the session types and years to process
    # testing for FP1 first
    session_types = ["FP1","FP2","FP3","Q","R"]
    years = [2018,2019,2021,2022,2023]
    season_rounds = [6,6,5,7,6]

    all_lap_data = []

    for session_type in session_types:
        try:
            df = load_session_data(session_type, years, season_rounds)
            if df is not None:
                all_lap_data.append(df)
        except Exception as e:
            print(f"💾Error processing session type {session_type}: {e}")

    # Only continue if we actually loaded something
    if all_lap_data:
        try:
            combined_df = pd.concat(all_lap_data, ignore_index=True)
            cleaned_lap_data = clean_lap_data(combined_df)
            cleaned_lap_data.to_pickle(OUTPUT_PATH)
            print(f"✅Saved processed dataset to {OUTPUT_PATH}")
        except Exception as e:
            print(f"❌Error during cleaning🧼 or saving💾: {e}")
    else:
        print("🚩No data loaded. Skipping cleaning and saving.")


def inspect_data():
    """
    Inspect the data
    """
    try:
        df = pd.read_pickle(OUTPUT_PATH)
        # print information about the dataframe
        print(df.head())
        print(df.info())
        print(df.describe())
        print(f"Data loaded successfully from {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"❌Error loading data for inspection: {e}")
        
if __name__ == "__main__":
    inspect_data()