import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import scipy.io.wavfile as wav
from scipy.signal import butter, lfilter
from io import BytesIO
from fpdf import FPDF
import datetime

# -----------------------------
# Bandpass Filter Function
# -----------------------------
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# -----------------------------
# Save WAV file
# -----------------------------
def save_wav(filename, data, samplerate):
    wav.write(filename, samplerate, np.int16(data * 32767))

# -----------------------------
# Generate PDF Report
# -----------------------------
def generate_pdf(patient_name, diagnosis, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Heart Sound Analysis Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Patient Name: {patient_name}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, diagnosis)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    st.download_button("Download Report", data=pdf_output, file_name="heart_report.pdf")

# -----------------------------
# Main App
# -----------------------------
st.set_page_config(page_title="Heartbeat Analyzer", layout="centered")
st.title("🫀 Heartbeat Waveform Analyzer")

st.sidebar.header("🎚 Controls")
duration = st.sidebar.slider("Recording Duration (seconds)", 1, 10, 5)
samplerate = st.sidebar.selectbox("Sampling Rate", [22050, 44100], index=1)
amplify = st.sidebar.slider("Amplitude Scale", 0.5, 5.0, 1.0)
lowcut = st.sidebar.slider("Low Cut Frequency (Hz)", 10, 100, 20)
highcut = st.sidebar.slider("High Cut Frequency (Hz)", 100, 1000, 300)

if "recording" not in st.session_state:
    st.session_state.recording = None

# -----------------------------
# Patient Info
# -----------------------------
with st.expander("📝 Enter Patient Details"):
    patient_name = st.text_input("Patient Name")
    age = st.text_input("Age")
    gender = st.radio("Gender", ["Male", "Female", "Other"])

# -----------------------------
# Audio Recording
# -----------------------------
st.markdown("## 🎙️ Record Heart Sound")
if st.button("Start Recording"):
    st.info("Recording... Please remain silent.")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    st.session_state.recording = audio_data[:, 0]
    save_wav("original.wav", st.session_state.recording, samplerate)
    st.success("Recording complete!")

# -----------------------------
# Display Waveforms & Playback
# -----------------------------
if st.session_state.recording is not None:
    signal = st.session_state.recording * amplify
    time = np.linspace(0, len(signal) / samplerate, len(signal))

    st.subheader("📈 Original Waveform")
    fig1, ax1 = plt.subplots()
    ax1.plot(time, signal)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude")
    ax1.set_title("Original Heart Sound")
    st.pyplot(fig1)

    st.audio("original.wav")

    st.subheader("🧹 Noise Reduced Waveform")
    filtered_signal = bandpass_filter(signal, lowcut, highcut, samplerate)
    save_wav("filtered.wav", filtered_signal, samplerate)

    fig2, ax2 = plt.subplots()
    ax2.plot(time, filtered_signal, color='green')
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Amplitude")
    ax2.set_title("Filtered Heart Sound")
    st.pyplot(fig2)

    st.audio("filtered.wav")

    # Diagnosis (Basic)
    st.subheader("📋 Diagnosis")
    diagnosis = st.text_area("Enter analysis/notes here:")

    if st.button("Analyze and Save Case"):
        st.success("Case saved successfully.")
        if patient_name:
            generate_pdf(patient_name, diagnosis, "heart_report.pdf")
        else:
            st.warning("Please enter patient name to generate report.")
