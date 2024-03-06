import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import os
import requests
import datetime
import numpy as np

st.set_page_config(page_title="Soil Temperature", page_icon="🌡️", layout='wide')

    
############################################################
# # Open database from csv file
# data = pd.read_csv("sensorData.csv")

#####################################################################
    
########################################################################
    
# Database configuration
db_config = {
    'user': 'root',
    'password': 'agriaid321',
    'host': '34.147.193.127',
    'database': 'mydb'
}
# Connect to the database
def db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        st.sidebar.success("Successfully connected to the database")
    except mysql.connector.Error as error:
        st.sidebar.error(f"Error connecting to MySQL: {error}")
    return conn

# Retrieve data from the database and convert it to a pandas DataFrame
def retrieve_data():
    conn = db_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM soil_measurements"
            cursor.execute(query)
            rows = cursor.fetchall()
            data = pd.DataFrame(rows, columns=['id', 'temperature', 'moisture', 'timestamp'])
            return data
        except mysql.connector.Error as error:
            st.error(f"Failed to retrieve data from MySQL table: {error}")
            return pd.DataFrame()
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
    else:
        st.error("Failed to connect to the database")
        return pd.DataFrame()
    
# Retrieve data from the database
data = retrieve_data()
            #df = pd.DataFrame(data)
            #print(df.head())

# Drop the rows with NULL values to avoid errors in the chart
data = data.dropna()

# Convert the 'timestamp' column to datetime format for better charting
data['timestamp'] = pd.to_datetime(data['timestamp'])

##########################################################################

st.markdown("# 🌡️ Soil Temperature")
st.sidebar.header("🌡️ Getting Soil Temperature")
with st.sidebar:
    st.image('White Full.png',output_format='png')
st.write(
    """Fill in the start and end date to change the data of the temperature over time"""
)
##############################################

# Convert timestamp in data to datetime64[ns] format from object (str)
data['timestamp']=pd.to_datetime(data['timestamp'])

# Start and end date:
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input('Start date', yesterday)
    st.write('Data starts: ' + str(data['timestamp'][0])[:16])

with col2:
    a = st.container()
    b = st.container()
    if b.button("Today"):
        end_date = a.date_input('End date', today)
    else:
        end_date = a.date_input('End date', max_value=datetime.date.today())

if start_date <= end_date:

    end_date = end_date + datetime.timedelta(days=1)

    # Convert start and end date to datetime64[ns] to match the df
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtereddata = data.loc[(data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)]

    st.divider()

    # Plot the data in a graph for visualisation
    st.markdown("### Temperature Over Time")

    # Temperature of set time plot
    fig_temp = px.line(filtereddata, x='timestamp', y='temperature', 
                        title='Temperature Over Set Time',
                        labels={'temperature': 'Temperature (°C)'})
    
    # Horizontal Average Line
    fig_temp.add_hline(y=25, line_dash="dash", line_color = "red", annotation_text="Ideal = 25°C")

    fig_temp.update_layout(autosize=True)

    # Temperature of all time plot
    fig_tempall = px.line(data, x='timestamp', y='temperature', 
                        title='Temperature Over All Time',
                        labels={'temperature': 'Temperature (°C)'})
    
    # Horizontal Average Line
    fig_tempall.add_hline(y=25, line_dash="dash", line_color = "red", annotation_text="Ideal = 25°C")

    fig_tempall.update_layout(autosize=True)

    # Make 2 tabs for 2 possible charts
    tab1, tab2 = st.tabs(["Time Width", "All Time"])
    
    with tab1:
        st.plotly_chart(fig_temp, use_container_width=True)
        with st.expander("View Raw Data of Set Time", expanded=False):
            st.dataframe(filtereddata.style.highlight_null('red'), use_container_width=True, hide_index=True)
    
    with tab2:
        st.plotly_chart(fig_tempall, use_container_width=True)
        with st.expander("View Raw Data of All Time", expanded=False):
            st.dataframe(data.style.highlight_null('red'), use_container_width=True, hide_index=True)

# Reiterate that the data is not in the right range
else:
    st.error('Error: End date must fall on or after start date.')

    st.divider()
    st.write("Set possible date values to see a graph!")

# Additional Information about the data
st.divider()

st.markdown("### Information")

st.markdown(
    """
    The data is live so it is important to rerun to see if there is new data.\

    Click on the **Rerun Page** button at the bottom of this page to refresh the data.
    
    ### About the data
    - Ideal soil temperature is between 12 and 25°C.
    - The data shown is from the senors and the start of reading can be read under the 'start date' box.
    - The table will refresh automatically when dates are entered.
    - Please view the raw data in order to see exactly what times are being shown.
    - Plots and raw data are **downloadable** by hovering over them and clicking a button on the top right corner.
    - If the 'today' button is pressed and you want to pick a different date,
    click the calendar input twice as it may not register.
"""
)



# Footer
st.markdown("---")

col1, inter_cols_pace, col2 = st.columns((2, 10, 2))
with col1:
    st.page_link("pages/5_Settings_and_Help.py", label="Settings and Contact Us", icon="⚙️")
    
with col2:
    if st.button("Rerun Page", type="primary"):
        st.rerun()

col1, inter_cols_pace, col2 = st.columns((2, 3, 2))

with col2:
    st.markdown("AgriAid Dashboard | A Streamlit App")

