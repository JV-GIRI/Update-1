import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import librosa
import librosa.display
from io import BytesIO
import soundfile as sf

st.set_page_config(page_title="PCG Realtime Waveform Analyzer", layout="wide")
st.title("🔬 Real-time PCG Waveform & Noise Reduction")

uploaded_file = st.file_uploader("📤 Upload a PCG (.wav) file", type=["wav"])

if uploaded_file:
    st.audio(uploaded_file, format='audio/wav')

    # Load audio with librosa for more control
    y, sr = librosa.load(uploaded_file, sr=None)
    
    # Show original waveform
    st.subheader("🔈 Original PCG Waveform")
    fig, ax = plt.subplots(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr, ax=ax)
    ax.set(title="Original PCG Waveform")
    st.pyplot(fig)

    # --- Controls ---
    st.subheader("🎚 Waveform Controls")
    duration = st.slider("Select duration (seconds)", 1, int(len(y)/sr), 5)
    amplitude_factor = st.slider("Amplitude scaling", 0.1, 5.0, 1.0)

    # Slice waveform and scale
    y_trimmed = y[:sr * duration] * amplitude_factor

    # --- Basic Denoising using simple bandpass filter ---
    from scipy.signal import butter, filtfilt
    def bandpass_filter(data, sr, lowcut=25.0, highcut=400.0):
        nyquist = 0.5 * sr
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(2, [low, high], btype='band')
        return filtfilt(b, a, data)

    y_denoised = bandpass_filter(y_trimmed, sr)

    # --- Plot Denoised Waveform ---
    st.subheader("🔇 Denoised Waveform (Bandpass Filtered 25–400 Hz)")
    fig2, ax2 = plt.subplots(figsize=(10, 3))
    librosa.display.waveshow(y_denoised, sr=sr, ax=ax2, color='r')
    ax2.set(title="Filtered PCG Signal")
    st.pyplot(fig2)

    # Save denoised to buffer and allow download or playback
    st.subheader("▶️ Play Denoised Audio")
    buf = BytesIO()
    sf.write(buf, y_denoised, sr, format='WAV')
    st.audio(buf.getvalue(), format='audio/wav')
