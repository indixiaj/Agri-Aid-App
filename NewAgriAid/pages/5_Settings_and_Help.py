import streamlit as st
import datetime

# Layout and styling
st.set_page_config(page_title='Settings and Help', page_icon='⚙️', layout='wide')

# Title of the dashboard
st.image('White Full.png',output_format='png')

with st.sidebar:
    st.image('White Full.png',output_format='png')

# Settings Section #############################
st.markdown("# ⚙️ Settings")

with st.expander("Edit Information", expanded=False):
    st.write('After changing, press enter to apply')

    # Username
    username = st.text_input('Username', 'Your Username')

    # Farm Name
    farmname = st.text_input('FarmName', 'Your Farm Name')

    # Join Date
    joindate = st.date_input("When did you join?", datetime.date(2024, 1, 1))

    # View Settings
    theme = st.selectbox(
    'Which theme would you like?',
    ('Dark', 'Light', 'Agri-Aid'))

st.markdown('''
        ### Username
''')
st.write(username)

st.markdown('''
        ### Farm Name
''')
st.write(farmname)

st.markdown('''
        ### Join Date
''')
st.write(joindate)

st.markdown('''
        ### Theme
''')
st.write(theme)

st.divider()

# Help Section #################################
st.markdown("# 📧 Contact Us With Your Questions!")
# form made using the opensource form submit service
# source: https://formsubmit.co/
# if implemented commercially this would need to be encrypted

contact_form = """
<form action="https://formsubmit.co/21571ed0b651327d66c82ae64e55d9e5" method="POST">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email" required>
     <textarea name= "message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
"""

st.markdown(contact_form, unsafe_allow_html=True)

# Use Local CSS File
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)

local_css("style.css")
