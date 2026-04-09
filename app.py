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
            cred = credentials.Certificate(fb_dict)
        else:
            cred = credentials.Certificate('kunci-firebase.json')
            
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://praktikum-d68ed-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"Gagal koneksi Firebase: {e}")

ref = db.reference('smart_home')

# Tampilan
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; }
    [data-testid="stMetric"] { background-color: #f8f9fa; padding: 15px; border-radius: 15px; }
    .pin-box { border: 2px solid #ff4b4b; padding: 15px; border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("Kelompok 10 Smart Home")
st.write(f"Admin")
st.caption(f"Server Time: {datetime.now().strftime('%H:%M:%S')}")

data = ref.get()
if not data:
    data = {"pintu": 0, "ac_servo": 0, "lampu": False, "suhu": 0, "kelembapan": 0, "last_nfc": "None"}

# -Monitor
st.subheader("Monitoring")
m_col1, m_col2 = st.columns(2)
with m_col1:
    st.metric("Suhu", f"{data.get('suhu', 0)}°C")
    pintu_status = "TERBUKA" if data.get('pintu') == 1 else "TERTUTUP"
    st.metric("Pintu", pintu_status)
with m_col2:
    st.metric("Kelembapan", f"{data.get('kelembapan', 0)}%")
    lampu_status = "NYALA" if data.get('lampu') == True else "🌑 MATI"
    st.metric("Lampu", lampu_status)

st.info(f"👤 **NFC Terakhir:** {data.get('last_nfc', 'Kosong')}")

# control
st.divider()
st.subheader("Kontrol")

# lampu
st.markdown("### Lampu Utama")
col_l1, col_l2 = st.columns(2)
with col_l1:
    if st.button("NYALAKAN"): ref.update({'lampu': True})
with col_l2:
    if st.button("MATIKAN"): ref.update({'lampu': False})

# pintu
st.markdown("---")
st.markdown("Pin Pintu")

MY_PIN = st.secrets["MY_PIN"] if "MY_PIN" in st.secrets else "1234"

pin_input = st.text_input("Masukkan PIN", type="password", help="PIN diperlukan untuk buka/tutup pintu")

if pin_input == MY_PIN:
    st.success("Akses Diterima!")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("BUKA PINTU"): ref.update({'pintu': 1})
    with col_p2:
        if st.button("KUNCI PINTU"): ref.update({'pintu': 0})
elif pin_input == "":
    st.warning("Silakan masukkan PIN untuk membuka tombol kontrol pintu.")
else:
    st.error("PIN SALAH!")

# Ac
st.markdown("---")
st.markdown("AC")
sudut_ac = st.slider("Servo", 0, 90, value=int(data.get('ac_servo', 0)), step=10)
if sudut_ac != data.get('ac_servo'):
    ref.update({'ac_servo': sudut_ac})

# Suhu
st.divider()
st.subheader("Trend Suhu")
history = [data.get('suhu', 0)-1, data.get('suhu', 0)-0.5, data.get('suhu', 0)]
st.line_chart(pd.DataFrame(history, columns=['Temp']))

# untuk rerun
time.sleep(2)
st.rerun()