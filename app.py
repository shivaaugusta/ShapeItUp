import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Inisialisasi Google Sheets menggunakan Streamlit Secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)

# Debugging: Tampilkan informasi kredensial
st.write("Client Email:", creds.service_account_email)

worksheet = None  # Inisialisasi default
try:
    spreadsheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g")
    st.write("Berhasil membuka spreadsheet:", spreadsheet.title)
    worksheet = spreadsheet.sheet1
except PermissionError as e:
    st.error(f"Gagal membuka spreadsheet: {e}")
except Exception as e:
    st.error(f"Error lain: {e}")

# --- Aplikasi Hanya Jalan Jika Google Sheet Siap ---
if worksheet is not None:
    # Judul & Penjelasan
    st.title("🎯 yEksperimen Estimasi Rata-rata Y Berdasarkan Bentuk")
    st.info("""
    **Instruksi:** Lihat grafik scatterplot di bawah ini. Tiap kategori direpresentasikan oleh bentuk dan warna yang berbeda.
    
    Tugas Anda: Pilih kategori (berdasarkan bentuk) yang memiliki **rata-rata nilai Y tertinggi**. 
    
    Anda **tidak perlu menghitung**. Cukup amati titik-titiknya dan tebak berdasarkan **persepsi visual** Anda.
    """)

    # Slider jumlah kategori
    n_categories = st.slider("🔢 Jumlah Kategori", min_value=2, max_value=10, value=5, step=1)

    # Persiapan bentuk & warna
    markers = ['^', 'o', 's', '*', 'v', '<', '>', 'p', 'h', 'D']
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']

    fig, ax = plt.subplots()
    y_data_per_category = []

    for i in range(n_categories):
        x = np.random.uniform(0, 1.5, 15)
        y = np.random.uniform(0, 1.5, 15)
        y_data_per_category.append(y)
        ax.scatter(
            x, y,
            marker=markers[i % len(markers)],
            s=80,
            c=colors[i % len(colors)],
            label=f'Kategori {i+1}',
            alpha=0.75,
            edgecolors='k'
        )

    ax.set_xlim(-0.1, 1.6)
    ax.set_ylim(-0.1, 1.6)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Hitung rata-rata Y tiap kategori
    y_means = [np.mean(y) for y in y_data_per_category]
    true_highest_category = np.argmax(y_means) + 1  # +1 karena label dimulai dari 1

    # Pilihan user
    selected_category = st.selectbox("📌 Pilih kategori dengan rata-rata Y tertinggi:", [f"Kategori {i+1}" for i in range(n_categories)])

    if st.button("🚀 Submit Jawaban"):
        selected_category_idx = int(selected_category.split(" ")[1])
        is_correct = (selected_category_idx == true_highest_category)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response_data = [
            timestamp,
            n_categories,
            selected_category,
            "Benar" if is_correct else "Salah",
            f"Kategori {true_highest_category}",
            ", ".join([f"{m:.3f}" for m in y_means])
        ]

        try:
            worksheet.append_row(response_data)
            if is_correct:
                st.success(f"✅ Jawaban Anda benar! Kategori {true_highest_category} memiliki rata-rata Y tertinggi.")
            else:
                st.error(f"❌ Jawaban Anda salah. Rata-rata Y tertinggi ada di **Kategori {true_highest_category}**.")
        except Exception as e:
            st.error(f"Gagal menyimpan ke Google Sheets: {e}")

        with st.expander("🔍 Rata-rata Y untuk masing-masing kategori"):
            for i, mean in enumerate(y_means):
                st.write(f"Kategori {i+1}: {mean:.3f}")
else:
    st.error("Aplikasi tidak dapat melanjutkan karena gagal mengakses Google Sheets.")
