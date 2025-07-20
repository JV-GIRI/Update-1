import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import io
import base64
import wave
from scipy.io import wavfile
from pydub import AudioSegment
from pydub.playback import play
import tempfile
from fpdf import FPDF

# Set Page Config
st.set_page_config(
    page_title="Heartbeat AI Analyzer",
    layout="wide",
    initial_sidebar_state="auto"
)

# Custom CSS for styling
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f8f9fa;
        }
        .main {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.1);
        }
        .stButton>button {
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5em 1em;
            font-weight: 600;
        }
        .stTextInput>div>div>input {
            padding: 0.75em;
            border-radius: 10px;
            border: 1px solid #ccc;
        }
        hr {
            border: 1px solid #dee2e6;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🩺 Heart Sound Recorder & Analyzer")

with st.container():
    st.subheader("🧑‍⚕️ Patient Details")
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    case_id = st.text_input("Case ID")
    st.markdown("---")

# RECORDING
st.subheader("🎙️ Record Heart Sound")
duration = st.slider("Recording Duration (seconds)", 2, 10, 5)
record_button = st.button("🔴 Start Recording")

if record_button:
    st.info("Recording...")
    fs = 44100
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    st.success("Recording Complete")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(temp_file.name, fs, recording)

    audio_bytes = open(temp_file.name, "rb").read()
    st.audio(audio_bytes, format="audio/wav")

    st.markdown("#### 🔍 Original Waveform")
    fig, ax = plt.subplots()
    time_axis = np.linspace(0, duration, len(recording))
    ax.plot(time_axis, recording, color="#2c3e50")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

    # Noise Reduction
    st.subheader("🔧 Noise Reduction")
    lowcut = st.slider("Low Cut Frequency", 10, 100, 30)
    highcut = st.slider("High Cut Frequency", 100, 800, 150)

    def butter_bandpass(lowcut, highcut, fs, order=6):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        return scipy.signal.butter(order, [low, high], btype='band')

    def apply_filter(data, lowcut, highcut, fs):
        b, a = butter_bandpass(lowcut, highcut, fs)
        return scipy.signal.lfilter(b, a, data.flatten())

    filtered = apply_filter(recording, lowcut, highcut, fs).reshape(-1, 1)

    st.markdown("#### 🎵 Filtered Waveform")
    fig2, ax2 = plt.subplots()
    ax2.plot(time_axis, filtered, color="#27ae60")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Amplitude")
    st.pyplot(fig2)

    # Save filtered sound
    temp_clean = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavfile.write(temp_clean.name, fs, filtered.astype(np.float32))

    # Play cleaned sound
    st.audio(temp_clean.name, format="audio/wav")

    # PDF Report
    st.subheader("📄 Generate Report")
    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt="Heartbeat Sound Analysis Report", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Patient Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
        pdf.cell(200, 10, txt=f"Case ID: {case_id}", ln=True)
        pdf.cell(200, 10, txt=f"Recording Duration: {duration} sec", ln=True)
        pdf.cell(200, 10, txt=f"Bandpass Range: {lowcut}Hz - {highcut}Hz", ln=True)

        # Save PDF
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(pdf_file.name)

        with open(pdf_file.name, "rb") as f:
            st.download_button("📥 Download PDF Report", f, file_name="heartbeat_report.pdf")

    # Cloud Save Placeholder
    st.subheader("☁️ Save to Cloud (Coming Soon)")
    st.info("Cloud save functionality will integrate Firebase/Supabase on your request.")
