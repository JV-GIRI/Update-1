import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import sounddevice as sd
import soundfile as sf
import io
from pydub import AudioSegment
from reportlab.pdfgen import canvas
from scipy.signal import butter, lfilter

# Function to apply noise reduction using a simple high-pass filter
def reduce_noise(y, sr):
    b, a = butter(6, 100 / (0.5 * sr), btype='high')
    filtered = lfilter(b, a, y)
    return filtered

# Function to create PDF report
def create_pdf(patient_name, case_notes):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, f"Heart Sound Analysis Report")
    c.drawString(100, 780, f"Patient Name: {patient_name}")
    c.drawString(100, 760, f"Case Notes: {case_notes}")
    c.save()
    buffer.seek(0)
    return buffer

# Function to record audio
def record_audio(duration=5, fs=22050):
    st.info(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    sf.write("recorded.wav", audio, fs)
    return "recorded.wav"

# Streamlit UI
st.set_page_config(layout="centered")
st.title("🩺 Heart Sound Analyzer")

# Patient Details Section
with st.expander("👤 Add Patient Details"):
    patient_name = st.text_input("Patient Name")
    age = st.number_input("Age", 1, 120)
    notes = st.text_area("Case Notes")

# Record Heart Sound
if st.button("🎙️ Record Heart Sound"):
    filename = record_audio()
    st.success("Recording complete!")

# Upload audio
uploaded_file = st.file_uploader("Upload Heart Sound (.wav)", type=["wav"])
if uploaded_file is not None:
    y, sr = librosa.load(uploaded_file, sr=None)
    st.audio(uploaded_file, format="audio/wav")
    st.success("Original heart sound loaded.")

    # Adjust duration and amplitude
    duration_factor = st.slider("Adjust Playback Speed (Duration)", 0.5, 2.0, 1.0)
    amplitude_factor = st.slider("Adjust Amplitude", 0.5, 2.0, 1.0)

    y = librosa.effects.time_stretch(y, rate=1/duration_factor)
    y = y * amplitude_factor

    # Show waveform
    st.subheader("📈 Waveform")
    fig, ax = plt.subplots()
    librosa.display.waveshow(y, sr=sr, ax=ax)
    st.pyplot(fig)

    # Play adjusted sound
    st.subheader("🎧 Play Adjusted Heart Sound")
    wav_io = io.BytesIO()
    sf.write(wav_io, y, sr, format='wav')
    st.audio(wav_io, format='audio/wav')

    # Noise reduction
    if st.button("🧹 Apply Noise Reduction"):
        reduced_y = reduce_noise(y, sr)
        st.subheader("🔊 After Noise Reduction")
        reduced_io = io.BytesIO()
        sf.write(reduced_io, reduced_y, sr, format='wav')
        st.audio(reduced_io, format='audio/wav')
        st.success("Noise reduction applied.")

        # Save analyzed case
        if st.button("💾 Save Case & Generate PDF"):
            if patient_name:
                pdf = create_pdf(patient_name, notes)
                st.download_button("📥 Download PDF Report", pdf, file_name="Heart_Report.pdf")
                st.success("Case saved successfully!")
            else:
                st.error("Please enter patient name.")
