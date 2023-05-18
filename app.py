import streamlit as st
import pandas as pd
import pymongo
import requests

from pymongo import MongoClient
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu
from PIL import Image

# import datetime for date fields
from datetime import datetime,timedelta
# datetime_now = datetime.now() # pass this to a MongoDB doc

logo_tab = Image.open("picture/favicon.ico")
logo_produk = Image.open("picture/android-chrome-192x192.png")

st.set_page_config(
    page_title='SmartFishSense',
    page_icon=logo_tab,
    layout='centered', #centered or wide
    initial_sidebar_state='expanded',
)
  
st.columns(3)[1].image(logo_produk,use_column_width=True)

st.markdown("<h1 style='text-align: center; color:textColor ;'>Smart Fish Sense</h1>", unsafe_allow_html=True)

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=["Control Menu", "Recent Status"],
    icons=["bi bi-toggles2", "bi bi-hourglass-split"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

# Replace the uri string with your MongoDB deployment's connection string.

uri = "mongodb+srv://agapedsky:dagozilla@cluster0.ro1gcoc.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)
db = client.TA
input_user = db.data1 # data yang diinput dari ui
output_user = db.data2 # data untuk ditampilkan di ui
# input_user.drop()
# output_user.drop()

#Inisialisasi awal
resetx = 0
exitx = 0
statusx = ""
confidencex = ""

def add_data_input():
    timex = datetime.today()
    # timex = timex + timedelta(hours=7) #khusus buat di github
    docs = [
            {"Date": (timex.strftime("%x")),"Time":  (timex.strftime("%X")), "Reset": resetx, "Run": exitx,},
            ]
    return docs

def add_data_output():
    timex = datetime.today()
    # timex = timex + timedelta(hours=7) #khusus buat di github
    docs = [
            {"Date": (timex.strftime("%x")),"Time":  (timex.strftime("%X")), "Status": statusx, "Confidence": confidencex,},
            ]
    return docs

def load_data_input():
    x = input_user.find()
    df = pd.DataFrame(x)
    selected_columns = ['Date','Time','Reset','Run']
    df_selected = df[selected_columns]
    return (df_selected)

def load_data_output():
    x = output_user.find()
    df = pd.DataFrame(x)
    selected_columns = ['Date','Time','Status','Confidence']
    df_selected = df[selected_columns]
    return (df_selected)



# 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
API_KEY = st.secrets["API_KEY"]
API_URL = "https://api-inference.huggingface.co/models/valhalla/distilbart-mnli-12-3"
headers = {"Authorization": f"Bearer {API_KEY}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #4dc7a2;
    color: #03585c;
    height: 3em;
    width: 12em;
    border-radius:100px;
    border:3px solid #379477;
    font-size:20px;
    font-weight: bold;
    margin: auto;
    display: block;
}

div.stButton > button:hover {
	background:linear-gradient(to bottom, #4dc7a2 5%, #379477 100%);
	background-color:#4dc7a2;
}

div.stButton > button:active {
	position:relative;
	top:3px;
}

</style>""", unsafe_allow_html=True)

if selected == "Control Menu":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset"):
            resetx = 1
        else:
            resetx = 0
    with col2:
        if st.button("Run"):
            exitx = 1
        else:
            exitx = 0
    if exitx != 0 or resetx != 0:
        if exitx == 1 and resetx ==1:
            exitx = 0
            resetx = 1
        data_input = add_data_input()
        result_input = input_user.insert_many(data_input)
        
        data_output = add_data_output()
        result_output = output_user.insert_many(data_output)

# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)


if selected == "Recent Status":
    data_status = load_data_output()
    st.table(data_status)

    with st.expander("Data Input"):
        data_inputx = load_data_input()
        st.table(data_inputx)
    
client.close()
