import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import io
import soundfile as sf
import noisereduce as nr
from pydub import AudioSegment
from scipy.io.wavfile import write
from datetime import datetime
import base64
from fpdf import FPDF
import json
import tempfile

st.set_page_config(page_title="Heart Sound Analyzer", layout="wide")

# Title
st.title("💓 Heart Sound Analyzer & Case Recorder")

# --------------------- Patient Details ---------------------
st.header("🧑‍⚕️ Enter Patient Details to Start a Case")
with st.form("patient_form"):
    patient_name = st.text_input("Patient Name")
    patient_id = st.text_input("Patient ID")
    age = st.number_input("Age", min_value=0, max_value=150, step=1)
    gender = st.radio("Gender", ["Male", "Female", "Other"])
    submit_patient = st.form_submit_button("Start Case")

if not submit_patient:
    st.warning("Please fill in patient details to proceed.")

# --------------------- Upload or Record ---------------------
st.header("🎙️ Upload or Record Heart Sound")
uploaded_file = st.file_uploader("Upload a .wav file", type=["wav"])

# Audio recording (requires JavaScript component for full microphone support)
def record_audio():
    import sounddevice as sd
    import wavio
    duration = 5  # seconds
    fs = 44100
    st.info("Recording for 5 seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavio.write(temp_wav.name, recording, fs, sampwidth=2)
    return temp_wav.name

if st.button("🎤 Record Heartbeat"):
    recorded_path = record_audio()
    st.success("Recording saved.")
    uploaded_file = open(recorded_path, 'rb')

if uploaded_file:
    y, sr = librosa.load(uploaded_file, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    # Waveform adjustment sliders
    st.sidebar.header("🔧 Waveform Adjustments")
    amp_factor = st.sidebar.slider("Amplitude Scale", 0.1, 5.0, 1.0)
    start_sec, end_sec = st.sidebar.slider("Select Time Range (seconds)", 0.0, duration, (0.0, duration), 0.1)
    start_sample = int(start_sec * sr)
    end_sample = int(end_sec * sr)
    y_trimmed = y[start_sample:end_sample] * amp_factor

    # Show original waveform
    st.subheader("📈 Original Heartbeat Waveform")
    fig, ax = plt.subplots()
    librosa.display.waveshow(y_trimmed, sr=sr, ax=ax)
    ax.set_title("Original Audio")
    st.pyplot(fig)

    # Audio Player - Normal
    st.audio(librosa.to_bytes(y_trimmed, sr=sr), format='audio/wav', start_time=0)

    # Noise Reduction
    st.subheader("🔇 Noise Reduction")
    denoised = nr.reduce_noise(y=y_trimmed, sr=sr)
    st.audio(librosa.to_bytes(denoised, sr=sr), format='audio/wav', start_time=0)

    # Show denoised waveform
    fig2, ax2 = plt.subplots()
    librosa.display.waveshow(denoised, sr=sr, ax=ax2, color='orange')
    ax2.set_title("Denoised Audio")
    st.pyplot(fig2)

    # --------------------- Analyse and Save ---------------------
    st.header("📋 Analyse Case & Download Report")
    if st.button("🔍 Analyse Case"):
        st.success("Case Analyzed and Saved.")

        # Display details
        st.markdown(f"**Patient Name**: {patient_name}")
        st.markdown(f"**Patient ID**: {patient_id}")
        st.markdown(f"**Age**: {age}")
        st.markdown(f"**Gender**: {gender}")

        # Save to local JSON file (simulate cloud)
        case = {
            "patient_name": patient_name,
            "patient_id": patient_id,
            "age": age,
            "gender": gender,
            "timestamp": str(datetime.now())
        }

        with open("case_data.json", "a") as f:
            f.write(json.dumps(case) + "\n")

    # --------------------- PDF Report ---------------------
    def generate_pdf(patient_name, patient_id, age, gender):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Heart Sound Analysis Report", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Name: {patient_name}", ln=True)
        pdf.cell(200, 10, txt=f"ID: {patient_id}", ln=True)
        pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
        pdf.cell(200, 10, txt=f"Gender: {gender}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {datetime.now()}", ln=True)

        # Save PDF
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        return pdf_bytes

    if st.button("📄 Download Report as PDF"):
        pdf = generate_pdf(patient_name, patient_id, age, gender)
        b64_pdf = base64.b64encode(pdf).decode('utf-8')
        href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{patient_id}_report.pdf">📥 Click here to download your PDF report</a>'
        st.markdown(href, unsafe_allow_html=True)

    # --------------------- Final Save ---------------------
    if st.button("☁️ Save Case to Cloud"):
        st.success("Case data has been saved to the cloud (simulated).")
        # You can later plug Firebase, AWS S3 or Firestore here
else:
    st.info("Upload or record a heartbeat sound to continue.")
