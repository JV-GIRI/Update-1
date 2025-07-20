import streamlit as st
import numpy as np
import soundfile as sf
import scipy.signal as signal
import matplotlib.pyplot as plt
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF
import io

# Page config
st.set_page_config(page_title="Heart AI + Case Sheets", layout="wide")

# Google Sheets setup
SA = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
gc = gspread.authorize(SA)
sheet = gc.open_by_url(st.secrets["private_gsheets_url"]).sheet1

# AI Murmur model placeholder
def predict_murmur(wav):
    # Dummy logic, replace with real model inference
    score = float(np.random.rand())
    label = "Murmur" if score > 0.5 else "Normal"
    return score, label

# PDF report generator
def generate_pdf_summary(name, score, label):
    buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Heart Murmur Analysis", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Patient: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.now()}", ln=True)
    pdf.cell(200, 10, txt=f"Murmur Score: {score:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Diagnosis: {label}", ln=True)
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# UI: Recording / Uploading
st.title("Heart AI Analyzer & Case History")
name = st.text_input("Patient Name")
uploaded = st.file_uploader("Upload heart sound (.wav)", type=["wav"])
if uploaded:
    data, sr = sf.read(uploaded)
    st.audio(uploaded, format="audio/wav")
    st.subheader("Waveform")
    plt.figure(figsize=(10, 3))
    plt.plot(np.linspace(0, len(data)/sr, len(data)), data)
    plt.xlabel("Time (s)"); plt.ylabel("Amplitude")
    st.pyplot(plt)

    # Denoise
    b, a = signal.butter(4, [20/(0.5*sr), 150/(0.5*sr)], btype='band')
    filtered = signal.filtfilt(b, a, data)
    st.audio(write_filtered := io.BytesIO(), format="audio/wav", data=sf.write(write_filtered, filtered, sr, format="WAV"))
    st.subheader("Waveform (Filtered)")
    plt.figure(figsize=(10,3))
    plt.plot(np.linspace(0, len(filtered)/sr, len(filtered)), filtered, color='orange')
    st.pyplot(plt)

    # AI Inference
    score, label = predict_murmur(filtered)
    st.subheader("🧠 AI Diagnosis")
    st.write(f"**Murmur Score:** {score:.2f}")
    st.write(f"**Prediction:** {label}")

    # Save to Google Sheets
    if st.button("💾 Save Case to Google Sheets"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, name, score, label])
        st.success("✅ Case saved to Google Sheets")

    # PDF Download
    pdf_bytes = generate_pdf_summary(name, score, label)
    st.download_button("📄 Download Report PDF", data=pdf_bytes, file_name=f"{name}_report.pdf", mime="application/pdf")
