%%writefile app.py
import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

st.set_page_config(page_title="SPK Prestasi Siswa", layout="wide")

st.title("🎓 Sistem Pendukung Keputusan Prestasi Siswa")
st.write("Metode Classification - Random Forest")

uploaded_file = st.file_uploader("📂 Upload Dataset Student CSV", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.subheader("📊 Dataset")
    st.dataframe(data.head())

    # Konversi G3 ke Kategori Prestasi
    def kategori(nilai):
        if nilai >= 16:
            return "Tinggi"
        elif nilai >= 11:
            return "Sedang"
        else:
            return "Rendah"

    data["Prestasi"] = data["G3"].apply(kategori)

    X = data.drop(["G3", "G2", "G1", "Prestasi"], axis=1)
    y = data["Prestasi"]

    # Encoding data kategori
    for col in X.columns:
        if X[col].dtype == object:
            X[col] = LabelEncoder().fit_transform(X[col])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    akurasi = accuracy_score(y_test, y_pred)

    st.subheader("✅ Hasil Akurasi Model")
    st.success(f"Akurasi Model: {akurasi * 100:.2f}%")

    st.subheader("📌 Input Data Siswa Baru")

    input_data = {}

    for col in X.columns:
        input_data[col] = st.number_input(f"Masukkan {col}", value=0)

    if st.button("🔍 Prediksi Prestasi"):
        input_df = pd.DataFrame([input_data])
        hasil = model.predict(input_df)

        st.subheader("📢 Hasil Prediksi")
        st.success(f"Prestasi Siswa Diprediksi: {hasil[0]}")

    st.subheader("📈 Visualisasi Jumlah Prestasi")
    fig, ax = plt.subplots()
    data["Prestasi"].value_counts().plot(kind="bar", ax=ax)
    st.pyplot(fig)
