import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Setup koneksi Google Sheets
def kirim_ke_sheets(data_dict):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").sheet1
    sheet.append_row([str(data_dict[k]) for k in data_dict])

# Aplikasi Streamlit
st.title("Eksperimen HCI: Estimasi Rata-rata Y")

num_categories = st.slider("Jumlah Kategori", 2, 10, 4)
markers = ['o', 's', '^', 'v', '>', '<', 'D', 'p', '*', 'h']
selected_markers = markers[:num_categories]

np.random.seed(42)
means = []
options = []

fig, ax = plt.subplots()
for i in range(num_categories):
    x = np.random.rand(20)
    y = np.random.normal(loc=0.2*i + 0.1, scale=0.05, size=20)
    ax.scatter(x, y, marker=selected_markers[i], label=f'Kategori {i+1}')
    means.append(np.mean(y))
    options.append(f'Kategori {i+1}')

ax.legend()
st.pyplot(fig)

guess = st.radio("Pilih kategori dengan rata-rata Y tertinggi:", options)

if st.button("Submit"):
    correct_idx = np.argmax(means)
    correct = options[correct_idx]
    is_correct = guess == correct
    st.success("Benar!" if is_correct else f"Salah. Jawaban benar: " + correct)

    log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jumlah_kategori": num_categories,
        "jawaban_user": guess,
        "jawaban_benar": correct,
        "benar": is_correct
    }

    try:
        kirim_ke_sheets(log)
        st.info("✅ Data berhasil dikirim ke Google Sheets.")
    except Exception as e:
        st.error(f"❌ Gagal mengirim ke Sheets: {e}")
