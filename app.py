# --- Streamlit App Eksperimen ShapeItUp (Tanpa toggle Filled/Unfilled/Open) ---
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# --- Inisialisasi Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)

# --- Akses Google Sheet ---
worksheet = None
try:
    spreadsheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g")
    worksheet = spreadsheet.worksheet("Eksperimen_2")  # Sheet baru khusus eksperimen 2
except Exception as e:
    st.error(f"Gagal membuka spreadsheet: {e}")

# --- Jika akses sukses ---
if worksheet is not None:
    st.title("\U0001F3AF Eksperimen Estimasi Y Berdasarkan Bentuk (Eksperimen 2)")
    st.info("""
    **Instruksi:** Lihat scatterplot di bawah ini. Tiap kategori direpresentasikan oleh bentuk berbeda.
    Pilih kategori (bentuk) yang memiliki rata-rata nilai Y tertinggi.
    """)

    n_categories = st.selectbox("\U0001F522 Jumlah Kategori", [2, 4, 6])

    # --- Shape Terpilih Berdasarkan Matrix ---
    shape_images = {
        "arrow-dash.png": "Arrow Dash",
        "arrow-filled.png": "Arrow Filled",
        "cross-filled.png": "Cross Filled",
        "pentagon-dash.png": "Pentagon Dash",
        "triangle-dash.png": "Triangle Dash",
        "triangle-filled.png": "Triangle Filled"
    }
    selected_shape_keys = list(shape_images.keys())[:n_categories]

    # --- Simpan data scatter
    if "data_initialized" not in st.session_state or st.session_state.n_categories != n_categories:
        st.session_state.n_categories = n_categories
        st.session_state.x_data = [np.random.uniform(0, 1.5, 15) for _ in range(n_categories)]
        st.session_state.y_data = [np.random.uniform(0, 1.5, 15) for _ in range(n_categories)]
        st.session_state.data_initialized = True

    # --- Plot dengan gambar PNG sebagai marker ---
    fig, ax = plt.subplots()
    for i in range(n_categories):
        x_vals = st.session_state.x_data[i]
        y_vals = st.session_state.y_data[i]
        shape_path = os.path.join("shapes", selected_shape_keys[i])

        for x, y in zip(x_vals, y_vals):
            img = Image.open(shape_path).convert("RGBA")
            img = img.resize((20, 20))
            im = OffsetImage(img, zoom=0.25)
            ab = AnnotationBbox(im, (x, y), frameon=False)
            ax.add_artist(ab)

        ax.scatter([], [], label=shape_images[selected_shape_keys[i]])  # dummy legend

    ax.set_xlim(-0.1, 1.6)
    ax.set_ylim(-0.1, 1.6)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # --- Pilihan dan Evaluasi ---
    selected_category = st.selectbox("\U0001F4CC Pilih kategori dengan rata-rata Y tertinggi:",
                                     [f"Kategori {i+1}" for i in range(n_categories)])

    if st.button("\U0001F680 Submit Jawaban"):
        y_means = [np.mean(y) for y in st.session_state.y_data]
        true_idx = int(np.argmax(y_means)) + 1
        selected_idx = int(selected_category.split(" ")[1])
        is_correct = (selected_idx == true_idx)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = [timestamp, n_categories, selected_category, "Benar" if is_correct else "Salah",
                    f"Kategori {true_idx}", ", ".join(f"{m:.3f}" for m in y_means)]

        try:
            worksheet.append_row(response)
            if is_correct:
                st.success(f"\u2705 Jawaban Anda benar! Kategori {true_idx} yang tertinggi.")
            else:
                st.error(f"\u274C Jawaban salah. Nilai Y tertinggi ada di kategori {true_idx}.")
        except Exception as e:
            st.error(f"Gagal simpan ke spreadsheet: {e}")

        with st.expander("\U0001F50D Rata-rata Y per kategori"):
            for i, mean in enumerate(y_means):
                st.write(f"Kategori {i+1}: {mean:.3f}")
else:
    st.error("Aplikasi tidak dapat melanjutkan karena gagal akses Google Sheets.")
