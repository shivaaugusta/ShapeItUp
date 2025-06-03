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

# --- Experiment Parameters ---
SHAPE_TYPES = {
    "Filled": ["o", "s", "D", "^", "v", "p", "h"],  # ● ■ ◆ ▲ ▼ ⬡ ⬢
    "Unfilled": ["o", "s", "D", "^", "v", "p", "h"],  # ○ □ ◇ △ ▽ ⬡ ⬢
    "Open": ["P", "X", "*", "+", "x", "d", "|"]  # ✱ ✖ ✚ ✛ ✜ ✢ ✕
}

# --- Experiment Functions ---
def generate_data(categories):
    return {f"Kategori {i+1}": np.random.normal(loc=np.random.uniform(0.1, 0.9), scale=0.1, size=20) 
            for i in range(categories)}

def plot_scatter(data, shape_type, categories):
    fig, ax = plt.subplots(figsize=(8, 6))
    markers = SHAPE_TYPES[shape_type]
    
    for i, (cat, values) in enumerate(data.items()):
        marker = markers[i % len(markers)]
        ax.scatter(np.random.rand(len(values)), values, 
                  label=cat, marker=marker, s=100)
    
    ax.set_title(f"Scatterplot ({shape_type} Shapes)")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    return fig

def get_correct_answer(data):
    return max(data.items(), key=lambda x: np.mean(x[1]))[0]

# --- Streamlit App ---
def main():
    st.title("WEksperimen HCI: Estimasi Rata-rata Y")
    
    # Initialize session state
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    
    # Experiment controls
    col1, col2 = st.columns(2)
    with col1:
        categories = st.slider("Jumlah Kategori", 2, 10, 5)
    with col2:
        shape_type = st.selectbox("Tipe Bentuk", list(SHAPE_TYPES.keys()))
    
    # Generate data and plot
    data = generate_data(categories)
    fig = plot_scatter(data, shape_type, categories)
    st.pyplot(fig)
    
    # User response
    correct_answer = get_correct_answer(data)
    user_choice = st.selectbox(
        "Pilih kategori dengan rata-rata Y tertinggi:",
        list(data.keys())
    )
    
    # Submit button
    if st.button("Submit Jawaban"):
        st.session_state.submitted = True
        is_correct = user_choice == correct_answer
        
        # Record results
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "Timestamp": timestamp,
            "Jumlah Kategori": categories,
            "Kategori Dipilih": user_choice,
            "Hasil Benar/Salah": "Benar" if is_correct else "Salah",
            "Tipe Bentuk": shape_type
        }
        
        # Save to Google Sheets
        try:
            sheet = connect_to_gsheet()
            sheet.append_row(list(result.values()))
            st.success("Data berhasil disimpan!")
        except Exception as e:
            st.error(f"Error menyimpan data: {e}")
        
        # Show feedback
        if is_correct:
            st.balloons()
            st.success("✅ Jawaban benar!")
        else:
            st.error(f"❌ Salah. Jawaban benar: {correct_answer}")
    
    # Debug info (optional)
    if st.checkbox("Tampilkan data mentah (debug)"):
        st.write(data)
        st.write(f"Rata-rata Y per kategori:")
        st.write({k: np.mean(v) for k, v in data.items()})

if __name__ == "__main__":
    main()
