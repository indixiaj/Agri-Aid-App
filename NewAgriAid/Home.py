import streamlit as st

st.set_page_config(
    page_title="Home Page",
    page_icon="🧑‍🌾",
    layout='wide'
)

st.image('White Full.png',output_format='png')
st.write("# 🏡 Welcome to Agri-Aid!")

# Quick Links to pages in the webapp
st.write('## Pages in this webapp:')

with st.sidebar:
    st.image('White Full.png',output_format='png')

st.page_link("pages/1_Dashboard.py", label="Your Dashboard", icon="📊")

st.page_link("pages/2_Irrigation.py", label="Irrigation Information", icon="💧")

st.page_link("pages/3_Soil_Temperature.py", label="Soil Temperature Information", icon="🌡️")

st.page_link("pages/4_NPK.py", label="NPK Information", icon="🥬")

st.page_link("pages/5_Settings_and_Help.py", label="Settings and Contact Us", icon="⚙️")

st.divider()

st.markdown(
    """
    We are 5 4th year engineering students looking to make the world a better place.\
    
    Consisting of Evyanne (Software Engineer), Indixia (Mechanical Engineer), Sandesh (EEE), Usman (EEE), and Abzal (EEE),
    we designed a solution to solve a major problem affecting a large population in Ethiopia. 
    The wheat plant has been a source of income and food for years and continues to be. 
    However, the wheat rust disease has been affecting communities reducing yield.

    We designed an IoT Farming System, designed specifically for the wheat plant in Ethiopia in order
    to monitor and control irrigation and nutrients.

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