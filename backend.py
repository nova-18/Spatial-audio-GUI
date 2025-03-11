import os
import numpy as np
from scipy.io import loadmat
from scipy.signal import resample
from scipy.spatial import KDTree
import soundfile as sf
import sounddevice as sd
import argparse


def play_stereo_audio(data, samplerate):
    # Ensure the shape is (samples, channels)
    if data.shape[0] == 2:
        data = data.T  # Transpose if channels are in rows

    sd.play(data, samplerate)
    sd.wait()

def load_mono_audio(file_path, target_samplerate=None):
    data, samplerate = sf.read(file_path)
    if len(data.shape) > 1:
        data = data.mean(axis=1)

    if target_samplerate and samplerate != target_samplerate:
        num_samples = int(round(float(len(data)) * target_samplerate / samplerate))
        data = resample(data, num_samples)
        samplerate = target_samplerate

    return np.array(data), samplerate
    
def save_stereo_audio(data, samplerate, file_path, file_name, file_type):
    if data.shape[0] == 2:
        data = data.T  
    full_path = os.path.abspath(os.path.join(file_path, f"{file_name}.{file_type}"))
    sf.write(full_path, data, samplerate)
    # print(f"Audio saved successfully to {file_path}")
    return full_path

def pad_zeros(arr, num_zeros):

    if num_zeros <= 0:
        return arr  # No padding needed

    padding = np.zeros(num_zeros, dtype=arr.dtype)
    
    return np.concatenate((arr, padding))

