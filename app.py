import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Inisialisasi Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)

# Ganti dengan SPREADSHEET_ID Anda
spreadsheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g")
worksheet = spreadsheet.sheet1  # Gunakan sheet pertama

# Judul aplikasi
st.title("Eksperimen HCI: Estimasi Rata-rata")

# Input jumlah kategori
n_categories = st.slider("Jumlah Kategori", min_value=2, max_value=10, value=5, step=1)

# Daftar bentuk
shapes = [
    ('^', 'full'), ('o', 'none'), ('s', 'full'), ('*', 'none'), ('v', 'full'),
    ('<', 'none'), ('>', 'full'), ('p', 'none'), ('h', 'full'), ('D', 'none')
]

# Simulasi data dan buat scatterplot
fig, ax = plt.subplots()
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
for i in range(n_categories):
    x = np.random.uniform(0, 1.5, 15)
    y = np.random.uniform(0, 1.5, 15)
    marker, fill = shapes[i]
    ax.scatter(x, y, marker=marker, fillstyle=fill, s=80, c=colors[i], label=f'Kategori {i+1}', alpha=0.7)

ax.axhline(y=0.75, color='r', linestyle='--')
ax.set_xlim(-0.1, 1.6)
ax.set_ylim(-0.1, 1.6)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.legend()
st.pyplot(fig)

# Tugas pengguna: Pilih rata-rata tertinggi
st.write("Pilih kategori dengan rata-rata Y tertinggi:")
selected_category = st.selectbox("Kategori", [f"Kategori {i+1}" for i in range(n_categories)])

# Tombol untuk submit respons
if st.button("Submit"):
    # Catat timestamp dan data
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response_data = [timestamp, n_categories, selected_category]

    # Tambahkan data ke Google Sheets
    worksheet.append_row(response_data)
    st.success(f"Respons disimpan: {selected_category}")
