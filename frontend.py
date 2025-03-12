import streamlit as st
import os
import shutil
import subprocess
import time
import sys

# Folders
UPLOAD_FOLDER = "in_sound"
DOWNLOAD_FOLDER = "op_sound"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def clear_folders():
    for folder in [UPLOAD_FOLDER, DOWNLOAD_FOLDER]:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove entire directory if present
            except Exception as e:
                st.error(f"Error deleting {file_path}: {e}")


if "initialized" not in st.session_state:
    st.session_state.initialized = True  # Mark session as initialized
    clear_folders()

st.title("Audio Processing GUI")


if "azimuth" not in st.session_state:
    st.session_state.azimuth = 0.0
if "elevation" not in st.session_state:
    st.session_state.elevation = 0.0

if "processed_file_path" not in st.session_state:
    st.session_state.processed_file_path = None

if "file_path" not in st.session_state:
    st.session_state.file_path = None

if "playing_audio" not in st.session_state:
    st.session_state.playing_audio = False

if "reset" not in st.session_state:
    st.session_state.reset = False

if st.session_state.reset :
    clear_folders() 
    

# Callbacks to update session state when input changes
def update_azimuth():
    st.session_state.azimuth = st.session_state["azimuth_input"]

def update_elevation():
    st.session_state.elevation = st.session_state["elevation_input"]

# User inputs with session state and on_change callbacks
azimuth = st.number_input(
    "Azimuth (0 to 360)",
    min_value=0.0,
    max_value=360.0,
    value=st.session_state.azimuth,
    step=0.1,
    format="%.2f",
    key="azimuth_input",
    on_change=update_azimuth
)
elevation = st.number_input(
    "Elevation (-90 to 90)",
    min_value=-90.0,
    max_value=90.0,
    value=st.session_state.elevation,
    step=0.1,
    format="%.2f",
    key="elevation_input",
    on_change=update_elevation
)
# File uploader
uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])

# if uploaded_file is None and os.listdir(UPLOAD_FOLDER):
#     for file in os.listdir(UPLOAD_FOLDER):
#         os.remove(os.path.join(UPLOAD_FOLDER, file))
#     st.session_state.file_path = None
#     # st.write("Upload folder cleared as file was removed.")

# Download type selector
download_type = st.selectbox(
    "Select download type",
    ["wav", "ogg", "mp3", "mpeg", "aac"]
)

# Save uploaded file
# file_path = None
if uploaded_file:
    st.session_state.file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(st.session_state.file_path, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

# Placeholder for processed file path

# Run button
if st.button("Run Audio Processing"):
    if st.session_state.file_path:
        file_name = os.path.basename(st.session_state.file_path)  # Extract just the filename like '123.wav'
        result = subprocess.run(
            [
                f"{sys.executable}", "backend.py",
                "--azimuth", str(azimuth),
                "--elevation", str(elevation),
                "--file_name", file_name,
                "--download_type", download_type
            ],
            capture_output=True,
            text=True
        )
        # st.write(f"STDOUT: {result.stdout}")
        # st.write(f"STDERR: {result.stderr}")

        # Save the processed file path to session state
        st.session_state.processed_file_path = result.stdout.strip()
        # st.write(f"Backend returned path: {repr(st.session_state.processed_file_path)}")
        # st.write(f"Files in download folder: {os.listdir(DOWNLOAD_FOLDER)}")

        if result.returncode != 0:
            st.error(f"Error in processing:\n{result.stderr}")
        elif os.path.exists(st.session_state.processed_file_path):
            st.success("Processing complete!")
        else:
            st.error("Processing finished, but file not found. Please refresh.")
            st.session_state.processed_file_path = None
    else:
        st.warning("Please upload a file first!")

# Play sound button
if not st.session_state.playing_audio:
    if st.button("▶️ Play Processed Sound"):
        if st.session_state.processed_file_path and os.path.exists(st.session_state.processed_file_path):
            st.session_state.playing_audio = True  # Hide button and show player
            st.rerun()  # Refresh the UI
        else:
            st.error("Processed file not found. Please refresh or reprocess.")

# If button is clicked, show the audio player
if st.session_state.playing_audio:
    if st.session_state.processed_file_path and os.path.exists(st.session_state.processed_file_path):
        # Audio player for processed sound
        st.audio(st.session_state.processed_file_path, format="audio/wav")
        
        # Stop playback button
        if st.button("⏹ Stop Playback"):
            st.session_state.playing_audio = False  # Reset to show play button again
            st.rerun()
    else:
        st.error("Processed file not found. Please refresh or reprocess.")
    
# Download Button
if st.button("Download Processed File"):
    # st.write(f"Trying to download: {repr(st.session_state.processed_file_path)}")
    # st.write(f"File exists at download time: {os.path.exists(st.session_state.processed_file_path) if st.session_state.processed_file_path else False}")
    # st.write(f"Files in download folder: {os.listdir(DOWNLOAD_FOLDER)}")

    if st.session_state.processed_file_path and os.path.exists(st.session_state.processed_file_path):
        # Simulated download progress bar
        progress = st.progress(0)
        if progress:  # Make sure progress bar was created successfully
            for percent_complete in range(100):
                time.sleep(0.01)  # Simulate download time
                progress.progress(percent_complete + 1)

        # Actual file download
        with open(st.session_state.processed_file_path, "rb") as f:
            st.download_button(
                label="Download File",
                data=f,
                file_name=os.path.basename(st.session_state.processed_file_path),
                mime="audio/" + download_type
            )
    else:
        st.error("Error in processing, please refresh.")

# Reset Button
# Reset Button
