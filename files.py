import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename
import tkinter.scrolledtext as scrolledtext

import numpy as np

# import tensorflow as tf
# print(tf.__version__)

import os
import logging
from modules.constants import *
from modules.extract import *

import zmq

encoding='utf-8'

logger = logging.Logger(name="COPD_GUI", level=logging.DEBUG)

validation_socket:zmq.Socket = None
feature_socket:zmq.Socket = None
predict_socket:zmq.Socket = None
console_output = None



def init_zmq_contexts():
    """
    DON'T FORGET TO DESTROY CONTEXTS BEFORE ENDING THE PROGRAM.

    Init `zmq` contexts in the following order:
    1. Validation Socket
    2. Feature Socket
    3. Prediction Socket
    """
    global validation_socket
    global validation_context
    validation_context = zmq.Context()

    logger.log(logging.DEBUG, "Connecting to Validation server...")
    validation_socket = validation_context.socket(zmq.REQ)
    validation_socket.connect("tcp://localhost:{}".format(VALIDATE_PORT))

    global feature_socket
    global feature_context
    feature_context = zmq.Context()

    logger.log(logging.DEBUG, "Connecting to Feature Extraction Server...")
    feature_socket = feature_context.socket(zmq.REQ)
    feature_socket.connect('tcp://localhost:{}'.format(FEATURE_PORT))

    global predict_socket
    global predict_context
    predict_context = zmq.Context()

    logger.log(logging.DEBUG, "Connecting to Predict Extraction Server...")
    predict_socket = predict_context.socket(zmq.REQ)
    predict_socket.connect('tcp://localhost:{}'.format(PREDICT_PORT))






def validate_file(filename):
    """
    Returns a reply from `modules.validate` in the format:
    ```
    {
        "file_name": audio_file_name,
        "validity": VALID_AUDIO|INVALID_AUDIO
    }
    ```
    """

    console_output.insert(END, '\nfilename: {}'.format(filename))
    console_output.insert(END, '\nValidating file...')

    validation_socket.send_string(filename)

    response = validation_socket.recv_json()

    # Check for errors in response
    if type(response) != dict:
        logger.log(logging.DEBUG, "Response recieved not type of dict. Response: {}".format(response))
        return False

    if 'file_name' not in response.keys() or 'validity' not in response.keys():
        logger.log(logging.WARN, "Malfunctioned response for validation. Response: {}".format(response))
        return False

    # FIXME: Fix this.
    # if response['file_name'] != filename:
    #     logger.log(logging.ERROR, "Request sent for file: '{}' but recieved response for file: '{}'".format(filename, response['file_name']))
    #     console_output.insert(END, '\nError in response from validation server. \nPerhaps some previous messages replies were pending. Please try again.')
    #     return False


    # Now the response is good, print the result to the gui console.
    if response['validity'] == INVALID_AUDIO:
        console_output.insert(END, '\nFile invalid. Please select a wav file.')
        return False

    if response['validity'] not in [VALID_AUDIO, INVALID_AUDIO]:
        logger.log(logging.WARN, "Recieved response: {}\nKeyError: Invalid value '{}' for key 'validity'.".format(response, response['validity']))
        return False

    console_output.insert(END, '\nFile validation complete: {}'.format(response))
    
    return True


def get_features(file_name):
    """
    Returns a message from `modules.extract` in the format:
    ```
    response = {
        'file_name': file_name,
        MFCC: mfcc,
        MEL: mel,
        C_STFT: c_stft,
        C_CQT:c_cqt,
        C_CENS: c_cens
    }
    ```
    """
    feature_socket.send_string(file_name)

    features_dict = feature_socket.recv_pyobj()

    return features_dict

    # Rant #1. 26 May 7:44 PM
    # I know ghanta koi fix karega ise. Including myself 😂 But still. No harm in trying.
    # So future developer, I could have directly imported the modules and done it, But...
    # Distributing modules will only make the deployment easier. Just know that
    # I'm proud that you opened this code. 
    # TODO: Add the below comparison to the test module.
    # test_features_dict = init_extraction(file_name)

    # for k in features_dict.keys():
    #     if type(features_dict[k]) == np.ndarray:
    #         print("np array for key {}".format(k))
    #         if np.array_equal(features_dict[k], test_features_dict[k]):
    #             print("np array for key {} equal".format(k))
    #         else:
    #             print("-----------------> np array for key {} NOT EQUAL".format(k))

    #     elif features_dict[k] == test_features_dict[k]:
    #         print("Key {} equal".format(k))
    #     else:
    #         print("Values for key {} different | {} | {}".format(key, features_dict[k], test_features_dict[k]))

def get_prediction(feature_type, feature_value):
    console_output.insert(END, '\nRequesting prediction for feature {}...'.format(feature_type))

    predict_socket.send_pyobj({
        'feature_type': feature_type,
        'content': feature_value
    })


def open_file_picker():
    filename = askopenfilename(filetypes=[("wav files", '.wav')])
    
    if not filename:
        console_output.insert(END, '\nERROR: Please select a file.')
        return

    console_output.insert(END, '\nChecking file: {}'.format(filename))
    
    is_valid = validate_file(filename)

    # FIXME: Change this
    if not is_valid:
        return

    console_output.insert(END, '\n')
    features = get_features(filename)

    del features['file_name']

    for key in features.keys():
        get_prediction(key, features[key])

        prediction = predict_socket.recv_pyobj()

        console_output.insert(END, '\nPrediction: Model Name: {} | Predicted Class: {}'.format(prediction['model'], prediction['class']))

def init_root_window():
    root = Tk()
    root.title("COPD Analyzer")
    root.geometry("800x600")
    # root.minsize(600, 400)


    text=Label(root, text="Select files to upload", width=30, pady=10, height=10, anchor=SW)
    text['font'] = ('Hack', '18')
    # text.config(anchor=CENTER)
    text.pack()

    myButton = Button(root, text="Upload File", padx=30, pady=5, command=open_file_picker)
    myButton.pack()

    # filename = "101_Meditron.wav"
    # fileNameText=Label(root, text="File Name: "+ filename, width=75, height=10, anchor=SW)
    # fileNameText.pack()

    # result = "Positive"
    # resultText=Label(root, text="Result: " + result, width=75, height=2, anchor=SW)
    # resultText.pack()

    # resultText.
    global console_output
    console_output = scrolledtext.ScrolledText(root, undo=True, pady=30, padx=10)
    console_output['font'] = ('Hack', '14')
    console_output.pack(expand=True, fill='both')
    # console_output.config(state=DISABLED)

    console_output.insert(INSERT, "Status messages will appear here...")



    root.mainloop()

    return console_output 


if __name__ == "__main__":
    # mfcc_model = load_model('saved_models/mfcc')
    # chroma_cens_model = load_model('saved_models/chroma_cens')

    # init_root_window()

    logger.log(logging.INFO, "Init zmq contexts...")
    init_zmq_contexts()

    logger.log(logging.INFO, "Loading Main Window...")
    console_output = init_root_window()

    logger.log(logging.INFO, "Destroying contexts..")
    validation_context.destroy()
    feature_context.destroy()


    



