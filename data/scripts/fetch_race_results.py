import requests
import os
import json

# Define the range of seasons you want to fetch
START_YEAR = 2018
END_YEAR = 2023  # You can adjust this as needed

# Output directory for raw data
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw', 'race_results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Base URL for Ergast API
BASE_URL = "http://ergast.com/api/f1/{season}/results.json?limit=100"


def fetch_race_results(season):
    page = 0
    all_races = []
    try:
        while True:
            offset = page * 100
            url = BASE_URL.format(season=season) + f"&offset={offset}"
            print(f"🌍 Fetching results for {season}, offset {offset}...")
                
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            races = data['MRData']['RaceTable']['Races']
            
            if not races:
                print("No more races to fetch")
                break
            
            # Adding the iterable object to the list. 
            all_races.extend(races)
            page += 1
        
        output_path = os.path.join(OUTPUT_DIR, f"race_results_{season}.json")
        with open(output_path, 'w') as f:
            json.dump({'Races': all_races}, f, indent=4)
        print(f"💾 Saved {len(all_races)} races to: {output_path}")  
           
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error while fetching {season}, page {page}: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error for {season}, page {page}: {e}")
    except Exception as e:
        print(f"❌ Unexpected error for {season}, page {page}: {e}")

if __name__ == "__main__":
    for year in range(START_YEAR, END_YEAR + 1):
        fetch_race_results(year)
