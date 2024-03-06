# May want to change some of the input parameter values based on what the literature says


# Import Dependencies
import requests
import time
from datetime import datetime
import datetime

# Class input values have defaults set which can be changed by specifing them when the class is called
class IrrigationBasic:
    def __init__(self, max_moisture=100, min_moisture=50, rain_threshold=0.2, et_threshold=0.3, flow_factor=1, tube_constant=5, location=1):
        self.max_moisture = max_moisture
        self.min_moisture = min_moisture
        self.current_moisture = 40  # Initial moisture level (mm)
        self.rain_threshold = rain_threshold  # Rainfall threshold for not irrigating
        self.et_threshold = et_threshold  # ET threshold for not irrigating
        self.flow_factor = flow_factor  # Pump flow factor for irrigation calculation
        self.tube_constant = tube_constant  # Tube constant for irrigation calculation
        self.location = location
        # Weather API values 
        # Location1 - Jeldu District, West Shewa Zone, Oromia National Region,Ethiopia, LatLong = [9.30896538021007,38.021007], soil depth: 28 to 100cm
        self.base_url_l1 = f'https://api.open-meteo.com/v1/forecast?latitude=9.30896538021007&longitude=38.021007&hourly=precipitation,et0_fao_evapotranspiration,soil_moisture_27_to_81cm&timezone=Africa%2FCairo&forecast_days=1'
        # Location2 - Warwick Univeristy Campus, LatLong = [52.37574,-1.5595], soil depth: 0 to 7cm
        self.base_url_l2 = f'https://api.open-meteo.com/v1/forecast?latitude=52.37574&longitude=-1.5595&hourly=precipitation,et0_fao_evapotranspiration,soil_moisture_3_to_9cm&timezone=Europe%2FLondon&forecast_days=1'
        if self.location == 1:
            self.depth_str = '27_to_81cm'
            self.soil_depth = 540 # mm
        elif self.location == 2:
            self.depth_str = '3_to_9cm'
            self.soil_depth = 60 # mm


    def read_moisture_sensor(self):
        # *** Simulated moisture reading, replace with actual sensor reading****
        return self.current_moisture  

    def get_weather_data(self):
        if self.location == 1:
            url = f"{self.base_url_l1}"
        elif self.location == 2:
            url = f"{self.base_url_l2}"
        else:
            return None
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            data = data['hourly']
            return data
        else:
            return None

    def should_irrigate(self):
        weather_data = self.get_weather_data()
        # Extract relevant information from the response
        current_hour = datetime.datetime.now() - datetime.timedelta(hours = 0)
        time_to_find = current_hour.strftime(f'%Y-%m-%dT%H:00')
        index = weather_data["time"].index(time_to_find)
        x_hat = weather_data[f'soil_moisture_{self.depth_str}'][index] # this is the predicted soil moisture from the weather API, not measured soil moisture
        p_hat = weather_data[f'precipitation'][index] # predicted preciptiation
        e_hat = weather_data[f'et0_fao_evapotranspiration'][index] # predicted evapotranspiration

        if weather_data is None:
            return False
        
    
        if p_hat > self.rain_threshold:
            return False
        if e_hat < self.et_threshold:
            return False
        return True

    def irrigate(self):
        irrigation_time = (self.min_moisture - self.read_moisture_sensor()) * self.flow_factor + self.tube_constant
        return irrigation_time

    def control_irrigation(self):
        if self.should_irrigate():
            moisture_level = self.read_moisture_sensor()
            if moisture_level < self.min_moisture:
                return self.irrigate()
            else: 
                return 0
            
        
        self.current_moisture = self.read_moisture_sensor()  # Reset moisture level after irrigation

if __name__ == "__main__":
    irrigation_system = IrrigationBasic()

    try:
        while True:
            print(irrigation_system.control_irrigation())
            time.sleep(10)  # Check moisture level every 10 seconds - change this to more time later
    except KeyboardInterrupt:
        pass