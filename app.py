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
  
col1, col2, col3 = st.columns(3)
with col1:
    st.write("")
with col2:
    st.image(logo_produk,use_column_width=True)
with col3:
    st.write("")

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
coll = db.data1
# coll.drop()

#Inisialisasi awal
resetx = 0
exitx = 0
statusx = ""
confidencex = ""

def add_data():
    # client = MongoClient(uri)
    # db = client.TA
    # coll = db.data1
    # # coll.drop()

    timex = datetime.today()
    timex = timex + timedelta(hours=7) #khusus buat di github
    docs = [
            {"Date": (timex.strftime("%x")),"Time":  (timex.strftime("%X")), "Reset": resetx, "Exit_idle": exitx, "Status": statusx, "Confidence": confidencex,},
            ]
    return docs

def load_data():
    # client = MongoClient(uri)
    # db = client.TA
    # coll = db.data1
    # # coll.drop()
    x = coll.find()
    df = pd.DataFrame(x)
    selected_columns = ['Date','Time','Status','Confidence']
    df_selected = df[selected_columns]
    return df_selected

# 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
API_KEY = st.secrets["API_KEY"]
API_URL = "https://api-inference.huggingface.co/models/valhalla/distilbart-mnli-12-3"
headers = {"Authorization": f"Bearer {API_KEY}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

# output = query({
#     "inputs": "Hi, I recently bought a device from your company but it is not working as advertised and I would like to get reimbursed!",
#     "parameters": {"candidate_labels": ["refund", "legal", "faq"]},
# })

m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #4dc7a2;
    border-radius: 50%;
    height: 4em;
    width: 4em;
}
</style>""", unsafe_allow_html=True)

if selected == "Control Menu":
    col1, col2 = st.columns(2)
    with col1:
        if st.columns([4,1,4])[1].button("Reset"):
            resetx = 1
        else:
            resetx = 0
    with col2:
        if st.columns([4,1,4])[1].button("Run"):
            exitx = 1
        else:
            exitx = 0
    if exitx != 0 or resetx != 0:
        if exitx == 1 and resetx ==1:
            exitx = 0
            resetx = 1
        data_input = add_data()
        result = coll.insert_many(data_input)

if selected == "Recent Status":
    data_status = load_data()
    st.table(data_status)
    
client.close()
