Project: Spatial Audio GUI
===========================

Description:
-------------
This project is an audio processing application built with Streamlit. It uses a backend script to process audio files based on user-defined parameters (azimuth and elevation) and a frontend for user interaction.

Online interface :
-------------
A live deployment of this project is available at the following link , no install required only a live internet connection is needed :
https://spatial-audio-gui-demo.streamlit.app/

For offline interface please follow the following steps for install on linux(debian) / mac  or  windows:
-------------------------------------------------------------------------------------------------
(IMP note : The project is created and tested in Linux (Ubuntu-24.04 LTS), there might be some version and package conflicts possible for offline working in windows and mac os hence, Online interface is provided and requested to be used as it is tested across the platforms)

Requirements:
--------------
- Python 3.12 (Ensure you have Python 3.12 installed on your system)
- Python dependencies are listed in "requirements.txt"
- System-level packages (e.g., PortAudio for sounddevice) are listed in "packages.txt"
- Git (optional, if you plan to clone the repository)

Setup Instructions:
--------------------

### For Linux/macOS:
1. **Clone the repository:**
git clone https://github.com/nova-18/Spatial-audio-gui.git
cd your-repo


2. **Create a virtual environment using Python 3.12:**
python3.12 -m venv .venv


3. **Activate the virtual environment:**
- On macOS/Linux:
  ```
  source .venv/bin/activate
  ```

4. **Install Python dependencies:**
pip install -r requirements.txt


5. **Install system-level dependencies:**
- For Ubuntu/Debian-based systems:
  ```
  xargs sudo apt-get install -y < packages.txt
  ```
- For macOS (using Homebrew):
  ```
  brew install portaudio
  ```
(Ensure you install any other dependencies mentioned in packages.txt.)

6. **Run the application:**
streamlit run frontend.py


### For Windows:
1. **Clone the repository:**
git clone https://github.com/nova-18/Spatial-audio-gui.git
cd your-repo

2. **Create a virtual environment using Python 3.12:**
python3.12 -m venv .venv

3. **Activate the virtual environment:**
- For Command Prompt:
  ```
  .venv\Scripts\activate
  ```
- For PowerShell:
  ```
  .venv\Scripts\Activate.ps1
  ```

4. **Install Python dependencies:**
pip install -r requirements.txt


5. **Install system-level dependencies:**
Windows does not use apt-get, so you’ll need to install the PortAudio library manually. You can:
- Download and install PortAudio from its official website: http://www.portaudio.com/download.html
- Or use a package manager like Chocolatey:
  ```
  choco install portaudio
  ```
(Ensure that the PortAudio binaries are accessible by your system so that the sounddevice module can find them.)

6. **Run the application:**
streamlit run frontend.py

Usage:
-------
- Open your web browser at the URL provided by Streamlit.
- Upload an audio file using the interface.
- Set the desired azimuth and elevation values.
- Click the "Run Audio Processing" button to process the audio.
- Use the provided buttons to play or download the processed audio.

Troubleshooting:
-----------------
- **Python Version:** Ensure you are using Python 3.12.
- **Virtual Environment:** Confirm your virtual environment is activated before installing dependencies or running the app.
- **System Dependencies:** Verify that system-level packages are installed according to your OS-specific instructions.
- **Logs:** Check for any error messages in your terminal or deployment logs if issues persist.


License:
---------
[Include your license information here]

