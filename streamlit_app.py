import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# App title and style
st.set_page_config(page_title="Infrasonic Heart Sound Recorder", layout="centered")
st.title("🩺 AI-Powered Heart Sound Recorder")
st.markdown("Record, Analyze, and Save Reports with AI Diagnosis")

# Record audio
duration = st.slider("Select recording duration (seconds):", 2, 15, 5)
fs = 44100  # Sampling frequency

if st.button("🎙️ Start Recording"):
    st.info("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float64')
    sd.wait()
    st.success("Recording completed!")

    # Convert to WAV
    wav_io = io.BytesIO()
    wav.write(wav_io, fs, (recording * 32767).astype(np.int16))
    wav_data = wav_io.getvalue()

    # Plot waveform
    st.subheader("📊 Waveform")
    st.audio(wav_data, format='audio/wav')
    st.line_chart(recording)

    # Basic noise reduction (mean filter)
    filtered = recording - np.mean(recording)

    # Feature Extraction
    max_amp = np.max(np.abs(filtered))
    duration_sec = recording.shape[0] / fs

    st.write(f"🔍 Duration: `{duration_sec:.2f} sec`")
    st.write(f"📈 Max Amplitude: `{max_amp:.4f}`")

    # Simple AI diagnosis (placeholder logic)
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

    # Download report
    st.download_button("⬇️ Download Report", report.strip(), file_name="Heart_Report.txt")

    # Save to Google Sheet
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = {
            "type": "service_account",
            "client_email": st.secrets["gspread"]["email"],
            "private_key": st.secrets["gspread"]["private_key"],
            "token_uri": "https://oauth2.googleapis.com/token"
        }

        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key(st.secrets["gspread"]["sheet_id"]).sheet1

        sheet.append_row([now, f"{duration_sec:.2f}", f"{max_amp:.4f}", diagnosis])
        st.success("✅ Report saved to Google Sheet successfully!")
    except Exception as e:
        st.error(f"❌ Failed to save to Google Sheet: {e}")
