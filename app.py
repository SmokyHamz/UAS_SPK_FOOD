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
# FUNGSI AMAN TAMPIL GAMBAR SERAGAM 250x250
# ==========================
def show_food_image_from_url(image_url, size=(250, 250)):
    try:
        if pd.notna(image_url) and str(image_url).startswith("http"):
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            img = img.resize(size)  # resize gambar agar seragam
            st.image(img)
        else:
            st.warning("❌ Gambar tidak tersedia")
    except:
        st.error("⚠️ Gagal memuat gambar")


# ==========================
# SIDEBAR
# ==========================
st.sidebar.title("⚙️ Mode Sistem")
mode = st.sidebar.radio(
    "Pilih Mode:",
    ["🔍 Rekomendasi dari Nutrisi", "🍱 Hitung Nutrisi dari 2 Makanan"]
)

# ==========================
# MODE 1: REKOMENDASI
# ==========================
if mode == "🔍 Rekomendasi dari Nutrisi":

    st.title("🍽️ Sistem Rekomendasi Makanan Berbasis CBR")
    st.write("Masukkan kebutuhan nutrisi Anda, lalu sistem akan merekomendasikan makanan terdekat.")

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

        st.subheader("🖼️ Gambar Makanan Rekomendasi")
        show_food_image_from_url(rekomendasi_terbaik['image'], size=(250, 250))

    else:
        st.info("Silahkan isi kebutuhan terlebih dahulu lalu klik 'Cari Rekomendasi'")


# ==========================
# MODE 2: HITUNG 2 MAKANAN
# ==========================
else:

    st.title("🍱 Sistem Hitung Nutrisi dari 2 Makanan")
    st.write("Pilih dua makanan untuk mengetahui total kandungan nutrisinya.")

    food_list = df['name'].tolist()

    food1 = st.selectbox("Pilih Makanan Pertama", food_list)
    food2 = st.selectbox("Pilih Makanan Kedua", food_list)

    if st.button("Hitung Total Nutrisi"):
        makanan1 = df[df['name'] == food1].iloc[0]
        makanan2 = df[df['name'] == food2].iloc[0]

        total_kalori = makanan1['calories'] + makanan2['calories']
        total_lemak = makanan1['fat'] + makanan2['fat']
        total_protein = makanan1['protein'] + makanan2['protein']
        total_karbo = makanan1['carbs'] + makanan2['carbs']

        # Tampilkan 2 kolom untuk makanan
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🍱 Makanan 1")
            show_food_image_from_url(makanan1['image'], size=(250, 250))
            st.write(makanan1[['calories', 'fat', 'protein', 'carbs']])

        with col2:
            st.subheader("🍛 Makanan 2")
            show_food_image_from_url(makanan2['image'], size=(250, 250))
            st.write(makanan2[['calories', 'fat', 'protein', 'carbs']])

        st.subheader("✅ Total Nutrisi Gabungan")
        st.success(f"""
        🔥 Kalori: {total_kalori:.2f} kkal  
        🥑 Lemak: {total_lemak:.2f} g  
        💪 Protein: {total_protein:.2f} g  
        🍞 Karbohidrat: {total_karbo:.2f} g
        """)

    else:
        st.info("Silakan pilih 2 makanan lalu klik **Hitung Total Nutrisi**")
