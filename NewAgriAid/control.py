
# May want to change some of the input parameter values based on what the literature says

# Units! Check that seconds are in ms and and water volumes are in ml (so mm^3)
# Import Dependencies
import requests
import time
from datetime import datetime
import datetime
import matplotlib.pyplot as plt
from matplotlib import rcParams
from casadi import *
import pandas as pd
# Import do_mpc package:
import do_mpc
# Animation Packages
import matplotlib.animation as animation 
from matplotlib.animation import FuncAnimation, ImageMagickWriter, FFMpegWriter
import io
import base64

# Class input values have defaults set which can be changed by specifing them when the class is called
class IrrigationBasic:
    '''
    This class implements an open loop controller.
    It contains the following functions: 
    - __init__
    - read_moisture_sensor
    - get_weather_data
    - should_irrigate
    - irrigate
    - control_irrigation
    - save_output_to_dataframe
    The class is initialised with the following parameters:
    - max_moisture
    - min_moisture
    - rain_threshold
    - et_threshold
    - flow_factor
    - tube_constant
    - location
    
    '''
    def __init__(self, max_moisture=60, min_moisture=30, rain_threshold=0.2, et_threshold=0.3, flow_factor=0.39, tube_constant=12.5, location=2):
        self.max_moisture = max_moisture
        self.min_moisture = min_moisture
        self.current_moisture = 20  # Initial moisture level (mm)
        self.rain_threshold = rain_threshold  # Rainfall threshold for not irrigating
        self.et_threshold = et_threshold  # ET threshold for not irrigating
        self.flow_factor = flow_factor  # Pump flow factor for irrigation calculation
        self.tube_constant = tube_constant  # Tube constant for irrigation calculation
        self.location = location # for practical tests we use the Warwick Univeristy Campus location
        self.df = pd.DataFrame(columns=['Datetime', 'Output'])
        # Weather API values 
        # Location1 - Jeldu District, West Shewa Zone, Oromia National Region,Ethiopia, LatLong = [9.30896538021007,38.021007], soil depth: 28 to 100cm
        self.base_url_l1 = f'https://api.open-meteo.com/v1/forecast?latitude=9.30896538021007&longitude=38.021007&hourly=precipitation,et0_fao_evapotranspiration,soil_moisture_27_to_81cm&timezone=Africa%2FCairo&forecast_days=1'
        # Location2 - Warwick Univeristy Campus, LatLong = [52.37574,-1.5595], soil depth: 0 to 7cm
        self.base_url_l2 = f'https://api.open-meteo.com/v1/forecast?latitude=52.37574&longitude=-1.5595&hourly=precipitation,et0_fao_evapotranspiration,soil_moisture_3_to_9cm&timezone=Europe%2FLondon&forecast_days=1'
        if self.location == 1:
            self.depth_str = '27_to_81cm'
            self.soil_depth = 540 # 540 mm
        elif self.location == 2:
            self.depth_str = '3_to_9cm'
            self.soil_depth = 60 # 60 mm


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
            return 0
    
        if p_hat > self.rain_threshold:
            return 0
        if e_hat < self.et_threshold:
            return 0
        return True

    def irrigate(self):
        irrigation_time = (self.min_moisture - self.read_moisture_sensor())* self.soil_depth * self.flow_factor + self.tube_constant
        return irrigation_time

    def control_irrigation(self):
        if self.should_irrigate():
            moisture_level = self.read_moisture_sensor()
            if moisture_level < self.min_moisture:
                # Get time_output (and prevent NoneType Errors)
                time_output = self.irrigate()
                if time_output == None:
                    time_output = 0
                else:
                    time_output = self.irrigate()
                # Calculate volume_output
                volume_output = time_output/self.flow_factor
                return volume_output, time_output, None
            else: 
                return 0 , 0, 0  
        else: 
            return 0 , 0, 0 
        
    # Define a function to reset the dataframe at the start of each day
    def reset_dataframe(self):
        self.df.drop(self.df.index,inplace=True) 

    # Define the function to save the irrigation output to a dataframe for plotting 
    def add_to_dataframe(self):
        # Get the current datetime
        current_datetime = datetime.datetime.now()
            
        # Check if it's a new day, if yes, reset the dataframe
        if current_datetime.hour == 0 and current_datetime.minute == 0:
            self.reset_dataframe()
            return self.df

        # Access the volume_output
        volume_output, time_ouptut, fig = self.control_irrigation()

        # Check if the new value exists in the 'Name' column
        if current_datetime.minute not in self.df['Datetime'].values:
            # Append the current datetime and the output of the function to the dataframe
            #self.df = self.df.append({'Datetime': current_datetime.hour, 'Output': volume_output}, ignore_index=True)
            new_row = {'Datetime': current_datetime.minute, 'Output': volume_output}
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)

        # Return the function to add data to the dataframe
        return self.df
        
