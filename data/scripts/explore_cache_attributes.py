import fastf1
import pandas as pd

# Enable FastF1 cache 
fastf1.Cache.enable_cache('data/cache')


# List of parent attributes to inspect (skip 'laps' since you have it in CSV)
parent_attributes = [
    'driver_info',
    'car_data', 
    'pos_data', 
    'weather_data', 
    'race_control_messages', 
    'session_info', 
    'results', 
    'track_status'
]

# Function to check if an attribute is an object and display its dir
def explore_parent_attributes(parent_attr,session):
    attribute = getattr(session, parent_attr, None)
    
    if attribute is not None:
        print(f"\nExploring {parent_attr}...\n")
        # If it's an object, get its available methods and attributes
        if hasattr(attribute, '__dict__'):
            # If it's an object, print its attributes and methods
            for attr in dir(attribute):
                if not attr.startswith('__'):
                    print(f" - {attr}")
        else:
            # Otherwise just show the data (if it's a simple list or DataFrame)
            print(attribute.head() if isinstance(attribute, pd.DataFrame) else attribute)
    else:
        print(f"{parent_attr} is not available or not loaded.")

def explore_specific(index_of_parent_attr,session):
    explore_parent_attributes(parent_attributes[index_of_parent_attr],session)
# Iterate over each parent attribute and explore it


if __name__=="__main__":
    #Default value as 0 when not using. 
    session = fastf1.get_session(2023, 6, 'R')  # Round 5 Race
    session.load()
    
    # this get's the car data. 
    laps = session.laps.loc[session.laps['Driver'] == 'NOR']

    
    print(laps)
    
    
        # Check if an attribute is a DataFrame