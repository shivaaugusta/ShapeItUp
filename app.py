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

# Lanjutkan aplikasi hanya jika worksheet tersedia
if worksheet is not None:
    st.title("Eksperimen HCI: Estimasi Rata-rata")
    n_categories = st.slider("Jumlah Kategori", min_value=2, max_value=10, value=5, step=1)

    markers = ['^', 'o', 's', '*', 'v', '<', '>', 'p', 'h', 'D']
    fig, ax = plt.subplots()
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
    
    # Simpan data Y untuk menghitung rata-rata
    y_data_per_category = []
    for i in range(n_categories):
        x = np.random.uniform(0, 1.5, 15)
        y = np.random.uniform(0, 1.5, 15)
        y_data_per_category.append(y)  # Simpan data Y untuk perhitungan
        marker = markers[i % len(markers)]
        ax.scatter(x, y, marker=marker, s=80, c=colors[i % len(colors)], label=f'Kategori {i+1}', alpha=0.7)

    ax.axhline(y=0.75, color='r', linestyle='--')
    ax.set_xlim(-0.1, 1.6)
    ax.set_ylim(-0.1, 1.6)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()
    st.pyplot(fig)

    # Hitung rata-rata Y untuk setiap kategori
    y_means = [np.mean(y) for y in y_data_per_category]
    # Tentukan kategori dengan rata-rata Y tertinggi (indeks dimulai dari 0, jadi tambah 1)
    true_highest_category = np.argmax(y_means) + 1

    # Debugging: Tampilkan rata-rata Y untuk verifikasi
    st.write("Rata-rata Y per kategori:", [f"Kategori {i+1}: {mean:.3f}" for i, mean in enumerate(y_means)])
    st.write(f"Kategori dengan rata-rata Y tertinggi (sebenarnya): Kategori {true_highest_category}")

    st.write("Pilih kategori dengan rata-rata Y tertinggi:")
    selected_category = st.selectbox("Kategori", [f"Kategori {i+1}" for i in range(n_categories)])

    if st.button("Submit"):
        try:
            # Ambil indeks kategori yang dipilih (misalnya, "Kategori 4" -> 4)
            selected_category_idx = int(selected_category.split(" ")[1])
            # Tentukan apakah pilihan pengguna benar
            is_correct = (selected_category_idx == true_highest_category)
            
            # Simpan data ke Google Sheets, termasuk apakah pilihan benar atau salah
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response_data = [timestamp, n_categories, selected_category, "Benar" if is_correct else "Salah"]
            worksheet.append_row(response_data)
            
            # Beri feedback ke pengguna
            if is_correct:
                st.success(f"Respons disimpan: {selected_category}. Pilihan Anda benar!")
            else:
                st.error(f"Respons disimpan: {selected_category}. Pilihan Anda salah. Kategori dengan rata-rata Y tertinggi adalah Kategori {true_highest_category}.")
        except Exception as e:
            st.error(f"Gagal menyimpan: {e}")
else:
    st.error("Aplikasi tidak dapat melanjutkan karena gagal mengakses worksheet.")
