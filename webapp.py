import streamlit as st
import pandas as pd
import pymongo
import requests
import hashlib
import bcrypt

from pymongo import MongoClient
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu
from PIL import Image
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from datetime import datetime,timedelta

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://agapedsky:dagozilla@cluster0.ro1gcoc.mongodb.net/?retryWrites=true&w=majority")
db = client.TA
input_user = db.data1 # data yang diinput dari ui
output_user = db.data2 # data untuk ditampilkan di ui
users_collection = db.users
# input_user.drop()
# output_user.drop()

# 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
API_KEY = st.secrets["API_KEY"]
API_URL = "https://api-inference.huggingface.co/models/valhalla/distilbart-mnli-12-3"
headers = {"Authorization": f"Bearer {API_KEY}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

#Inisialisasi awal
resetx = 0
exitx = 0
statusx = ""
confidencex = ""

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

@st.cache
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

def load_data_input(z):
    x = input_user.find()
    df = pd.DataFrame(x)
    df = df.iloc[::-1].head(z)
    selected_columns = ['Date','Time','Reset','Run']
    df_selected = df[selected_columns]
    return (df_selected)

def load_data_output(z):
    x = output_user.find()
    df = pd.DataFrame(x)
    df = df.iloc[::-1].head(z)
    selected_columns = ['Date','Time','Status','Confidence']
    df_selected = df[selected_columns]
    return (df_selected)

# Encryption functions
def generate_rsa_keys():
    publicKey, privateKey = rsa.newkeys(2048)
    return publicKey, privateKey

def encrypt_rsa(publicKey, message):
    encrypted_message = rsa.encrypt(message.encode(), publicKey)
    return encrypted_message

def decrypt_rsa(privateKey, encrypted_message):
    decrypted_message = rsa.decrypt(encrypted_message, privateKey).decode()
    return decrypted_message

def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed_password

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)

# def login():
#     st.title("Login")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     signup_confirm = st.checkbox("Create a new account?")
#     login_confirm = st.button("Login")
#     if signup_confirm and login_confirm:
#         signup(username, password)
#     elif login_confirm:
#         user = users_collection.find_one({"username": username})
#         if user:
#             stored_password = user["password"]
#             if check_password(password, stored_password):
#                 st.success("Logged in successfully!")
#                 # Simpan username sebagai informasi login
#                 st.session_state["username"] = username
#                 # Tampilkan halaman utama
#                 st.session_state.page = 1
#             else:
#                 st.error("Invalid password!")
#         else:
#             st.error("User does not exist.")
    
def signup(username, password):
    # st.title("Signup")
    # username = st.text_input("Username")
    # password = st.text_input("Password", type="password")
    # if st.button("Signup"):
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        st.error("Username already exists.")
    else:
        hashed_password = hash_password(password)
        user = {"username": username, "password": hashed_password}
        users_collection.insert_one(user)
        st.success("Signup successful!")
        # st.session_state.page = 1
        existing_user = users_collection.find_one({"username": username})
        return

# Fungsi untuk membuat halaman utama
def home_page():
    # Clear the previous content
    # st.header(f"Selamat datang, {st.session_state['username']}!")
    # --- NAVIGATION MENU ---
    selected = option_menu(
        menu_title=None,
        options=["Control Menu", "Recent Status"],
        icons=["bi bi-toggles2", "bi bi-hourglass-split"],  # https://icons.getbootstrap.com/
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        # styles={
        #             "container": {"padding": "0!important", "background-color": "#fafafa"},
        #             "icon": {"color": "orange", "font-size": "25px"},
        #             "nav-link": {
        #                 "font-size": "25px",
        #                 "text-align": "center",
        #                 "margin": "0px",
        #                 "--hover-color": "#eee",
        #             },
        #             "nav-link-selected": {"background-color": "green"},
        #         },
    )

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
        output_index = st.slider('Previous Data', 0, 100,10)
        data_status = load_data_output(output_index)
        st.table(data_status)

# Pages logic 
if 'page' not in st.session_state: st.session_state.page = 0
def nextPage(): st.session_state.page += 1
def firstPage(): st.session_state.page = 0

ph = st.empty()

## Page 0
if st.session_state.page == 0:
    with ph.container():
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        signup_confirm = st.checkbox("Create a new account?")
        login_confirm = st.button("Login")
        if signup_confirm and login_confirm:
            signup(username, password)
            nextPage()
        elif login_confirm:
            user = users_collection.find_one({"username": username})
            if user:
                stored_password = user["password"]
                if check_password(password, stored_password):
                    st.success("Logged in successfully!")
                    # Simpan username sebagai informasi login
                    st.session_state["username"] = username
                    # Tampilkan halaman utama
                    nextPage()
                else:
                    st.error("Invalid password!")
            else:
                st.error("User does not exist.")

## Page 1
if st.session_state.page == 1:
    with ph.container():
        home_page()
        if st.button("Logout",on_click=firstPage):
            # Hapus informasi login dan kembali ke halaman login
            del st.session_state["username"]
            # st.session_state.page = 0

client.close()
