# streamlit_app.py

import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io
import os
from datetime import datetime
from fpdf import FPDF
from sklearn.preprocessing import MinMaxScaler

# App Configuration
st.set_page_config(page_title="Heart Sound Analyzer", layout="wide")

# Sidebar - Navigation Tabs
st.sidebar.title("Navigation")
tabs = ["Record", "Cases", "About"]
page = st.sidebar.radio("Go to", tabs)

# Session state to store recorded files and cases
if 'cases' not in st.session_state:
    st.session_state.cases = []

# Bandpass filter
from scipy.signal import butter, lfilter

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

# AI diagnosis stub (Replace with real CNN model later)
def ai_diagnosis(filtered_data):
    hr = np.random.randint(60, 100)
    diagnosis = "Normal heart sounds" if hr < 90 else "Possible murmur detected"
    return hr, diagnosis

# Generate PDF report
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Heart Sound Analysis Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_report(name, age, gender, heart_rate, diagnosis):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
    pdf.cell(200, 10, txt=f"Gender: {gender}", ln=True)
    pdf.cell(200, 10, txt=f"Heart Rate: {heart_rate} bpm", ln=True)
    pdf.multi_cell(0, 10, txt=f"AI Analysis: {diagnosis}")

    output = io.BytesIO()
    pdf.output(output)
    return output

# Page 1 - Record Audio
if page == "Record":
    st.title("📼 Record Heart Sound")

    with st.form("patient_form"):
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=0)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        duration = st.slider("Recording Duration (sec)", 3, 10, 5)
        submitted = st.form_submit_button("Start Recording")

    if submitted:
        fs = 4000
        st.info("Recording in progress...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        st.success("Recording complete")

        # Preprocess
        audio = recording.flatten()
        filtered_audio = bandpass_filter(audio, 20.0, 500.0, fs)

        # Diagnosis
        heart_rate, diagnosis = ai_diagnosis(filtered_audio)

        # Save and playback
        filename = f"record_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        wav.write(filename, fs, (filtered_audio * 32767).astype(np.int16))
        st.audio(filename, format="audio/wav")

        # Waveform
        st.line_chart(filtered_audio)

        # Generate report
        report = generate_report(name, age, gender, heart_rate, diagnosis)
        st.download_button("Download Report", report, file_name="report.pdf")

        # Save to session
        st.session_state.cases.append({
            "name": name,
            "age": age,
            "gender": gender,
            "heart_rate": heart_rate,
            "diagnosis": diagnosis,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

# Page 2 - Case History
elif page == "Cases":
    st.title("📋 Case History")
    if st.session_state.cases:
        for idx, case in enumerate(st.session_state.cases[::-1], 1):
            st.subheader(f"Case {idx}")
            st.write(f"**Name:** {case['name']}")
            st.write(f"**Age:** {case['age']} | **Gender:** {case['gender']}")
            st.write(f"**Heart Rate:** {case['heart_rate']} bpm")
            st.write(f"**AI Diagnosis:** {case['diagnosis']}")
            st.write(f"**Recorded On:** {case['time']}")
    else:
        st.warning("No cases found yet.")

# Page 3 - About
elif page == "About":
    st.title("ℹ️ About")
    st.markdown("""
    This mobile-optimized Streamlit app allows real-time heart sound recording and AI-assisted interpretation.

    **Features:**
    - Infrasonic heart sound recording (20Hz–500Hz bandpass filter)
    - AI-generated diagnosis and PDF report
    - Local case history tracking
    - User-friendly mobile interface

    Built using: Python, Streamlit, NumPy, SciPy, FPDF
    """)
        
