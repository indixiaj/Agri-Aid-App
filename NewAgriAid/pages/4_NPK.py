import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import os
import requests
import datetime
import numpy as np

st.set_page_config(page_title="NPK Levels", page_icon="⚖️", layout='wide')

# ############################################################
# Open database from csv file
data = pd.read_csv("sensorData.csv")

# #####################################################################

# ########################################################################

# with st.sidebar:
#     st.image('White Full.png',output_format='png')
    
# # Database configuration
# db_config = {
#     'user': 'root',
#     'password': 'agriaid321',
#     'host': '34.147.193.127',
#     'database': 'mydb'
# }
# # Connect to the database
# def db_connection():
#     conn = None
#     try:
#         conn = mysql.connector.connect(**db_config)
#         st.sidebar.success("Successfully connected to the database")
#     except mysql.connector.Error as error:
#         st.sidebar.error(f"Error connecting to MySQL: {error}")
#     return conn

# # Retrieve data from the database and convert it to a pandas DataFrame
# def retrieve_data():
#     conn = db_connection()
#     if conn is not None:
#         cursor = conn.cursor()
#         try:
#             query = "SELECT * FROM soil_measurements"
#             cursor.execute(query)
#             rows = cursor.fetchall()
#             data = pd.DataFrame(rows, columns=['id', 'temperature', 'moisture', 'timestamp'])
#             return data
#         except mysql.connector.Error as error:
#             st.error(f"Failed to retrieve data from MySQL table: {error}")
#             return pd.DataFrame()
#         finally:
#             if cursor is not None:
#                 cursor.close()
#             if conn is not None:
#                 conn.close()
#     else:
#         st.error("Failed to connect to the database")
#         return pd.DataFrame()
    
# # Retrieve data from the database
# data = retrieve_data()
#             #df = pd.DataFrame(data)
#             #print(df.head())

# # Drop the rows with NULL values to avoid errors in the chart
# data = data.dropna()

# # Convert the 'timestamp' column to datetime format for better charting
# data['timestamp'] = pd.to_datetime(data['timestamp'])

# ##########################################################################

#####################################################################

st.markdown("# ⚖️ NPK Values")
st.sidebar.header("⚖️ Getting NPK Values")
with st.sidebar:
    st.image('White Full.png',output_format='png')

st.write(
    """Fill in the start and end date to change the data of the NPK values over time"""
)
####################### TIME SELECTION #######################

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

    # Make 3 tabs for the 3 possible charts of each N, P, K
    tabN, tabP, tabK = st.tabs(["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"])
    
    with tabN:
        # Plot the data in a graph for visualisation
        st.markdown("### Nitrate Levels in the Soil")

        # Current N Level
        val_N = data['N'].iloc[-1]
        st.metric(label="Current N Level", value=f"{val_N:.2f}")
        if val_N < 34.6:
            st.markdown(''':red[⚠️ N is low]''')

        # Temperature of set time plot
        fig_N = px.line(filtereddata, x='timestamp', y='N', 
                            title='N Levels Over Set Time',
                            labels={'N': 'N Level (mg/kg)'})
        
        # Horizontal Average Line
        fig_N.add_hline(y=34.6, line_dash="dash", line_color = "red", annotation_text="Minimum = 34.6")

        fig_N.update_layout(autosize=True)
        st.plotly_chart(fig_N, use_container_width=True)

        with st.expander("View Raw Data of Set Time", expanded=False):
            st.dataframe(data.style.highlight_null('red'), use_container_width=True, hide_index=True)

        with st.expander("⭐ Information about N", expanded=False):
            st.markdown(
                """
                ### Information About Nitrates
                - Ideal values for N for wheat is above 34.6 mg/kg
                - Nitrogen helps stimulate the growth of the overall plant
                - Wheat does not utilise as much Nitrogen compared to Potassium
                - Nitrogen levels are an **indicator of wheat rust** disease as there are correlations with the wheat not uptaking as much nitrogen as needed when ill
                """
            )
    
    with tabP:
        # Plot the data in a graph for visualisation
        st.markdown("### Phosphorus Levels in the Soil")

        # Current N Level
        val_P = data['P'].iloc[-1]
        st.metric(label="Current P Level", value=f"{val_P:.2f}")
        if val_P < 15.6:
            st.markdown(''':red[⚠️ P is low]''')

        # Temperature of set time plot
        fig_P = px.line(filtereddata, x='timestamp', y='P', 
                            title='P Levels Over Set Time',
                            labels={'P': 'P Level (mg/kg)'})
        
        # Horizontal Average Line
        fig_P.add_hline(y=15.6, line_dash="dash", line_color = "red", annotation_text="Minimum = 15.6")

        fig_P.update_layout(autosize=True)
        st.plotly_chart(fig_P, use_container_width=True)

        with st.expander("View Raw Data of Set Time", expanded=False):
            st.dataframe(data.style.highlight_null('red'), use_container_width=True, hide_index=True)

        with st.expander("⭐ Information about P", expanded=False):
            st.markdown(
                """
                ### Information About Phosporus
                - Ideal values for P for wheat is above 15.6 mg/kg
                - Phosporus is a major plant nutrient which is vital for early **root development**
                - P is also important for grain fill
                - Having proper root growth will consequently help plants handle moisture
                """
            )
            

    with tabK:
        # Plot the data in a graph for visualisation
        st.markdown("### Potassium Levels in the Soil")

        # Current N Level
        val_K = data['K'].iloc[-1]
        st.metric(label="Current K Level", value=f"{val_K:.2f}")
        if val_K < 150:
            st.markdown(''':red[⚠️ K is low]''')

        # Temperature of set time plot
        fig_K = px.line(filtereddata, x='timestamp', y='K', 
                            title='K Levels Over Set Time',
                            labels={'K': 'K Level (mg/kg)'})
        
        # Horizontal Average Line
        fig_K.add_hline(y=150, line_dash="dash", line_color = "red", annotation_text="Minimum = 150")

        fig_K.update_layout(autosize=True)
        st.plotly_chart(fig_K, use_container_width=True)

        with st.expander("View Raw Data of Set Time", expanded=False):
            st.dataframe(data.style.highlight_null('red'), use_container_width=True, hide_index=True)
        
        with st.expander("⭐ Information about K", expanded=False):
            st.markdown(
                """
                ### Information About Potassium
                - Ideal values for K for wheat is above 150 mg/kg
                - Potassium is a major plant nutrient espcially for wheat crops as it improves **lodging resistance**
                - Furthermore, K is also used to increase **disease and drought tolerance**
                """
            )

# Reiterate that the data is not in the right range
else:
    st.error('Error: End date must fall on or after start date.')

    st.divider()
    st.write("Set possible date values to see a graph!")

# Additional Information about the data
st.divider()


st.markdown(
    """
    The data is live so it is important to rerun to see if there is new data.\

    Click on the **Rerun Page** button at the bottom of this page to refresh the data.
    
    ### Additional Help on the page
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
