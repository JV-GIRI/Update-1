import streamlit as st
import numpy as np
import soundfile as sf
import noisereduce as nr
from scipy.signal import butter, lfilter
import io
from fpdf import FPDF
from pydub import AudioSegment
import tempfile
import matplotlib.pyplot as plt
import datetime

# --- App Title ---
st.set_page_config(page_title="PCG AI Diagnosis App", layout="centered")
st.markdown("<h1 style='text-align: center;'>💓 HEARTEST : AI assisted PCG analyzer</h1>", unsafe_allow_html=True)

# --- 1. Patient Details ---
st.sidebar.subheader("📋 Patient Details")
patient_name = st.sidebar.text_input("Name")
age = st.sidebar.number_input("Age", 1, 120)
sex = st.sidebar.selectbox("Sex", ["Male", "Female"])
patient_id = st.sidebar.text_input("Patient ID", value=f"PCG{np.random.randint(1000,9999)}")

# --- 2. Record Audio ---
st.markdown("### 🎙️ Record Heart Sound")
duration = st.slider("Recording duration (seconds)", 3, 15, 5)
record_btn = st.button("🔴 Record Now")

# Temporary storage
uploaded_file = None
if record_btn:
    st.info("Recording... Please wait.")
    import sounddevice as sd

    fs = 44100
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()

    temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    sf.write(temp_audio_path, audio, fs)
    uploaded_file = temp_audio_path
    st.success("✅ Recorded Successfully!")

# Or Upload
st.markdown("### 📁 Or Upload Heart Sound")
uploaded_file = st.file_uploader("Upload .wav file", type=["wav"])

# --- 3. Plot Waveform ---
def plot_waveform(data, sr, title="Waveform"):
    fig, ax = plt.subplots()
    ax.plot(np.linspace(0, len(data) / sr, len(data)), data)
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

# --- 4. Bandpass Filter ---
def butter_bandpass_filter(data, lowcut=20.0, highcut=1000.0, fs=44100, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band')
    y = lfilter(b, a, data)
    return y

# --- 5. Process File ---
if uploaded_file:
    st.markdown("### 🔎 Waveform & Playback")
    data, sr = sf.read(uploaded_file)
    data = data[:, 0] if len(data.shape) > 1 else data
    plot_waveform(data, sr, "🔉 Original Waveform")
    st.audio(uploaded_file, format="audio/wav", start_time=0)

    # Bandpass Filter + Noise Reduction
    filtered = butter_bandpass_filter(data, 20, 1000, sr)
    reduced_noise = nr.reduce_noise(y=filtered, sr=sr)

    # Show filtered waveform
    plot_waveform(reduced_noise, sr, "🔇 After Noise Reduction")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        sf.write(f.name, reduced_noise, sr)
        st.audio(f.name, format="audio/wav")

    # Heart Rate Estimation (Mock logic)
    estimated_hr = np.random.randint(60, 100)
    st.metric("💓 Estimated Heart Rate", f"{estimated_hr} bpm")

    # Simulate AI Diagnosis
    st.markdown("### 🤖 AI Diagnosis")
    ai_result = "Normal Heart Sounds Detected"
    if estimated_hr > 90:
        ai_result = "Possible Tachycardia Pattern Detected"
    elif estimated_hr < 60:
        ai_result = "Possible Bradycardia Pattern Detected"
    st.success(ai_result)

    # --- 6. Generate Report ---
    st.markdown("### 📄 Download Report")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Heart Sound AI Report", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, f"Patient Name: {patient_name}", ln=True)
    pdf.cell(200, 10, f"Age: {age}", ln=True)
    pdf.cell(200, 10, f"Sex: {sex}", ln=True)
    pdf.cell(200, 10, f"Patient ID: {patient_id}", ln=True)
    pdf.cell(200, 10, f"Estimated Heart Rate: {estimated_hr} bpm", ln=True)
    pdf.multi_cell(0, 10, f"AI Interpretation:\n{ai_result}")

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    st.download_button("📥 Download Report PDF", data=pdf_output.getvalue(), file_name="Heart_Report.pdf", mime="application/pdf")
