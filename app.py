import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import time
from datetime import datetime

st.set_page_config(
    page_title="Kelompok 10 Smart Home",
    layout="centered"
)

# FIREBASE
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_dict)
        else:
            cred = credentials.Certificate('kunci-firebase.json')
            
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://praktikum-d68ed-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"Gagal koneksi Firebase: {e}")

ref = db.reference('smart_home')

# Tampilan CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; }
    [data-testid="stMetric"] { 
        background-color: #f0f2f6; 
        padding: 15px; 
        border-radius: 15px; 
        border: 1px solid #d1d1d1;
    }
    [data-testid="stMetricValue"] { color: #1f1f1f !important; }
    [data-testid="stMetricLabel"] { color: #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("Kelompok 10 Smart Home")
st.write(f"Admin")

data = ref.get()
if not data:
    data = {"pintu": 0, "ac_servo": 0, "lampu": False, "suhu": 0, "kelembapan": 0, "last_nfc": "None"}

# Monitoring
st.subheader("Monitoring")
m_col1, m_col2 = st.columns(2)
with m_col1:
    st.metric("Suhu", f"{data.get('suhu', 0)}°C")
    pintu_status = "TERBUKA" if data.get('pintu') == 1 else "TERTUTUP"
    st.metric("Pintu Utama", pintu_status)
with m_col2:
    st.metric("Kelembapan", f"{data.get('kelembapan', 0)}%")
    lampu_status = "NYALA" if data.get('lampu') == True else "MATI"
    st.metric("Lampu", lampu_status)

st.info(f"Last NFC: {data.get('last_nfc', 'Kosong')}")

# Kontrol
st.divider()
st.subheader("Kontrol Perangkat")

# lampu
st.markdown("Lampu")
col_l1, col_l2 = st.columns(2)
with col_l1:
    if st.button("NYALAKAN LAMPU"): ref.update({'lampu': True})
with col_l2:
    if st.button("MATIKAN LAMPU"): ref.update({'lampu': False})

# Ac
st.markdown("---")
st.markdown("Ventilasi AC")
col_a1, col_a2 = st.columns(2)
with col_a1:
    if st.button("BUKA VENTILASI"): ref.update({'ac_servo': 90})
with col_a2:
    if st.button("TUTUP VENTILASI"): ref.update({'ac_servo': 0})
st.caption(f"Posisi Servo Saat Ini: {data.get('ac_servo', 0)}°")

# pintu
st.markdown("---")
st.markdown("Keamanan Pintu")
MY_PIN = st.secrets["MY_PIN"] if "MY_PIN" in st.secrets else "1234"
pin_input = st.text_input("Masukkan PIN", type="password")

if pin_input == MY_PIN:
    st.success("Akses Diterima!")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("BUKA PINTU"): ref.update({'pintu': 1})
    with col_p2:
        if st.button("KUNCI PINTU"): ref.update({'pintu': 0})
elif pin_input != "":
    st.error("PIN SALAH!")

st.divider()
st.subheader("Grafik Suhu")
# Dummy history
history = [data.get('suhu', 0)-1, data.get('suhu', 0)-0.5, data.get('suhu', 0)]
st.line_chart(pd.DataFrame(history, columns=['Temp']))

# Auto rerun
time.sleep(2)
st.rerun()