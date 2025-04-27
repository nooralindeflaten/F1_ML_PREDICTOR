import numpy as np
import pandas as pd
import fastf1

def get_corner_entry_exit(corner_distance: float, entry_offset: float = 20, exit_offset: float = 10):
    return corner_distance - entry_offset, corner_distance + exit_offset