########################################################################################################################################################
        
class IrrigationRMPC:
    '''
    This class implements a RMPC controller. 

    It contains the following functions: 
    - __init__
    - read_moisture_sensor
    - get_weather_data
    - control_irrigation
    - save_output_to_dataframe
    The class is initialised with the following parameters:
    - max_moisture
    - min_moisture
    - rain_threshold
    - et_threshold
    - flow_factor
    - tube_constant
    - location
    - horizon
    - max_duration
    - trajectory
    - current_moisture
    '''
    def __init__(self, max_moisture=100, min_moisture=50, max_irrigation = 0.2, min_irrigation = 0, flow_factor=0.39, tube_constant=12.5, location=2, horizon=10, max_duration=10, trajectory= 1, current_moisture = 40):
        self.max_moisture = max_moisture
        self.min_moisture = min_moisture
        self.max_irrigation = max_irrigation
        self.min_irrigation = min_irrigation
        self.flow_factor = flow_factor
        self.tube_constant = tube_constant
        self.location = location
        self.trajectory = trajectory
        self.horizon = horizon
        self.max_duration = max_duration
        self.current_moisture = current_moisture
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
        
        # Dictionary of mpc variables
        self.setup_mpc = {
            'n_horizon': horizon,
            't_step': 0.02,
            'n_robust': 1,
            'store_full_solution': True,
        }

    def read_moisture_sensor(self):
        # *** Simulated moisture reading, replace with actual sensor reading****
        return self.current_moisture 


    def control_irrigation(self, num_steps=60):
        # Create the model
        model_type = 'continuous' 
        # Define the model instance
        model = do_mpc.model.Model(model_type)

        # Define model variables
        x = model.set_variable(var_type='_x', var_name='x', shape=(1,1))
        # Define the model control inputs
        u = model.set_variable(var_type='_u', var_name='u', shape=(1,1))
        # Define the external disturbances (preciptation and evapotranspiration) 
        # as time varying parameters
        p = model.set_variable(var_type='_tvp', var_name='p') 
        e = model.set_variable(var_type='_tvp', var_name='e') 

        # Soil Depth
        soil_depth = self.soil_depth

        # Define the system dynamics
        c = 0.8
        model.set_rhs('x', (1 - c)* x + u + p - e)

        # Define the stage and terminal cost of the control problem
        # This is used to directly plot the trajectory of the cost of each state
        # The espression is the sum of squared errors between the soil moisture and the refernce soil mositure ``trajectory`` from the support files class 
        trajectory  = self.trajectory_generator() # percentage soil moisture from the support file class
        model.set_expression('cost', sum1((trajectory - x)**2))

        # Set up the model
        model.setup()

        # Generate an instance of the do_mpc mpc class defined above
        mpc = do_mpc.controller.MPC(model)
        # set the prediction horizon `n_horizon`, robust horizon `n_robust` 
        # and time step `t_step`
        # use orthogonal collocation as the discretisation scheme
        setup_mpc = {
            'n_robust': 1,
            'n_horizon': 5,
            't_step': 0.02,
            'state_discretization': 'collocation',
            'collocation_type': 'radau',
            'collocation_deg': 1,
            'collocation_ni': 1,
            'store_full_solution': True,
        }

        mpc.set_param(**setup_mpc)

        mterm = model.aux['cost']
        lterm = model.aux['cost']

        mpc.set_objective(mterm=mterm,lterm=lterm)

        mpc.set_rterm(u=1e-4)

        # Define the MPC Constraints 
        # This are soil moisture percentage values

        # lower bounds of the input
        mpc.bounds['lower','_u','u'] = self.min_irrigation

        # upper bounds of the input
        mpc.bounds['upper','_u','u'] = self.max_irrigation

        tvp_template = mpc.get_tvp_template()

        def tvp_fun_control(t_now):
            for k in range(setup_mpc['n_horizon']+1):
                weather_data = self.get_weather_data()
                tvp_template['_tvp', k , 'p'] = weather_data['precipitation'][-1]
                tvp_template['_tvp',k,'e'] = weather_data['et0_fao_evapotranspiration'][-1]
            return tvp_template

        mpc.set_tvp_fun(tvp_fun_control)
        # Finish the MPC setup
        mpc.setup()

        # Define the estimator
        # The state feedback estimator assusmes that all states can be directly measured
        estimator = do_mpc.estimator.StateFeedback(model)

        # Define the simulator
        # This is an instance do-mpc simulator based on the defined model
        simulator = do_mpc.simulator.Simulator(model)

        simulator.set_param(t_step = 0.02)

        # Define the numerical realisations of the uncertain time-varying parameters in tvp_num

        # Get the structure of the time-varying parameters
        tvp_num = simulator.get_tvp_template()

        # Define function for time-varying parameters
        # Called in each simulation step, and returns the current 
        # realisations of the parameters, with respect to the defined input t_now
        def tvp_fun_simulator(t_now):
            return tvp_num
        
        simulator.set_tvp_fun(tvp_fun_simulator)

        simulator.setup()

        # Seed
        np.random.seed(99)

        # Initial state
        e = np.ones([1,1])
        x0 = np.random.uniform(0.1*e,0.30*e) # Values between 0.30 and 0.55 for all states - check that this a reasonable
        mpc.x0 = x0
        simulator.x0 = x0
        estimator.x0 = x0

        # Use initial state to set the initial guess.
        mpc.set_initial_guess()

        for k in range(num_steps):
            u0 = mpc.make_step(x0)
            y_next = simulator.make_step(u0)
            x0 = estimator.make_step(y_next)

        # Access the calculated outputs (in percentage moisture) from the controller at each timestep (each minute in the hour)
        percentage_outputs = [value[0] for value in mpc.data['_u']]
        # Replace None values in percentage_outputs
        percentage_outputs = [0 if percentage_output is None else percentage_output for percentage_output in percentage_outputs]
        # Calculate volume_outputs
        volume_outputs = [(percentage_output * self.soil_depth) for percentage_output in percentage_outputs]
        # Calculate time_outputs
        time_outputs = [(time_output * self.flow_factor /1000) for time_output in volume_outputs]
        # Calculate cumulative sums of the outputs for the plots
        sum_time_outputs = [sum(time_outputs[:i+1]) for i in range(len(time_outputs))]
        sum_volume_outputs = [sum(volume_outputs[:i+1]) for i in range(len(volume_outputs))]

        #Plot results#####################
        rcParams['axes.grid'] = True
        rcParams['font.size'] = 18
        fig, ax, graphics = do_mpc.graphics.default_plot(mpc.data, figsize=(16,9))
        graphics.plot_results()
        graphics.reset_axes()
        
         # Reset moisture level after irrigation
        self.current_moisture = self.read_moisture_sensor() 

        return sum_volume_outputs[-1], sum_time_outputs[-1], fig
    
    # Define a function to reset the dataframe at the start of each day
    def reset_dataframe(self):
        self.df.drop(self.df.index,inplace=True) 

    # Define the function to save the irrigation output to a dataframe for plotting 
    def add_to_dataframe(self):
        # Get the current datetime
        current_datetime = datetime.datetime.now()
            
        # Check if it's a new day, if yes, reset the dataframe
        if current_datetime.minute == 0 and current_datetime.minute == 0:
            self.reset_dataframe()
            return self.df

        # Access the volume_output
        volume_output, time_ouptut, fig = self.control_irrigation()

        # Check if the new value exists in the 'Name' column
        if current_datetime.minute not in self.df['Datetime'].values:
            # Append the current datetime and the output of the function to the dataframe
            self.df = self.df.append({'Datetime': current_datetime.minute, 'Output': volume_output}, ignore_index=True)

        # Return the function to add data to the dataframe
        return self.df

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
    
    def trajectory_generator(self):
        '''This function creates the trajectory for the soil water level to match'''
        # Define trajectories
        # These are different soil moisture perentages for differnet crop growth stages 
        if self.trajectory==1:
            x = 0.42 
        elif self.trajectory==2: 
            x = 0.45 
        elif self.trajectory==3:
            x = 0.48
        else:
            print("For trajectories, only choose 1, 2, or 3 as an integer value")
            exit()
        return x
    

########################################################################################################################################################
# This is for debugging, uncomment to use
if __name__ == "__main__":
    irrigation_system = IrrigationBasic()

    try:
        while True:
            # volume_output, time_output, fig = irrigation_system.control_irrigation()
            # print(volume_output)
            df = irrigation_system.add_to_dataframe()
            print(df)

            csv_data = df.to_csv('outputIrrigation.csv', index = False)
            time.sleep(30)  # Check moisture level every 10 seconds - change this to more time later
    except KeyboardInterrupt:
        pass
