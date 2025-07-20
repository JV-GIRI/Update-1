# streamlit_app.py
import streamlit as st
import os
import uuid
import librosa
import numpy as np
import datetime
from tensorflow.keras.models import load_model
import json

# Load pre-trained model (Simulated placeholder)
@st.cache_resource
def load_cnn_model():
    model = load_model("model/rvhd_cnn_model.h5")  # replace with actual model path
    return model

model = load_cnn_model()

# Function to analyze audio and extract features
def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=None)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_db = librosa.power_to_db(mel_spec, ref=np.max)
    mel_db_resized = librosa.util.fix_length(mel_db, size=216, axis=1)
    return mel_db_resized[np.newaxis, ..., np.newaxis]  # Add batch and channel dims

# Simulated function to interpret model output
def interpret_prediction(pred):
    if pred[0][0] > 0.5:
        return "Possible Rheumatic Valvular Heart Disease (RVHD) detected"
    else:
        return "Normal heart sound pattern"

# Case history persistence
def save_case(case):
    if not os.path.exists("case_data"):
        os.makedirs("case_data")
    case_id = str(uuid.uuid4())
    with open(f"case_data/{case_id}.json", "w") as f:
        json.dump(case, f)

def load_all_cases():
    if not os.path.exists("case_data"):
        return []
    cases = []
    for file in os.listdir("case_data"):
        with open(os.path.join("case_data", file), "r") as f:
            cases.append(json.load(f))
    return cases

# Streamlit UI Tabs
st.set_page_config(page_title="PCG RVHD Analyzer", layout="centered")
tabs = st.tabs(["Upload & Analyze", "Case History"])

# Upload & Analyze tab
with tabs[0]:
    st.title("Phonocardiogram Analyzer with AI for RVHD")
    st.write("Upload a PCG (phonocardiogram) `.wav` or `.mp3` file to analyze for rheumatic valvular heart disease.")

    with st.form("UploadForm"):
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=1, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        uploaded_file = st.file_uploader("Upload PCG file", type=["wav", "mp3"])
        submitted = st.form_submit_button("Analyze")

    if submitted and uploaded_file:
        temp_filename = f"temp_audio_{uuid.uuid4()}.wav"
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.read())

        st.info("Analyzing audio file...")
        features = extract_features(temp_filename)
        prediction = model.predict(features)
        interpretation = interpret_prediction(prediction)
        hr_estimate = np.random.randint(60, 100)  # Simulated HR estimate

        st.success("Analysis Complete")
        st.markdown(f"**Heart Rate:** {hr_estimate} bpm")
        st.markdown(f"**Interpretation:** {interpretation}")

        os.remove(temp_filename)

        # Save case
        case = {
            "name": name,
            "age": age,
            "gender": gender,
            "filename": uploaded_file.name,
            "result": interpretation,
            "heart_rate": hr_estimate,
            "timestamp": str(datetime.datetime.now())
        }
        save_case(case)

# Case History tab
with tabs[1]:
    st.title("Past Analyzed Cases")
    cases = load_all_cases()
    if not cases:
        st.info("No previous cases found.")
    else:
        for case in sorted(cases, key=lambda x: x['timestamp'], reverse=True):
            with st.expander(f"{case['name']} | {case['age']} yrs | {case['timestamp']}"):
                st.write(f"**Gender:** {case['gender']}")
                st.write(f"**File:** {case['filename']}")
                st.write(f"**Heart Rate:** {case['heart_rate']} bpm")
                st.write(f"**Interpretation:** {case['result']}")
                
