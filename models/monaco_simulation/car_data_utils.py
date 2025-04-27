import pandas as pd



# Brake functions

def slice_car_data_by_distance(car_data, start_distance, end_distance):
    """Return a slice of car data between start_distance and end_distance."""
    # Filter the car data based on the distance
    sliced_data = car_data[car_data['Distance'].between(start_distance, end_distance)].reset_index(drop=True)
    # Check if sliced_data is empty
    if sliced_data.empty:
        raise ValueError(f"No data found between distances {start_distance} and {end_distance}.")
    # return the sliced data
    return sliced_data

def slice_car_data_by_brake(car_data):
    """
    Return a list of tuples (start_distance, end_distance) for contiguous brake zones.
    Groups continuous segments in car_data where Brake == True.
    """
    brake_data = car_data[car_data['Brake'] == True].reset_index()

    if brake_data.empty:
        return []

    # Find breaks in the index to separate zones
    brake_data['group'] = (brake_data['index'].diff() != 1).cumsum()

    brake_zones = []
    for _, group_df in brake_data.groupby('group'):
        start_distance = group_df.iloc[0]['Distance']
        end_distance = group_df.iloc[-1]['Distance']
        brake_zones.append((start_distance, end_distance))

    return brake_zones


def compute_telemetry_averages(car_data_slice):
    return {
        'speed_avg': car_data_slice['Speed'].mean(),
        'rpm_avg': car_data_slice['RPM'].mean(),
        'throttle_avg': car_data_slice['Throttle'].mean(),
        'brake_pct': car_data_slice['Brake'].sum() / len(car_data_slice)
    }
    
    
    
def build_brake_zones(car_data, brake_zone_indices):
    """
    Takes car_data and list of (start_index, end_index) tuples for brake zones.
    Returns a DataFrame of averaged telemetry data per zone.
    """
    zones = []

    # Iterate through each brake zone and compute averages for telemetry data in that zone
    for start, end in brake_zone_indices:
        zone_data = slice_car_data_by_distance(car_data, start, end)
        zone_data
        # Ensure zone_data is not empty
        if zone_data.empty:
            continue
        # Compute averages for telemetry data in the zone
        zones.append({
            'start_session_time': zone_data['SessionTime'].iloc[0],
            'end_session_time': zone_data['SessionTime'].iloc[-1],
            'start_distance': zone_data['Distance'].iloc[0],
            'end_distance': zone_data['Distance'].iloc[-1],
            **compute_telemetry_averages(zone_data)
        })
        
        

    return pd.DataFrame(zones)



# Throttle functions


def slice_car_data_by_throttle(car_data, threshold=80):
    """
    Return a list of tuples (start_distance, end_distance) for contiguous throttle zones.
    Groups continuous segments in car_data where Throttle >= threshold%.
    """
    throttle_data = car_data[car_data['Throttle'] >= threshold].reset_index()

    if throttle_data.empty:
        return []

    # Find breaks in the index to separate zones
    throttle_data['group'] = (throttle_data['index'].diff() != 1).cumsum()

    throttle_zones = []
    for _, group_df in throttle_data.groupby('group'):
        start_distance = group_df.iloc[0]['Distance']
        end_distance = group_df.iloc[-1]['Distance']
        throttle_zones.append((start_distance, end_distance))

    return throttle_zones

def build_throttle_zones(car_data, throttle_zone_indices):
    """
    Takes car_data and list of (start_index, end_index) tuples for throttle zones.
    Returns a DataFrame of averaged telemetry data per zone.
    """
    zones = []

    # Iterate through each throttle zone and compute averages for telemetry data in that zone
    for start, end in throttle_zone_indices:
        zone_data = slice_car_data_by_distance(car_data, start, end)

        # Ensure zone_data is not empty
        if zone_data.empty:
            continue

        # Compute averages for telemetry data in the zone
        zones.append({
            'start_session_time': zone_data['SessionTime'].iloc[0],
            'end_session_time': zone_data['SessionTime'].iloc[-1],
            'start_distance': zone_data['Distance'].iloc[0],
            'end_distance': zone_data['Distance'].iloc[-1],
            **compute_telemetry_averages(zone_data)
        })

    return pd.DataFrame(zones)



def plot_throttle_zones(pos_data, throttle_zones_df):
    """
    Plot the throttle zones using X, Y coordinates from pos_data and throttle zone session times.
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.plot(pos_data['X'], pos_data['Y'], color='gray', alpha=0.5, label='Track Layout')

    for _, zone in throttle_zones_df.iterrows():
        mask = (pos_data['SessionTime'] >= zone['start_session_time']) & (pos_data['SessionTime'] <= zone['end_session_time'])
        plt.scatter(pos_data.loc[mask, 'X'], pos_data.loc[mask, 'Y'], color='green', alpha=0.5, label='Throttle Zone')

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Throttle Zones on Track Layout')
    plt.legend()
    plt.axis('equal')
    plt.grid()
    plt.show()
    

# Corner functions
def get_car_data_around_corner(car_data, pos_data, circuit_info, window=15):
    """
    For each corner in circuit_info, slice car_data ±window meters from the corner distance.
    Returns a list of dicts with entry/exit telemetry and corner metadata.
    """
    segments = []
    for _, corner in circuit_info.iterrows():
        dist = corner['Distance']
        slice_data = car_data[car_data['Distance'].between(dist - window, dist + window)].copy()
        if slice_data.empty:
            continue
        entry_data = slice_data[slice_data['Distance'] < dist]
        exit_data = slice_data[slice_data['Distance'] > dist]
        
        segments.append({
            'corner_number': corner['Number'],
            'corner_name': corner.get('Name', f"Turn {corner['Number']}"),
            'distance': dist,
            'entry_speed_avg': entry_data['Speed'].mean(),
            'exit_speed_avg': exit_data['Speed'].mean(),
            'min_speed': slice_data['Speed'].min(),
            'entry_throttle_avg': entry_data['Throttle'].mean(),
            'exit_throttle_avg': exit_data['Throttle'].mean(),
            'entry_brake_pct': entry_data['Brake'].sum() / len(entry_data) if not entry_data.empty else 0,
            'exit_brake_pct': exit_data['Brake'].sum() / len(exit_data) if not exit_data.empty else 0,
        })
    return pd.DataFrame(segments)
