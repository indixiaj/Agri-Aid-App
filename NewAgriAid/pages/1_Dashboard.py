import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import os
import requests

# Layout and styling
st.set_page_config(page_title="AgriAid Dashboard", page_icon="🌿", layout='wide')

# Weather Data API
base_url = f'https://api.open-meteo.com/v1/forecast?latitude=52.3793&longitude=1.5615&hourly=precipitation_probability,precipitation,et0_fao_evapotranspiration&timezone=Europe%2FLondon&past_hours=1&forecast_days=1&forecast_hours=12'
def get_weather_data():
        url = f"{base_url}"
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            data = data['hourly']
            return data
        else:
            return None

weather_data = get_weather_data()
        
# Extract relevant information from the response
time = weather_data['time']
xi = weather_data['precipitation_probability']
p_hat = weather_data['precipitation']
e_hat = weather_data['et0_fao_evapotranspiration']
wdf = pd.DataFrame({'time':time,'precipitation probability':xi, 'precipitation':p_hat, 'evapotranspiration':e_hat})

##########################
# Open database from csv file
NPKdata = pd.read_csv("sensorData.csv")
##########################

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

with st.sidebar:
    st.image('White Full.png',output_format='png')

# Title of the dashboard
st.image('White Full.png',output_format='png')
st.markdown("# Your Dashboard")


st.divider()

st.markdown("## 🌱 Current Soil Conditions")

# Key information
col3, col4 = st.columns(2)

with col3:
    val_temp = data['temperature'].iloc[-1]
    st.metric(label="Temperature", value=f"{val_temp:.2f}°C")
    if val_temp < 15:
        st.markdown(''':red[⚠️ Temp is low]''')

with col4:
    val_moisture = data['moisture'].iloc[-1]
    st.metric(label="Moisture", value=f"{val_moisture:.2f}%")
    if val_moisture <50:
        st.markdown(''':red[⚠️ Moisture is low]''')

st.markdown("### NPK Readings (mg/kg)")

col5, col6, col7  = st. columns(3)

with col5:
    val_N = NPKdata['N'].iloc[-1]
    st.metric(label="N", value=f"{val_N:.2f}")
    if val_N < 34.6:
        st.markdown(''':red[⚠️ N is low]''')
with col6:
    val_P = NPKdata['P'].iloc[-1]
    st.metric(label="P", value=f"{val_P:.2f}")
    if val_P < 15.6:
        st.markdown(''':red[⚠️ P is low]''')
with col7:
    val_K = NPKdata['K'].iloc[-1]
    st.metric(label="K", value=f"{val_K:.2f}")
    if val_P < 150:
        st.markdown(''':red[⚠️ K is low]''')

st.divider()

# Display interactive charts using Plotly
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌦️ Weather Forecast")
    wdf['precipitation'] = wdf['precipitation'].apply(lambda x: '🌧️' if x > 0 else ' ')
    
    st.dataframe(
        wdf,
        use_container_width=True,
        column_config={
            "time": "The next 12 hours",
            "precipitation": "Rain?",
            "evapotranspiration": None,
            "precipitation probability": None,
        },
        hide_index=True,
    )


with col2:
    st.markdown("### 💧 Moisture Over Last 24h")
    fig_moist = px.line(data[-24:], x='timestamp', y='moisture', 
                        title='Moisture Over Time',
                        labels={'moisture': 'Moisture (%)'})
    fig_moist.update_layout(autosize=True)
    st.plotly_chart(fig_moist, use_container_width=True)

# Use an expander to hide raw data by default to keep the dashboard clean
with st.expander("View Today's Raw Data", expanded=False):
    st.dataframe(data[-24:].style.highlight_null('red'), use_container_width=True, hide_index=True)

st.divider()

st.markdown("### Average Statistics")

# Key information
col3, col4 = st.columns(2)

with col3:
    avg_temp = data['temperature'].mean()
    st.metric(label="Average Temperature", value=f"{avg_temp:.2f}°C")
    if avg_temp < 20:
        st.markdown(''':red[⚠️ Average Temp is low]''')

with col4:
    avg_moisture = data['moisture'].mean()
    st.metric(label="Average Moisture", value=f"{avg_moisture:.2f}%")
    if avg_moisture <50:
        st.markdown(''':red[⚠️ Average Moisture is low]''')

colN, colP, colK = st.columns(3)

with colN:
    avg_N = NPKdata['N'].mean()
    st.metric(label="Average N", value=f"{avg_N:.2f}mg/kg")
    if avg_N < 34.6:
        st.markdown(''':red[⚠️ Average N is low]''')
with colP:
    avg_P = NPKdata['P'].mean()
    st.metric(label="Average P", value=f"{avg_P:.2f}mg/kg")
    if avg_P < 15.6:
        st.markdown(''':red[⚠️ Average P is low]''')
with colK:
    avg_K = NPKdata['K'].mean()
    st.metric(label="Average K", value=f"{avg_K:.2f}mg/kg")
    if avg_P < 150:
        st.markdown(''':red[⚠️ Average K is low]''')


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

