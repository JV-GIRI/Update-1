import streamlit as st
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import librosa
import librosa.display
import io
import tempfile
from scipy.signal import butter, lfilter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

# ------------------ Helper Functions ------------------ #
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y

def generate_waveform_plot(y, sr, title):
    fig, ax = plt.subplots()
    librosa.display.waveshow(y, sr=sr, ax=ax)
    ax.set(title=title)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

def save_pdf_report(patient_name, findings, waveform_img_buf):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 800, f"Patient Name: {patient_name}")
    c.drawString(100, 780, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 760, f"Findings: {findings}")
    c.drawImage(waveform_img_buf, 100, 500, width=400, height=200)
    c.save()
    buffer.seek(0)
    return buffer

# ------------------ Streamlit UI ------------------ #
st.set_page_config(layout="wide")
st.title("Live Heartbeat Analysis & Case Recorder")

st.sidebar.header("Patient Details")
patient_name = st.sidebar.text_input("Name")
patient_age = st.sidebar.number_input("Age", min_value=0, max_value=120)
patient_gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("Upload Heart Sound (.wav)", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav', start_time=0)
    y, sr = librosa.load(uploaded_file, sr=None)

    st.subheader("Original Waveform")
    original_plot = generate_waveform_plot(y, sr, "Original Heartbeat")
    st.image(original_plot)

    duration = st.slider("Adjust Duration (seconds)", 1.0, float(len(y) / sr), float(len(y) / sr))
    amp_scale = st.slider("Adjust Amplitude", 0.1, 5.0, 1.0)
    y = y[:int(sr * duration)] * amp_scale

    if st.button("Apply Noise Reduction"):
        y_filtered = butter_lowpass_filter(y, cutoff=200.0, fs=sr)
        st.subheader("Filtered Waveform")
        filtered_plot = generate_waveform_plot(y_filtered, sr, "Filtered Heartbeat")
        st.image(filtered_plot)
        st.audio(y_filtered, format='audio/wav')

        filtered_wav = tempfile.NamedTemporaryFile(delete=False, suffix="_filtered.wav")
        sf.write(filtered_wav.name, y_filtered, sr)
        st.download_button("Download Filtered Sound", data=open(filtered_wav.name, "rb").read(), file_name="filtered_heartbeat.wav")

    if st.button("Analyse & Generate Report"):
        waveform_img_buf = generate_waveform_plot(y, sr, "Analysed Heartbeat")
        findings = "Normal heart sound" if max(y) < 0.5 else "Abnormal/murmur detected"
        pdf = save_pdf_report(patient_name, findings, waveform_img_buf)
        st.download_button("Download PDF Report", data=pdf, file_name=f"{patient_name}_heartbeat_report.pdf")

    if st.button("Save Case to Cloud (Local Placeholder)"):
        case_dir = f"saved_cases/{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(case_dir, exist_ok=True)
        with open(f"{case_dir}/details.txt", "w") as f:
            f.write(f"Name: {patient_name}\nAge: {patient_age}\nGender: {patient_gender}\n")
        sf.write(f"{case_dir}/original.wav", y, sr)
        st.success("Case saved locally. Cloud integration coming soon!")

else:
    st.info("Upload a .wav file to begin analysis.")

# Optional: Add audio recording via browser (future integration using media stream capture)
