import pandas as pd
import fastf1
import os

# Enable cache for FastF1
fastf1.Cache.enable_cache('data/cache')  # Adjust if your cache is elsewhere
YEAR = 2023
ROUND = 6
DRIVER_NUM = '4'
LAPS_CSV_FILE = 'data/raw/telemetry/races/2023/laps_2023_r6.csv'  # Your path to the CSV file

def load_lap_csv(csv_path: str) -> pd.DataFrame:
    try:
        # Load the CSV data
        laps = pd.read_csv(csv_path)
        
        print(laps.dtypes)
        
        # Filter laps for Lando Norris ('NOR')
        # Already timedelta, so we don’t need to convert again!
        lando_laps = pd.DataFrame(laps[laps['Driver'] == 'NOR'])
        # Drop deleted/malformed laps just in case
        lando_laps = lando_laps[~lando_laps['Deleted'] & lando_laps['IsAccurate']]

        # Drop NaNs in LapStartTime or LapTime
        lando_laps = lando_laps.dropna(subset=['LapStartTime', 'LapTime'])

        # Create LapEndTime
        lando_laps['LapEndTime'] = lando_laps['LapStartTime'] + lando_laps['LapTime']
        print(lando_laps.dtypes)

        return lando_laps
    
    except Exception as e:
        print(f"❌ Failed to load {csv_path} file: {e}")


def load_fastf1_data(session, driver_number):
    try:
        #                         Date     RPM  Speed  nGear  Throttle  Brake  DRS Source                   Time            SessionTime
        #                     39887 2023-05-28 14:57:09.325     0.0    0.0      0     104.0   True    0    car 0 days 02:56:08.348000 0 days 02:56:08.348000
        car_data = session.car_data[driver_number]
        #Date   Status       X       Y      Z Source                   Time            SessionTime
        # ex: 40854 2023-05-28 14:57:08.974  OnTrack -6739.0 -8965.0  512.0    pos 0 days 02:56:07.997000 0 days 02:56:07.997000
        # 40855 2023-05-28 14:57:09.434  OnTrack -6739.0 -8965.0  512.0    pos 0 days 02:56:08.457000 0 days 02:56:08.457000
        # 40856 2023-05-28 14:57:09.614  OnTrack -6739.0 -8965.0  512.0    pos 0 days 02:56:08.637000 0 days 02:56:08.637000
        pos_data = session.pos_data[driver_number]

        # Clean up and reset index for consistency
        car_data.reset_index(drop=True, inplace=True)
        pos_data.reset_index(drop=True, inplace=True)

        return car_data, pos_data
    except Exception as e:
        print(f"❌ Error loading session data {e}")

import pandas as pd

def merge_norris_monaco_2023(lap_df: pd.DataFrame, car_data: pd.DataFrame, pos_data: pd.DataFrame) -> pd.DataFrame:
    try:
        # 🕒 Step 1: Convert time columns
        
        # 🧹 Step 2: Sort all by time
        car_data = car_data.sort_values('SessionTime')
        pos_data = pos_data.sort_values('SessionTime')
        lap_df = lap_df.sort_values('LapStartTime')
        # 🔗 Step 3: Merge car_data and pos_data on SessionTime (nearest)
        telemetry = pd.merge_asof(car_data, pos_data, on='SessionTime', direction='nearest')

        # 🔍 Step 4: Assign lap number based on time interval
        telemetry['LapNumber'] = None
        for _, lap in lap_df.iterrows():
            in_lap = (telemetry['SessionTime'] >= lap['LapStartTime']) & (
                telemetry['SessionTime'] < lap.get('LapEndTime', pd.Timedelta.max))
            telemetry.loc[in_lap, 'LapNumber'] = lap['LapNumber']

        # 🧬 Step 5: Join lap info (compound, stint, pit etc.)
        final_df = telemetry.merge(
            lap_df.drop(columns=['LapStartTime', 'LapEndTime'], errors='ignore'),
            on='LapNumber',
            how='left'
        )

        print("✅ Merged Norris Monaco data successfully!")
        return final_df

    except Exception as e:
        print(f"❌ Merge failed: {e}")
        return pd.DataFrame()



def save_processed_data(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)
    
    
import pandas as pd
import fastf1
import matplotlib.pyplot as plt
import seaborn as sns

# Cache enablement for FastF1
fastf1.Cache.enable_cache('data/cache')  # Adjust if your cache is elsewhere

# Define year, round, and driver
YEAR = 2022
ROUND = 10  # Example, change to a specific race round
DRIVER_NUM = '16'  # Charles Leclerc's driver number

# Fetch the session data
session = fastf1.get_session(YEAR, ROUND, 'R')
session.load()

# Get Leclerc's car data and position data
car_data, pos_data = load_fastf1_data(session, DRIVER_NUM)

# Placeholder for weather data (to be included later)
def fetch_weather_data(session):
    # Future weather data code, for now it's just a placeholder
    weather_data = None  # Placeholder
    return weather_data

weather_data = fetch_weather_data(session)

# Merge Leclerc's telemetry data with lap data (which would come from CSV or database)
lap_df = load_lap_csv(f'data/raw/telemetry/races/{YEAR}/laps_{YEAR}_r{ROUND}.csv')  # Example path
merged_data = merge_norris_monaco_2023(lap_df, car_data, pos_data)  # This can be adjusted

# Set up visualizations
def setup_visualizations():
    sns(style="whitegrid")
    plt.figure(figsize=(14, 8))

# Analyze strategy calls and lap time (a starting point for tracking)
def analyze_strategy_calls(merged_data):
    # Example: Strategy analysis - you could expand this by tracking pit stops, tire changes, etc.
    # Let's plot lap times vs lap number
    plt.plot(merged_data['LapNumber'], merged_data['LapTime'].dt.total_seconds(), label='Lap Time (s)')
    plt.xlabel('Lap Number')
    plt.ylabel('Lap Time (seconds)')
    plt.title('Lap Times for Leclerc')
    plt.legend()
    plt.show()

# Call functions to set up the analysis
setup_visualizations()
analyze_strategy_calls(merged_data)

# Save this setup as a basis for future analysis

def main():
    session = fastf1.get_session(YEAR, ROUND, 'R')
    session.load()
    print(f"🔄 Loading session....")
    output_path = 'data/processed/lando_monaco_2023.csv'  # Path to save the processed file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # Load lap data
        # Load car and position data from FastF1
        car_data, pos_data, lap_df = load_fastf1_data(session, DRIVER_NUM)

        # Merge lap data with telemetry and position data
        merged_df = merge_norris_monaco_2023(lap_df, car_data, pos_data)
        # Save the merged dataframe to CSV
        save_processed_data(merged_df, output_path)

        print(f"✅ Data saved to {output_path}")
        #print(merged_df.head())
    
    except Exception as e:
        print(f"❌ There was an error {e} trying to save processed data")

if __name__ == '__main__':
    main()
