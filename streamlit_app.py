import streamlit as st
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import io
import os
from scipy.signal import butter, filtfilt
from fpdf import FPDF
from pydub import AudioSegment
from pydub.playback import play
import tempfile

st.set_page_config(layout="wide")
st.title("Heart Sound Case Analyzer")

# 1. Record or Upload Audio
st.header("🎙️ Step 1: Record or Upload Heart Sound")
audio_data = None

recorded = st.file_uploader("Upload heart sound (.wav)", type=["wav"])
if recorded:
    audio_data, samplerate = sf.read(recorded)
    st.success("Audio uploaded successfully!")

# 2. Filter settings
st.header("🎚️ Step 2: Apply Filters and Adjustments")

lowcut = st.slider("Low Cut Frequency (Hz)", 10, 100, 20)
highcut = st.slider("High Cut Frequency (Hz)", 150, 1000, 150)
amp_factor = st.slider("Amplitude Multiplier", 1.0, 5.0, 1.5)
duration = st.slider("Clip Duration (sec)", 1, 10, 5)

# 3. Bandpass Filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low, high = lowcut / nyq, highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return b, a

def apply_bandpass_filter(data, lowcut, highcut, fs):
    b, a = butter_bandpass(lowcut, highcut, fs)
    y = filtfilt(b, a, data)
    return y

if audio_data is not None:
    st.subheader("📊 Waveform Visualization")

    # Show waveform
    fig, ax = plt.subplots()
    t = np.linspace(0, duration, int(duration * samplerate))
    ax.plot(t[:len(audio_data)], audio_data[:len(t)])
    ax.set_title("Original Audio Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

    # Filtered and amplified signal
    filtered_audio = apply_bandpass_filter(audio_data, lowcut, highcut, samplerate)
    filtered_audio *= amp_factor

    # Buttons to play audio
    st.subheader("🔊 Listen to Heart Sound")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Play Original"):
            temp_path = tempfile.mktemp(suffix=".wav")
            sf.write(temp_path, audio_data, samplerate)
            audio = AudioSegment.from_wav(temp_path)
            play(audio)
    with col2:
        if st.button("▶️ Play After Noise Reduction"):
            temp_path = tempfile.mktemp(suffix=".wav")
            sf.write(temp_path, filtered_audio, samplerate)
            audio = AudioSegment.from_wav(temp_path)
            play(audio)

# 4. Patient Details
st.header("🧑‍⚕️ Step 3: Enter Patient Details")
with st.form("patient_form"):
    pname = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=1, max_value=120)
    gender = st.radio("Gender", ["Male", "Female", "Other"])
    symptoms = st.text_area("Symptoms")
    submit = st.form_submit_button("Start Case")

# 5. Analysis Button and Save Case
if submit and audio_data is not None:
    st.success("Patient details saved.")
    st.header("📁 Step 4: Save and Export Case")

    if st.button("🧪 Analyse & Save Case"):
        case_data = {
            "Name": pname,
            "Age": age,
            "Gender": gender,
            "Symptoms": symptoms
        }

        # Save filtered audio
        filtered_path = f"{pname.replace(' ', '_')}_filtered.wav"
        sf.write(filtered_path, filtered_audio, samplerate)

        # PDF report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Heart Sound Report", ln=True, align="C")
        for key, value in case_data.items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
        pdf.output("case_report.pdf")

        st.success("Case analyzed and saved!")
        with open("case_report.pdf", "rb") as f:
            st.download_button("📄 Download Report", f, file_name="Heart_Report.pdf")

        with open(filtered_path, "rb") as f:
            st.download_button("🎧 Download Filtered Audio", f, file_name="Filtered_Audio.wav")

        st.info("Case saved to local cloud (simulation).")
