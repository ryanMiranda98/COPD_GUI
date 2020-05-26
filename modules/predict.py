import zmq
from modules.constants import *
import logging
import os
import numpy as np


from tensorflow.keras.models import load_model


def init_zmq():
    global context
    global socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:{}".format(PREDICT_PORT))


def predict(prediction_request):
    """
    Expects a dict with keys `feature_name` and `content`
    """

    feature_type = prediction_request['feature_type']

    if feature_type not in [MFCC, C_CENS, C_CQT, C_STFT, MEL]:
        raise Exception('Invalid Feature type for prediction: {}'.format(feature_type))

    model = model_from_feature[feature_type]

    prediction = np.argmax(model.predict([np.reshape(prediction_request['content'], (1, *prediction_request['content'].shape, 1))]), axis=1)[0]

    predicted_class = "COPD" if prediction == 0 else "non-COPD"

    print("Prediction for type {} = {}".format(feature_type, predicted_class))

    socket.send_pyobj({
        'model': feature_type,
        'class': predicted_class
    })




def load_model_from_file(type=None):
    model_dir = 'saved_models'

    if type not in [MFCC, C_CENS, MEL, C_CQT, C_STFT]:
        raise Exception("Invalid type.")

    concerned_dir = os.path.join(model_dir, feature_model_dirs[type])

    dir_contents = os.listdir(concerned_dir)

    if len(dir_contents) == 0:
        raise Exception("No model found in {}".format(concerned_dir))


    # Damn Underscores fuck you.
    conversion_dict = {
        MFCC: 'mfcc',
        MEL: 'melspectrogram',
        C_CENS: 'chroma_cens',
        C_CQT: 'chroma_cqt',
        C_STFT: 'chroma_stft'
    }


    model_numbers = [int(name.strip().split(conversion_dict[type])[1].split(".")[0].split("_")[2]) for name in dir_contents]

    model_name = feature_model_dirs[type] + "_" + "model_" + str(sorted(model_numbers)[-1]) + ".h5"

    # list_dir = [f.lower() for f in dir_contents]   # Convert to lower case
    
    print('Found best model "{}" for type: {}'.format(model_name, feature_model_dirs[type]))

    model_path = os.path.join(concerned_dir, model_name)

    print("Loading {} model...".format(type))
    model = load_model(model_path)

    return model



if __name__ == "__main__":
    global mfcc_model
    global mel_model
    global chroma_cens_model
    global chroma_cqt_model
    global chroma_stft_model

    mfcc_model = load_model_from_file(MFCC)
    mel_model = load_model_from_file(MEL)
    chroma_cens_model = load_model_from_file(C_CENS)
    chroma_cqt_model = load_model_from_file(C_CQT)
    chroma_stft_model = load_model_from_file(C_STFT)

    global model_from_feature
    model_from_feature = {
        MFCC: mfcc_model,
        MEL: mel_model,
        C_STFT: chroma_stft_model,
        C_CQT: chroma_cqt_model,
        C_CENS: chroma_cens_model
    }

    init_zmq()

    while True:
        #  Wait for next request from client
        prediction_request = socket.recv_pyobj()
        print("Received request: {}: Type: {}".format(prediction_request, type(prediction_request['feature_type'])))

        predict(prediction_request)



        feature_models = {
            'mfcc': mfcc_model,
            'chroma_cens': chroma_cens_model,
            'chroma_cqt': chroma_cqt_model,
            'chroma_stft': chroma_stft_model,
            'melspectrogram': mel_model
        }