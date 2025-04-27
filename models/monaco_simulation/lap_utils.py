import pandas as pd
from fastf1 import get_session
from fastf1.core import Laps
from typing import Literal

# Calculates the average of car data behaviour Speed, RPM, Throttle, Break of all laps
def calculate_average_car_data(driver_laps: Laps):
    """
    Calculate the average car data for a specific driver and car data type.
    
    Parameters:
        driver_laps (Laps): The laps object containing telemetry data for a specific driver
        
    Calculates:
        using the get_car_data() method of the lap object, it calculates the average of the specified car data type.
        car_data (str): The type of car data to calculate the average for ('Speed', 'RPM', 'Throttle', 'Brake').
        
    Returns:
        pd.DataFrame: A DataFrame containing the average car data for the specified driver and car data type.
    """
    lap_data_df = []
    # Get the telemetry data for the specified driver
    for _, lap in driver_laps.iterlaps():
        try:
            car_data = lap.get_car_data()
            # Calculate the average of the specified car data type
            avg_speed = car_data['Speed'].mean()
            avg_rpm = car_data['RPM'].mean()
            avg_throttle = car_data['Throttle'].mean()
            avg_brake = car_data['Brake'].mean()
            
            lap_data_df.append({
                'LapNumber': lap['LapNumber'],
                'speed_avg': avg_speed,
                'rpm_avg': avg_rpm,
                'throttle_avg': avg_throttle,
                'brake_avg': avg_brake,
            })
    
        except AttributeError:
            print(f"Lap {lap['LapNumber']} does not have car data.")
            continue
    # Convert the list of dictionaries to a DataFrame
    lap_data_df = pd.DataFrame(lap_data_df)
    return lap_data_df



# Get corner info
# Returns the corners DataFrame with cleaned/filtered values.
# Adds things like entry/exit classification later if needed.
def get_circuit_corners(corners):
    corner_data = []
    for corner in corners.iterrows():
        if corner['X'] is not None and corner['Y'] is not None:
            corner_data.append({
                'Number': corner['Number'],
                'X': corner['X'],
                'Y': corner['Y'],
                'Angle': corner['Angle'],
                'Distance': corner['Distance']
            })
    return pd.DataFrame(corner_data)

# Get's the car data for a specific section of the track
def slice_car_data_by_distance(car_data, start_m, end_m):
    return car_data[(car_data['Distance'] >= start_m) & (car_data['Distance'] <= end_m)].reset_index(drop=True)

# divide breaking data into sections using lap.get_car_data() where Break column == True
def slice_car_data_by_brake(car_data):
    """Return a list of tuples with start and end index of brake sections."""
    brake_data = car_data[car_data['Brake'] == True].reset_index()
    brake_zones = []

    if brake_data.empty:
        return brake_zones

    current_start = brake_data.loc[0, 'index']
    previous_index = brake_data.loc[0, 'index']

    for i in range(1, len(brake_data)):
        current_index = brake_data.loc[i, 'index']
        if current_index - previous_index > 1:
            # end of a braking zone
            brake_zones.append((current_start, previous_index))
            current_start = current_index
        previous_index = current_index

    brake_zones.append((current_start, previous_index))  # add final zone
    return brake_zones



# build breaking sones grouping values by distance from the break sections
def build_brake_zones(car_data, brake_sections):
    """
    Use the break sections to find the start and end of the brake zones.
    Use the full car_data to get the telemetry data for those zones.
    The brake_zones will be a DataFrame will contain average telemetry data for each zone
    Then we can see how much breaking vs throttle was used in each zone.
    """
    brake_zones = []
    current_brake_zone = []
    for i, section in brake_sections.iterrows():
        start_distance = section['Distance'] - 10  # Adjust as needed
        end_distance = section['Distance'] + 10  # Adjust as needed
        car_data_slice = slice_car_data_by_distance(car_data, start_distance, end_distance)
        telemetry_averages = compute_telemetry_averages(car_data_slice)
        current_brake_zone.append({
            'BreakSection': i,
            'StartDistance': start_distance,
            'EndDistance': end_distance,
            'speed_avg': telemetry_averages['speed_avg'],
            'rpm_avg': telemetry_averages['rpm_avg'],
            'throttle_avg': telemetry_averages['throttle_avg'],
            'brake_pct': telemetry_averages['brake_pct'],
        })
    return pd.DataFrame(brake_zones)

# compute telemetry data for a specific driver segment
def compute_telemetry_averages(car_data_slice):
    return {
        'speed_avg': car_data_slice['Speed'].mean(),
        'rpm_avg': car_data_slice['RPM'].mean(),
        'throttle_avg': car_data_slice['Throttle'].mean(),
        'brake_pct': car_data_slice['Brake'].sum() / len(car_data_slice)
    }


# Tag position data with corner
def tag_position_with_corners(pos_data, track_map):
    # `track_map` should have corner definitions: [(corner_id, x_min, x_max, y_min, y_max), ...]
    pos_data['corner'] = None
    for cid, xmin, xmax, ymin, ymax in track_map:
        mask = (pos_data['X'] >= xmin) & (pos_data['X'] <= xmax) & (pos_data['Y'] >= ymin) & (pos_data['Y'] <= ymax)
        pos_data.loc[mask, 'corner'] = cid
    return pos_data

# Finding closest pos data to corner
# Finds the row in pos_data with the smallest Euclidean distance to the corner.
# Returns the session time or index for that point.
def find_closest_pos_to_corner(pos_data, corner_x, corner_y):
    pos_data['distance'] = ((pos_data['X'] - corner_x) ** 2 + (pos_data['Y'] - corner_y) ** 2) ** 0.5
    closest_row = pos_data.loc[pos_data['distance'].idxmin()]
    return closest_row['SessionTime'], closest_row.name  # Return session time and index of the closest point

def get_corner_entry_exit(corner_distance, entry_offset: float = 20, exit_offset: float = 10):
    return corner_distance - entry_offset, corner_distance + exit_offset

# build the get_car_data dataframe for a lap
def build_lap_car_data(lap, entry_offset: float = 20, exit_offset: float = 10):
    car_data = lap.get_car_data()
    pos_data = lap.get_pos_data()
    weather_data = lap.get_weather_data()
    
    # Get corner data
    corners = get_circuit_corners(lap.event.circuit.corners)
    
    # Tag position data with corners
    pos_data = tag_position_with_corners(pos_data, corners)
    
    # Get entry and exit points for each corner
    for _, corner in corners.iterrows():
        entry, exit = get_corner_entry_exit(corner['Distance'], entry_offset, exit_offset)
        car_data_slice = slice_car_data_by_distance(car_data, entry, exit)
        telemetry_averages = compute_telemetry_averages(car_data_slice)
        
        # Add telemetry averages to the car data
        car_data.loc[(car_data['Distance'] >= entry) & (car_data['Distance'] <= exit), 'Telemetry'] = telemetry_averages
    
    return car_data