def FFT(sig):
    n = len(sig)

    if n == 1 :
        return sig

    w = np.exp(1j * 2 * np.pi / n) 
    sig_even, sig_odd = sig[::2], sig[1::2]
    y_even, y_odd = FFT(sig_even), FFT(sig_odd)
    y = [0] * n

    for i in range(n//2):
        y[i] = y_even[i] + (w**i) * y_odd[i]
        y[i + n//2] = y_even[i]  - (w**i) * y_odd[i]

    return y

def IFFT(sig):
    n = len(sig)

    if n == 1 :
        return sig

    w = (1/n) * np.exp(1j * (-2) * np.pi / n) 
    sig_even, sig_odd = sig[::2], sig[1::2]
    y_even, y_odd = IFFT(sig_even), IFFT(sig_odd)
    y = [0] * n

    for i in range(n//2):
        y[i] = y_even[i] + (w**i) * y_odd[i]
        y[i + n//2] = y_even[i]  - (w**i) * y_odd[i]

    return y

def convolve(sig1, sig2):
    ft_sig1 = np.fft.fft(sig1)
    ft_sig2 = np.fft.fft(sig2)
    prod = ft_sig1 * ft_sig2

    out = np.fft.ifft(prod)
    out = out.real.astype(np.float32)
    max_val = np.max(np.abs(out))
    if max_val != 0:  # Only divide if the max is not zero
        out /= max_val
    # out /= np.max(np.abs(out))
    return out

def get_chunks(audio, block_len, resp_len):
    N = block_len
    M = resp_len
    padded_audio = np.concatenate((np.zeros(M-1, dtype=audio.dtype),audio))

    step = N - M + 1

    num_chunks = (len(padded_audio) - N) // step + 1

    # Create the chunks
    chunks = [padded_audio[i:i + N] for i in range(0, num_chunks * step, step)]

    # Check if the last chunk needs padding
    if len(chunks[-1]) < N:
        chunks[-1] = np.pad(chunks[-1], (0, N - len(chunks[-1])))
    # Create the chunks
    # chunks = [padded_audio[i:i + N] for i in range(0, len(padded_audio), step)]

    # last_chunk_start = len(padded_audio) - ((len(padded_audio) - (M - 1)) % step)
    # if last_chunk_start < len(padded_audio):
    #     last_chunk = padded_audio[last_chunk_start:]
    #     if len(last_chunk) < N:
    #         last_chunk = np.pad(last_chunk, (0, N - len(last_chunk)))
    #     chunks.append(last_chunk)
    # Pad the last chunk if needed
    # if len(chunks[-1]) < N:
    #     chunks[-1] = np.pad(chunks[-1], (0, N - len(chunks[-1])))

    # chunks = [padded_audio[i:min(i+N,len(padded_audio))] for i in range(0,len(padded_audio),N - M + 1 )]

    # if len(chunks[-1]) <N:
    #     rem = N - len(chunks[-1])
    #     tem = np.array(list(chunks[-1]) + [0] * rem)
    #     chunks[-1] = tem
    return chunks

def process_chunks(chunk_arr,orig_len, filter_len):
    M = filter_len
    filtered = [chunk[M::] for chunk in chunk_arr]
    out = np.concatenate(filtered)
    out = out[:orig_len]
    return out
    
def create_hrtf_dict(azimuths, elevations, responses):
    hrtf_dict = {}
    for az, el, response in zip(azimuths, elevations, responses):
        hrtf_dict[(az, el)] = response
    return hrtf_dict

def extract_closest_hrtf(hrtf_dict, target_azimuth, target_elevation):
    
    available_points = np.array(list(hrtf_dict.keys()))
    tree = KDTree(available_points)

    _, index = tree.query([target_azimuth, target_elevation])
    closest_azimuth, closest_elevation = available_points[index]

    return hrtf_dict[(closest_azimuth, closest_elevation)]


def main():
    DOWNLOAD_FOLDER = "op_sound"
    UPLOAD_FOLDER = "in_sound"
    parser = argparse.ArgumentParser()
    parser.add_argument('--azimuth', type=float, required=True, help='Azimuth angle (0-360)')
    parser.add_argument('--elevation', type=float, required=True, help='Elevation angle (-90 to 90)')
    parser.add_argument('--file_name', type=str, required=True, help='name of the audio file')
    parser.add_argument('--download_type', type=str, choices=['wav', 'mp3', 'aac', 'ogg', 'mpeg'], required=True, help='Download file type')

    args = parser.parse_args()
    azi = args.azimuth
    ele = args.elevation
    audio_name = args.file_name
    download_type = args.download_type

   
    file = loadmat('res/ReferenceHRTF.mat')
    sample_rate = file['sampleRate'][0][0]
    hrtf_data = file['hrtfData']
    source_pos = file['sourcePosition']
    azimuth = source_pos[:,0]
    elevation = source_pos[:,1]

    left_channel = hrtf_data[:, :, 0] 
    right_channel = hrtf_data[:, :, 1]

    left_channel = left_channel.T
    right_channel = right_channel.T

    left_channel_dict = create_hrtf_dict(azimuths=azimuth, elevations=elevation, responses=left_channel)
    right_channel_dict = create_hrtf_dict(azimuths=azimuth, elevations=elevation, responses=right_channel)
    
    # print(f"left : {left_channel.shape}; right : {right_channel.shape}")

    lef_chan_resp = extract_closest_hrtf(hrtf_dict=left_channel_dict, target_azimuth=azi, target_elevation=ele)
    rig_chan_resp = extract_closest_hrtf(hrtf_dict=right_channel_dict, target_azimuth=azi, target_elevation=ele)

    lef_chan_resp = pad_zeros(lef_chan_resp,512 - len(lef_chan_resp))
    rig_chan_resp = pad_zeros(rig_chan_resp,512 - len(rig_chan_resp))


    audio_path = os.path.join(UPLOAD_FOLDER, f"{audio_name}")
    audio,sample_rate = load_mono_audio(audio_path, target_samplerate=sample_rate)

    chunks = get_chunks(audio = audio,block_len=512,resp_len=256)

    left_out , rig_out = [], []

    for chunk in chunks:
        out_lef = convolve(chunk, lef_chan_resp)
        out_rig = convolve(chunk, rig_chan_resp)
        left_out.append(out_lef)
        rig_out.append(out_rig)

    op_lef_chan = process_chunks(left_out, orig_len=len(audio), filter_len=256)
    op_rig_chan = process_chunks(rig_out, orig_len=len(audio), filter_len=256)

    stereo_audio = np.column_stack((op_lef_chan, op_rig_chan))
    
    # play_stereo_audio(stereo_audio, samplerate = sample_rate)        
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    out_path = save_stereo_audio(data = stereo_audio,samplerate = sample_rate, file_name='output',file_path=DOWNLOAD_FOLDER, file_type=download_type)
    print(out_path)    
    
    return out_path
if __name__ == "__main__":
    main()
