import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import noisereduce as nr
from fpdf import FPDF
import os
import datetime
import json

st.set_page_config(page_title="Smart PCG AI Tool", layout="centered")

# File to store case history
CASE_HISTORY_FILE = "case_history.json"

# ---------- BANDPASS FILTER ----------
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    return butter(order, [low, high], btype='band')

def bandpass_filter(data, lowcut=20.0, highcut=500.0, fs=4000.0, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    return lfilter(b, a, data)

# ---------- RECORD AUDIO ----------
def record_audio(duration=5, fs=4000):
    st.info("Recording started... Please keep quiet.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return np.squeeze(recording)

# ---------- PLOT WAVEFORM ----------
def plot_waveform(data, fs, title):
    fig, ax = plt.subplots(figsize=(10, 2))
    time = np.linspace(0, len(data)/fs, num=len(data))
    ax.plot(time, data)
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

# ---------- AI DIAGNOSIS (Mockup) ----------
def ai_diagnose(filtered_data, fs):
    heart_rate = int(60 + (np.random.rand() * 20))  # mockup heart rate
    diagnosis = "Normal heart sounds" if heart_rate < 90 else "Murmur detected"
    return heart_rate, diagnosis

# ---------- SAVE REPORT ----------
def generate_pdf_report(patient_data, heart_rate, diagnosis, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, "PCG AI Diagnosis Report", ln=True, align='C')
    pdf.ln(10)

    for key, value in patient_data.items():
        pdf.cell(200, 10, f"{key}: {value}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, f"Heart Rate: {heart_rate} bpm", ln=True)
    pdf.cell(200, 10, f"AI Diagnosis: {diagnosis}", ln=True)

    pdf.output(filename)

# ---------- SAVE CASE LOCALLY ----------
def save_case(case):
    if not os.path.exists(CASE_HISTORY_FILE):
        with open(CASE_HISTORY_FILE, 'w') as f:
            json.dump([], f)
    with open(CASE_HISTORY_FILE, 'r') as f:
        cases = json.load(f)
    cases.append(case)
    with open(CASE_HISTORY_FILE, 'w') as f:
        json.dump(cases, f)

def load_cases():
    if os.path.exists(CASE_HISTORY_FILE):
        with open(CASE_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

# ========== MAIN UI ==========

st.title("🩺 PCG Sound Analyzer with AI")

# View all cases
if st.button("📂 View Previous Cases"):
    all_cases = load_cases()
    if not all_cases:
        st.warning("No cases found.")
    else:
        for idx, c in enumerate(all_cases[::-1]):
            with st.expander(f"Case {len(all_cases)-idx} - {c['Patient Name']} ({c['Date']})"):
                st.write(c)
                st.download_button("📥 Download Report", data=open(c["Report File"], "rb"), file_name=os.path.basename(c["Report File"]))

st.subheader("📋 Enter Patient Details")
with st.form("patient_form"):
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=1, max_value=120, value=25)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    submit = st.form_submit_button("✅ Start Case")

if submit:
    st.session_state["patient"] = {"Patient Name": name, "Age": age, "Gender": gender, "Date": str(datetime.date.today())}

if "patient" in st.session_state:
    st.success("Patient registered: " + st.session_state["patient"]["Patient Name"])

    duration = st.slider("Recording Duration (seconds)", 3, 10, 5)
    if st.button("🎙️ Record Heart Sound"):
        raw_audio = record_audio(duration)
        fs = 4000

        st.audio(raw_audio.tobytes(), format="audio/wav", start_time=0)
        plot_waveform(raw_audio, fs, "Raw Heart Sound")

        st.subheader("🎧 Noise Reduction & Bandpass Filtering")
        reduced_noise = nr.reduce_noise(y=raw_audio, sr=fs)
        filtered_audio = bandpass_filter(reduced_noise, fs=fs)
        st.audio(filtered_audio.tobytes(), format="audio/wav", start_time=0)
        plot_waveform(filtered_audio, fs, "Filtered Heart Sound")

        st.subheader("🧠 AI Interpretation")
        hr, diag = ai_diagnose(filtered_audio, fs)
        st.metric("Estimated Heart Rate", f"{hr} bpm")
        st.success(f"AI Diagnosis: {diag}")

        # Save report
        fname = f"report_{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        generate_pdf_report(st.session_state["patient"], hr, diag, fname)

        # Save to history
        case_info = st.session_state["patient"].copy()
        case_info.update({"Heart Rate": hr, "AI Diagnosis": diag, "Report File": fname})
        save_case(case_info)

        with open(fname, "rb") as f:
            st.download_button("📄 Download PDF Report", data=f, file_name=fname)

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit · Bluetooth mic compatible · Designed for mobile use")
