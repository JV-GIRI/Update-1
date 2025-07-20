import streamlit as st
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import datetime
import json
import os

st.set_page_config(page_title="RVHD AI PCG Analyzer", layout="wide")

# --------- PATIENT INFORMATION ----------
with st.expander("🧑‍⚕️ Enter Patient Details to Start Analysis", expanded=True):
    name = st.text_input("Full Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    patient_id = st.text_input("Patient ID")
    symptoms = st.text_area("Symptoms")
    notes = st.text_area("Clinical Notes")

    patient_ready = st.button("✅ Save & Start PCG Analysis")

# --------- AUDIO FILE UPLOAD ---------
st.markdown("### 🎧 Upload PCG (.wav) or Record Below:")
col1, col2 = st.columns(2)

with col1:
    audio_file = st.file_uploader("Upload .wav File", type=["wav"])

with col2:
    record_audio = st.button("🎙️ Record (Infrasonic Recorder)")

# --------- FUNCTION TO PLOT AUDIO WAVEFORM ---------
def plot_waveform(audio, samplerate):
    duration = len(audio) / samplerate
    time = np.linspace(0., duration, len(audio))
    plt.figure(figsize=(10, 3))
    plt.plot(time, audio, color='green')
    plt.title("Filtered PCG Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    st.pyplot(plt)

# --------- SIMULATED AI INTERPRETATION ---------
def ai_analysis(audio):
    # Simulated placeholder logic
    duration = len(audio)
    if duration % 2 == 0:
        return "Likely Rheumatic Mitral Stenosis"
    else:
        return "Likely Normal or Innocent Murmur"

# --------- PROCESS AFTER PATIENT INFO SAVED ---------
if patient_ready:
    if not audio_file and not record_audio:
        st.warning("Upload or record a PCG file first.")
    else:
        # Load audio
        if audio_file:
            audio, sr = sf.read(audio_file)
        else:
            # Simulated recording fallback
            audio = np.random.randn(5000) * 0.02
            sr = 4000

        st.success("✅ Audio received. Displaying waveform:")
        plot_waveform(audio, sr)

        result = ai_analysis(audio)
        st.subheader("🧠 AI Analysis Result:")
        st.success(result)

        # --------- Save Patient + Result Data ---------
        save_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "patient_id": patient_id,
            "symptoms": symptoms,
            "notes": notes,
            "analysis": result,
            "timestamp": str(datetime.datetime.now())
        }

        os.makedirs("saved_data", exist_ok=True)
        with open(f"saved_data/{patient_id}_{name.replace(' ', '_')}.json", "w") as f:
            json.dump(save_data, f, indent=4)

        st.info("📁 Patient info + PCG report saved for future use.")
