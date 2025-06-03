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
    for i in range(n_categories):
        x = np.random.uniform(0, 1.5, 15)
        y = np.random.uniform(0, 1.5, 15)
        marker = markers[i % len(markers)]
        ax.scatter(x, y, marker=marker, s=80, c=colors[i % len(colors)], label=f'Kategori {i+1}', alpha=0.7)

    ax.axhline(y=0.75, color='r', linestyle='--')
    ax.set_xlim(-0.1, 1.6)
    ax.set_ylim(-0.1, 1.6)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()
    st.pyplot(fig)

    st.write("Pilih kategori dengan rata-rata Y tertinggi:")
    selected_category = st.selectbox("Kategori", [f"Kategori {i+1}" for i in range(n_categories)])

    if st.button("Submit"):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response_data = [timestamp, n_categories, selected_category]
            worksheet.append_row(response_data)
            st.success(f"Respons disimpan: {selected_category}")
        except Exception as e:
            st.error(f"Gagal menyimpan: {e}")
else:
    st.error("Aplikasi tidak dapat melanjutkan karena gagal mengakses worksheet.")
