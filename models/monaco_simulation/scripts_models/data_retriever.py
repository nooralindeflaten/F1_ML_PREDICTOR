
import os
import pandas as pd
from fastf1 import get_session
import fastf1
fastf1.Cache.enable_cache('/Users/nooralindeflaten/f1_ML_predictor/data/cache')  # or wherever your cache lives


# Loads the processed telemetry data from a CSV file for a specific driver, session, year, and round name.
def load_processed_csv(driver: str, session: str, year: int, round_name: str):
    path = f"/Users/nooralindeflaten/f1_ML_predictor/data/processed/{driver}_{str(year)}_{round_name}_{session}.csv"
    return pd.read_csv(path)

# Loads the raw telemetry data from a CSV file for a specific driver, session, year, round, and target data type.
def load_raw_csv(driver: str, session: str, year: int, round: int, target_data: str):
    if session == "Q":
        session = "qualifying"
    elif session == "R":
        session = "races"
    elif session == "FP1":
        session = "practice/FP1"
    elif session == "FP2":
        session = "practice/FP2"
    elif session == "FP3":
        session = "practice/FP3"
    elif session == "Sprint":
        session = "sprint"
    path = f"/Users/nooralindeflaten/f1_ML_predictor/data/raw/telemetry/{session}/{str(year)}/{target_data}_{str(year)}_r{round}_.csv"
    data = pd.read_csv(path)
    driver_data = data[data['Driver'] == driver]
    return driver_data

# Get's the session data from fastf1
def get_fastf1_session(session_type: str, year: int, round_number: int):
    session = get_session(year, round_number, session_type)
    session.load()
    return session

# Get's the lap data for a specific driver
def get_driver_laps(session, driver: str):
    laps = session.laps
    driver_laps = laps[laps['Driver'] == driver]
    return driver_laps

# Get's data from the current session circuit
def get_circuit_info(session):
    return session.event.get_circuit_info()

# Prints the possible properties of the circuit library
def print_circuit_properties(circuit_info):
    print("Circuit Properties:")
    for prop in dir(circuit_info):
        if not prop.startswith('_'):
            print(prop)
    print("\n")
    print("Circuit Methods:")
    for method in dir(circuit_info):
        if not method.startswith('_'):
            print(method)
            
# Get's corner properties from circuit
def get_circuit_corners(circuit_info):
    return circuit_info.corners

# Get's telemetry car_data from a single lap
def get_lap_car_data(lap):
    car_data = lap.get_car_data()
    return car_data

# Get's telemetry pos_data from a single lap
def get_lap_pos_data(lap):
    pos_data = lap.get_pos_data()
    return pos_data

# Get's telemetry weather data from a single lap
def get_lap_weather_data(lap):
    weather_data = lap.get_weather_data()
    return weather_data


# Get's telemetry driver data from a single lap
def get_lap_driver_data(lap):
    driver_data = lap.get_telemetry()
    return driver_data

# Get car data from all driver laps
def get_all_laps_car_data(driver_laps):
    return driver_laps.get_car_data()

# Get pos data from all driver laps
def get_all_laps_pos_data(driver_laps):
    return driver_laps.get_pos_data()

# Get weather data from all driver laps
def get_all_laps_weather_data(driver_laps):
    return driver_laps.get_weather_data()

# Get telemetry for all driver laps
def get_all_laps_driver_data(driver_laps):
    return driver_laps.get_telemetry()

# Get car data with distance from a single lap
def get_car_data_with_distance(lap):
    car_data = lap.get_car_data().add_distance()
    return car_data


