# models/monaco_simulation/weather_rules.py
def is_crossover_to_inters(track_temp, rain_intensity):
    return track_temp < 30 and rain_intensity > 0.5

def should_stay_out_on_softs(rain_intensity):
    return rain_intensity < 0.3