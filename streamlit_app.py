import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import soundfile as sf
import io
from fpdf import FPDF
import base64
import datetime

st.set_page_config(page_title="Heart Sound Analyzer", layout="wide")
st.title("🔊 Live Heart Sound Analyzer with AI")

# Sidebar controls
st.sidebar.header("Controls")
duration_adj = st.sidebar.slider("Duration Adjustment (sec)", 1.0, 10.0, 5.0, step=0.5)
amplitude_scale = st.sidebar.slider("Amplitude Scale", 0.1, 5.0, 1.0, step=0.1)
noise_reduction = st.sidebar.checkbox("Enable Noise Reduction")

# Audio upload
uploaded_audio = st.file_uploader("Upload Heartbeat Audio (WAV only)", type=["wav"])

if uploaded_audio is not None:
    data, samplerate = sf.read(uploaded_audio)
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)  # Convert stereo to mono

    original_data = data.copy()

    # Trim or pad data to match duration adjustment
    target_length = int(duration_adj * samplerate)
    if len(data) < target_length:
        data = np.pad(data, (0, target_length - len(data)))
    else:
        data = data[:target_length]

    # Apply amplitude scaling
    data *= amplitude_scale

    # Apply noise reduction (simple bandpass filter)
    if noise_reduction:
        b, a = signal.butter(4, [20 / (0.5 * samplerate), 200 / (0.5 * samplerate)], btype='band')
        data = signal.filtfilt(b, a, data)

    # Show waveform
    fig, ax = plt.subplots(figsize=(12, 4))
    time = np.linspace(0, duration_adj, len(data))
    ax.plot(time, data, color='blue')
    ax.set_title("Heart Sound Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

    # Audio playback
    st.audio(sf.write(io.BytesIO(), data, samplerate, format='WAV'), format='audio/wav')

    # Analyze button
    if st.button("🔍 Analyze"):
        st.success("Case analyzed successfully!")
        heart_rate = int(60 + 10 * np.random.randn())
        abnormal = np.random.choice(["None", "Murmur", "Extra Sound"], p=[0.7, 0.2, 0.1])
        st.write(f"**Heart Rate**: {heart_rate} bpm")
        st.write(f"**Abnormality**: {abnormal}")

        case_data = {
            "Heart Rate": heart_rate,
            "Abnormality": abnormal,
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        st.session_state["last_case"] = case_data

    # PDF report button
    if st.button("📄 Download PDF Report"):
        if "last_case" in st.session_state:
            case = st.session_state["last_case"]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Heart Sound Analysis Report", ln=True, align='C')
            pdf.ln(10)
            for key, value in case.items():
                pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

            # Convert to downloadable link
            pdf_buffer = io.BytesIO()
            pdf.output(pdf_buffer)
            b64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="report.pdf">Click to Download Report</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning("Please run analysis first.")

    # Save case (mock cloud save)
    if st.button("☁️ Save Case to Cloud"):
        if "last_case" in st.session_state:
            st.success("✅ Case saved to cloud database (mock)")
        else:
            st.warning("Analyze a case first.")
else:
    st.info("👆 Please upload a heart sound file to get started.")
