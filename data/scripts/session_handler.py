import fastf1
class SessionFetcher:
    def __init__(self, year, round_number, session_type):
        self.year = year
        self.round_number = round_number
        self.session_type = session_type
        self.session = fastf1.get_session(year, round_number, session_type)
    
    def load(self):
        self.session.load()

    def get_laps(self):
        return self.session.laps

    def get_results(self):
        return self.session.results

    def get_car_data(self, driver):
        return self.session.car_data[driver]
