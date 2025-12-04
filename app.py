import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import requests
from io import BytesIO

# ==========================
# LOAD DATA
# ==========================
@st.cache_data
def load_data():
    df = pd.read_csv("nutrition.csv")

    df.rename(columns={
        "proteins": "protein",
        "carbohydrate": "carbs"
    }, inplace=True)

    numeric_cols = ['calories', 'fat', 'protein', 'carbs']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=numeric_cols)

    return df, numeric_cols

df, numeric_cols = load_data()

# ==========================
# FUNGSI TAMPIL GAMBAR SERAGAM
# ==========================
def show_food_image_from_url(image_url, size=(250, 250)):
    try:
        if pd.notna(image_url) and str(image_url).startswith("http"):
            response = requests.get(image_url, timeout=10)
            img = Image.open(BytesIO(response.content))
            img = img.resize(size)
            st.image(img)
        else:
            st.warning("❌ Gambar tidak tersedia")
    except:
        st.error("⚠️ Gagal memuat gambar")

# ==========================
# TARGET NUTRISI HARIAN
# ==========================
TARGET_KALORI = 2000
TARGET_PROTEIN = 75
TARGET_LEMAK = 65
TARGET_KARBO = 300

# ==========================
# STATUS NUTRISI
# ==========================
def status_nutrisi(total, target):
    if total < target * 0.8:
        return "❗ Kurang"
    elif total <= target * 1.2:
        return "✅ Cukup"
    else:
        return "⚠️ Berlebih"

# ==========================
# SIDEBAR
# ==========================
st.sidebar.title("⚙️ Mode Sistem")
mode = st.sidebar.radio(
    "Pilih Mode:",
    ["🔍 Rekomendasi dari Nutrisi", "🍽️ Nutrisi Harian (3x Makan)"]
)

# ==========================
# MODE 1: REKOMENDASI
# ==========================
if mode == "🔍 Rekomendasi dari Nutrisi":

    st.title("🍽️ Sistem Rekomendasi Makanan Berbasis CBR")

    cal_input = st.number_input("Target Kalori (kkal)", min_value=0, value=500)
    fat_input = st.number_input("Batas Lemak (g)", min_value=0, value=10)
    protein_input = st.number_input("Minimal Protein (g)", min_value=0, value=20)
    carb_input = st.number_input("Minimal Karbohidrat (g)", min_value=0, value=50)

    if st.button("Cari Rekomendasi"):
        user_case = np.array([cal_input, fat_input, protein_input, carb_input])

        def euclidean_distance(case1, case2):
            return np.sqrt(np.sum((case1 - case2) ** 2))

        df['distance'] = df.apply(lambda row:
            euclidean_distance(
                user_case,
                np.array([row['calories'], row['fat'], row['protein'], row['carbs']])
            ),
            axis=1
        )

        result = df.sort_values(by='distance').head(5)

        st.subheader("🔍 Rekomendasi Makanan")
        st.dataframe(result[['name', 'calories', 'fat', 'protein', 'carbs', 'distance']])

        rekomendasi_terbaik = result.iloc[0]

        st.success(f"🎯 Rekomendasi terbaik: **{rekomendasi_terbaik['name']}**")
        show_food_image_from_url(rekomendasi_terbaik['image'])

# ==========================
# MODE 2: NUTRISI HARIAN 3x MAKAN
# ==========================
else:

    st.title("🍽️ Perhitungan Nutrisi Harian (3x Makan)")

    food_list = df['name'].tolist()

    pagi = st.selectbox("Sarapan", food_list)
    siang = st.selectbox("Makan Siang", food_list)
    malam = st.selectbox("Makan Malam", food_list)

    if st.button("Hitung Nutrisi Harian"):

        m1 = df[df['name'] == pagi].iloc[0]
        m2 = df[df['name'] == siang].iloc[0]
        m3 = df[df['name'] == malam].iloc[0]

        total_kalori = m1['calories'] + m2['calories'] + m3['calories']
        total_lemak = m1['fat'] + m2['fat'] + m3['fat']
        total_protein = m1['protein'] + m2['protein'] + m3['protein']
        total_karbo = m1['carbs'] + m2['carbs'] + m3['carbs']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Sarapan")
            show_food_image_from_url(m1['image'])
            st.write(m1[['calories', 'fat', 'protein', 'carbs']])

        with col2:
            st.subheader("Makan Siang")
            show_food_image_from_url(m2['image'])
            st.write(m2[['calories', 'fat', 'protein', 'carbs']])

        with col3:
            st.subheader("Makan Malam")
            show_food_image_from_url(m3['image'])
            st.write(m3[['calories', 'fat', 'protein', 'carbs']])

        st.subheader("✅ TOTAL NUTRISI HARIAN")

        st.success(f"""
🔥 Kalori: {total_kalori:.2f} kkal → {status_nutrisi(total_kalori, TARGET_KALORI)}  
🥑 Lemak: {total_lemak:.2f} g → {status_nutrisi(total_lemak, TARGET_LEMAK)}  
💪 Protein: {total_protein:.2f} g → {status_nutrisi(total_protein, TARGET_PROTEIN)}  
🍞 Karbohidrat: {total_karbo:.2f} g → {status_nutrisi(total_karbo, TARGET_KARBO)}
        """)

    else:
        st.info("Silakan pilih menu Sarapan, Siang, dan Malam terlebih dahulu.")
