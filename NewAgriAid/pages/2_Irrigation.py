import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import os
import requests
import datetime
import time

st.set_page_config(page_title="Soil Moisture", page_icon="💧", layout ='wide')

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
            query = "SELECT * FROM control_outputs"
            cursor.execute(query)
            rows = cursor.fetchall()
            data = pd.DataFrame(rows, columns=['id', 'hr', 'output', 'timestamp'])
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

st.markdown("# 💧 Soil Moisture")

st.write('This page shows total volume used within a day and accumulated levels of volume output.')
st.write('Scroll to see more!')

st.sidebar.header("💧 Getting Soil Moisture")
with st.sidebar:
    st.image('White Full.png',output_format='png')

# Irrigation Status
st.write('### Irrigation Status')

if data['output'].iloc[-1] > 0:
    st.image('On.png', width=100)

else:
    st.image('Off.png', width = 100)

st.divider()
# Find accumulated volume and graph it out for the day

st.markdown("## 📅 Daily Accumulated Volume Output")

# Convert timestamp in data to datetime64[ns] format from object (str)
data['timestamp']=pd.to_datetime(data['timestamp'])

# Accumulate the data and create a new column
accumulated_df = data['output'].cumsum()
data.insert(3, "Total Output",accumulated_df)

# Formatting Layout
c = st.container()

d = st.container()

col1, col2, col3 = d.columns((6,8,2))

with col1:
    st.write('Data starts: ' + str(data['timestamp'][0])[:16])

with col3:
    if st.button("Today", type = 'secondary'):
        accum_date = c.date_input('Pick Date', datetime.date.today())
    else:
        accum_date = c.date_input('Pick Date', min_value=datetime.date(2024,3,5), max_value=datetime.date.today())


accum_date = pd.to_datetime(accum_date)

endaccum_date = accum_date + datetime.timedelta(days=1)

dailyData = data.loc[(data['timestamp'] > accum_date) & (data['timestamp'] <= endaccum_date)]


# Total volume of water used at the chosen day

# Accumulated Volume Plot
fig_temp = px.line(dailyData, x='timestamp', y='Total Output', 
                    title='Volume Output Over Set Time',
                    labels={'output': 'Volume (ml)'})

fig_temp.update_layout(autosize=True)

st.plotly_chart(fig_temp, use_container_width=True)

st.write('### Total Output on chosen date (ml)')
st.metric(label=str(accum_date)[:10], value=dailyData['Total Output'][-1:])

with st.expander("View Raw Data For Specific Day", expanded=False):
    st.dataframe(dailyData.style.highlight_null('red'), use_container_width=True, hide_index=True)


st.divider()

###################### TIME WIDTH #################################################

st.markdown('''
        ## ⌛ Volume Output at Specified Time Range
        Fill in the desired start and end date of data to visualise each output value!
''')

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
    if b.button("Today", key = int):
        end_date = a.date_input('End date', today)
    else:
        end_date = a.date_input('End date')

if start_date <= end_date:
    # Convert start and end date to datetime64[ns] to match the df
    end_date = end_date + datetime.timedelta(days=1)

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtereddata = data.loc[(data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)]


    # Plot the data in a graph for visualisation
    st.markdown("### Volume Output Over Time")

    # Volume of set time plot
    fig_temp = px.line(filtereddata, x='timestamp', y='output', 
                        title='Volume Output Over Set Time',
                        labels={'output': 'Volume (ml)'})

    fig_temp.update_layout(autosize=True)

    # Volume of all time plot
    fig_tempall = px.line(data, x='timestamp', y='output', 
                        title='Volume Output Over All Time',
                        labels={'output': 'Volume (ml)'})

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
    """
    )

with st.expander("Information about Our Control System", expanded=False):
    st.markdown(
        """
        **Basic Control**

This irrigation system monitors the weather (precipitation and evapotranspiration) and the current moisture level of plants to calculate the irrigation required.

**MPC Control**

This irrigation system  implements model predictive control to achieve the optimal soil moisture level for crop growth. Model predictive control is a control scheme that uses a system model to predict the future behaviour

of the system over a time “horizon” window and, based on the predicted future states and the

current estimated state of the system, calculate the optimal control inputs to achieve a defined

control objective subject to system constraints..
    """
    )

    st.image('irrigationpic.png',output_format='png')

with st.expander("Additional Information", expanded=False):

    st.markdown(
        """     
        ### About the data
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
