import streamlit as st
import numpy as np
import soundfile as sf
import io
from scipy.signal import butter, lfilter
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import os

# ---------- Bandpass Filter Function ----------
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    return butter(order, [low, high], btype='band')

def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# ---------- UI Starts ----------
st.title("🩺 PCG Analyzer with Bandpass Filtering")
st.markdown("🎧 **Supports Bluetooth or Stethoscope Mic**")

# ---------- Patient Info ----------
with st.expander("➕ Enter Patient Details"):
    patient_name = st.text_input("Patient Name")
    patient_id = st.text_input("Patient ID")
    age = st.number_input("Age", 0, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    mic_type = st.selectbox("Mic Used", ["Stethoscope", "Bluetooth Mic"])

# ---------- Upload or Record ----------
st.subheader("📤 Upload or Record Heart Sound (.wav)")

uploaded_file = st.file_uploader("Upload .wav file", type=["wav"])

record_button = st.button("🔴 Start Recording (Use External Tool)")

if record_button:
    st.info("Use mobile app or audio recorder to record and upload .wav")

# ---------- Process File ----------
if uploaded_file:
    with st.spinner("Processing audio..."):
        # Read the audio
        audio_data, samplerate = sf.read(uploaded_file)
        duration = len(audio_data) / samplerate

        st.success(f"✅ Audio Loaded | Duration: {duration:.2f} sec | Sample Rate: {samplerate} Hz")

        # Play Original
        st.audio(uploaded_file, format='audio/wav', start_time=0, label="🔊 Original Sound")

        # Filter
        filtered = apply_bandpass_filter(audio_data, 20, 150, samplerate)

        # Save filtered audio
        temp_wav = io.BytesIO()
        sf.write(temp_wav, filtered, samplerate, format='WAV')
        temp_wav.seek(0)

        st.audio(temp_wav, format='audio/wav', start_time=0, label="🔊 Filtered Sound")

        # Download Option
        st.download_button("⬇️ Download Filtered Sound", data=temp_wav, file_name="filtered_heart_sound.wav")

        # Show waveform (optional)
        st.line_chart(filtered[:5000])  # Display 1st second only

# ---------- Save Patient Case ----------
if st.button("📁 Save Case"):
    if not patient_name or not uploaded_file:
        st.warning("Please enter patient details and upload audio.")
    else:
        st.success(f"✅ Case Saved for {patient_name} (ID: {patient_id})")
