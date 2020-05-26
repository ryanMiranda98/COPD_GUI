import time
import zmq
from modules.constants import *
import librosa

socket=None

def init_zmq():
    global context
    global socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:{}".format(FEATURE_PORT))

FIX_AUDIO_LENGTH=20
sample_rate=22040


def extract_features(series, n_count=40):

    if n_count != 40:
        print("Values other than 40 for n_count can cause problems with the model. Value = {}".format(n_count))

    # Make every series the same length
    series = librosa.util.fix_length(series, size = FIX_AUDIO_LENGTH * sample_rate)

    # Duration of audio = no. of samples / sample_rate
    length = len(series) / float(sample_rate)

    # print("Progress: {}/{} (Omitted: {}) | {}\nSeries_Length = {} | sample_rate = {} | Audio Length: {}".format(count + omitted, len(audio_paths), omitted, clip, len(series), sample_rate, length))
    
    # TODO: Use the features 
    mfcc = librosa.feature.mfcc(y=series, n_mfcc=n_count)
    mel = librosa.feature.melspectrogram(y=series, n_mels=n_count)
    c_stft = librosa.feature.chroma_stft(y=series, n_chroma=n_count)
    c_cqt = librosa.feature.chroma_cqt(y=series, n_chroma=n_count)
    c_cens = librosa.feature.chroma_cens(y=series, n_chroma=n_count)

    return mfcc, mel, c_stft, c_cqt, c_cens


def init_extraction(file_name):
    series, _ = librosa.load(file_name, res_type='kaiser_fast')

    # Extract 5 features
    mfcc, mel, c_stft, c_cqt, c_cens = extract_features(series)

    response = {
        'file_name': file_name,
        'mfcc': mfcc,
        'melspectrogram': mel,
        'chroma_stft': c_stft,
        'chroma_cqt':c_cqt,
        'chroma_cens': c_cens
    }

    if socket is not None:
        socket.send_pyobj(response)

    return response






if __name__ == "__main__":
    init_zmq()

    while True:
        #  Wait for next request from client
        audio_file_name = socket.recv_string()
        print("Received request: {}: Type: {}".format(audio_file_name, type(audio_file_name)))

        init_extraction(audio_file_name)