import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
import os
import json
from datetime import datetime

# Directory to save patient data
os.makedirs("patients", exist_ok=True)

st.set_page_config(page_title="RVHD Detection - AI Assisted", layout="wide")
st.title("🩺 AI-Based Rheumatic Valvular Heart Disease (RVHD) Detector")

# Tabs
menu = st.sidebar.radio("Navigation", ["Upload & Analyze", "Case History"])

if menu == "Upload & Analyze":
    st.header("📤 Upload Phonocardiogram (PCG) Audio")

    with st.form("patient_form"):
        name = st.text_input("Patient Name")
        age = st.number_input("Age", 0, 120, 45)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        file = st.file_uploader("Upload .wav file of heart sound", type=["wav"])
        submit = st.form_submit_button("Analyze")

    if submit and file is not None:
        y, sr = librosa.load(file, sr=4000)
        duration = librosa.get_duration(y=y, sr=sr)

        # --- Simulated AI Interpretation ---
        heart_rate = int(60 / (duration / 6))  # crude est.

        # Frequency analysis
        freqs = np.abs(librosa.stft(y))
        avg_power = freqs.mean()

        if heart_rate > 100:
            condition = "Tachycardia detected"
        elif heart_rate < 50:
            condition = "Bradycardia detected"
        else:
            condition = "Heart rate normal"

        if avg_power > 25:
            rvhd_findings = "Possible Mitral Regurgitation (holosystolic murmur)"
        elif avg_power < 10:
            rvhd_findings = "Possible Mitral Stenosis (diastolic rumble)"
        else:
            rvhd_findings = "Normal or unclear pathology"

        # --- Display Results ---
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🫀 Heart Sound Waveform")
            fig, ax = plt.subplots()
            librosa.display.waveshow(y, sr=sr, ax=ax)
            ax.set_title("Phonocardiogram Waveform")
            st.pyplot(fig)

        with col2:
            st.subheader("📄 AI Interpretation Report")
            st.markdown(f"**Patient:** {name}\n")
            st.markdown(f"**Age / Gender:** {age} / {gender}")
            st.markdown(f"**Heart Rate:** {heart_rate} bpm")
            st.markdown(f"**Condition:** {condition}")
            st.markdown(f"**RVHD Suspicion:** {rvhd_findings}")

        # Save case
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_record = {
            "name": name,
            "age": age,
            "gender": gender,
            "heart_rate": heart_rate,
            "condition": condition,
            "rvhd_findings": rvhd_findings,
            "timestamp": timestamp
        }
        with open(f"patients/{name}_{timestamp}.json", "w") as f:
            json.dump(patient_record, f)

        st.success("✅ Case saved and AI report generated.")

elif menu == "Case History":
    st.header("📁 Past Patient Cases")
    files = sorted(os.listdir("patients"), reverse=True)

    if not files:
        st.info("No patient records available.")
    else:
        for file in files:
            with open(f"patients/{file}") as f:
                data = json.load(f)
                with st.expander(f"🗂️ {data['name']} | {data['timestamp']}"):
                    st.markdown(f"**Age / Gender:** {data['age']} / {data['gender']}")
                    st.markdown(f"**Heart Rate:** {data['heart_rate']} bpm")
                    st.markdown(f"**Condition:** {data['condition']}")
                    st.markdown(f"**RVHD Suspicion:** {data['rvhd_findings']}")
                    
