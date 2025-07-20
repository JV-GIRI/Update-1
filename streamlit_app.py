import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Streamlit app config
st.set_page_config(page_title="Infrasonic Heart Sound Recorder", layout="centered")
st.title("🩺 AI-Powered Heart Sound Recorder")
st.markdown("Record, Analyze, and Save Reports with AI Diagnosis")

# Recording settings
duration = st.slider("Select recording duration (seconds):", 2, 15, 5)
fs = 44100  # Sampling frequency

# Record audio on button click
if st.button("🎙️ Start Recording"):
    st.info("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float64')
    sd.wait()
    st.success("Recording completed!")

    # Convert to WAV
    wav_io = io.BytesIO()
    wav.write(wav_io, fs, (recording * 32767).astype(np.int16))
    wav_data = wav_io.getvalue()

    # Waveform and playback
    st.subheader("📊 Waveform")
    st.audio(wav_data, format='audio/wav')
    st.line_chart(recording)

    # Noise reduction
    filtered = recording - np.mean(recording)

    # Feature Extraction
    max_amp = np.max(np.abs(filtered))
    duration_sec = recording.shape[0] / fs

    st.write(f"🔍 Duration: `{duration_sec:.2f} sec`")
    st.write(f"📈 Max Amplitude: `{max_amp:.4f}`")

    # AI Diagnosis
    if max_amp > 0.2:
        diagnosis = "Abnormal heart sound detected. Possible murmur."
    else:
        diagnosis = "Normal heart sound pattern detected."

    st.subheader("🧠 AI Diagnosis")
    st.info(diagnosis)

    # Prepare report
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""
    🗓️ Recorded at: {now}
    📌 Duration: {duration_sec:.2f} seconds
    📌 Max Amplitude: {max_amp:.4f}
    🤖 AI Diagnosis: {diagnosis}
    """

    st.text_area("📝 Diagnosis Report", report.strip(), height=200)

    # Download Report
    st.download_button("⬇️ Download Report", report.strip(), file_name="Heart_Report.txt")

    # Save to Google Sheet
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = {
            "type": "service_account",
            "project_id": st.secrets["gspread"]["project_id"],
            "private_key_id": st.secrets["gspread"]["private_key_id"],
            "private_key": st.secrets["gspread"]["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["gspread"]["client_email"],
            "client_id": st.secrets["gspread"]["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": st.secrets["gspread"]["client_x509_cert_url"]
        }

        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gc = gspread.authorize(credentials)

        # Google Sheet key from link
        sheet_key = "1i8yt5bEct6WIB4R-gwjp0NsElDXUvFoDS8_GYcb5SW0"
        sheet = gc.open_by_key(sheet_key).sheet1

        sheet.append_row([now, f"{duration_sec:.2f}", f"{max_amp:.4f}", diagnosis])
        st.success("✅ Report saved to Google Sheet successfully!")
    except Exception as e:
        st.error(f"❌ Failed to save to Google Sheet: {e}")
