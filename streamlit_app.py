import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import librosa
import librosa.display
from io import BytesIO
import soundfile as sf
from scipy.signal import butter, filtfilt

# Page configuration
st.set_page_config(page_title="PCG Realtime Waveform Analyzer", layout="wide")

# Sidebar for patient info
with st.sidebar:
    st.header("👤 Patient Information")
    patient_name = st.text_input("Name")
    patient_id = st.text_input("Patient ID")
    patient_age = st.number_input("Age", min_value=0, max_value=120, step=1)
    patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    
    save_info = st.button("💾 Save Patient + Analysis Info")
    
    # Infrasonic record link (via RedVox app or manual instruction)
    st.markdown("📡 **Infrasonic Recorder**")
    st.markdown("[🎙️ Record Using RedVox App](https://redvox.io/)")

    if save_info:
        st.session_state['patient_data'] = {
            "Name": patient_name,
            "ID": patient_id,
            "Age": patient_age,
            "Gender": patient_gender,
            "PCG_Analyzed": st.session_state.get("last_pcg_file", "Not Uploaded")
        }
        st.success("✅ Patient info & PCG analysis saved!")

# Title
st.title("🔬 Real-time PCG Waveform & Noise Reduction")

# Upload section
st.markdown("### 📤 Upload a PCG (.wav) file")
uploaded_file = st.file_uploader("Choose a PCG WAV file", type=["wav"])

# Audio Processing
if uploaded_file:
    st.session_state["last_pcg_file"] = uploaded_file.name  # Save session
    st.audio(uploaded_file, format='audio/wav')

    # Load audio with librosa
    y, sr = librosa.load(uploaded_file, sr=None)

    # Display original waveform
    st.subheader("🔈 Original PCG Waveform")
    fig, ax = plt.subplots(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr, ax=ax)
    ax.set(title="Original PCG Waveform")
    st.pyplot(fig)

    # Controls
    st.subheader("🎚 Waveform Controls")
    duration = st.slider("Select duration (seconds)", 1, int(len(y) / sr), 5)
    amplitude_factor = st.slider("Amplitude scaling", 0.1, 5.0, 1.0)

    # Slice and scale
    y_trimmed = y[:sr * duration] * amplitude_factor

    # Bandpass filter
    def bandpass_filter(data, sr, lowcut=25.0, highcut=400.0):
        nyquist = 0.5 * sr
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(2, [low, high], btype='band')
        return filtfilt(b, a, data)

    y_denoised = bandpass_filter(y_trimmed, sr)

    # Plot denoised waveform
    st.subheader("🔇 Denoised Waveform (Bandpass Filtered 25–400 Hz)")
    fig2, ax2 = plt.subplots(figsize=(10, 3))
    librosa.display.waveshow(y_denoised, sr=sr, ax=ax2, color='r')
    ax2.set(title="Filtered PCG Signal")
    st.pyplot(fig2)

    # Play filtered audio
    st.subheader("▶️ Play Denoised Audio")
    buf = BytesIO()
    sf.write(buf, y_denoised, sr, format='WAV')
    st.audio(buf.getvalue(), format='audio/wav')

    # Optionally show stored info
    if 'patient_data' in st.session_state:
        st.markdown("---")
        st.markdown("### 📄 Saved Patient Information")
        st.json(st.session_state['patient_data'])
