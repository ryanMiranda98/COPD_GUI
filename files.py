import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename

# import keras
from tensorflow.keras.models import load_model
# from keras.utils import CustomObjectScope
# from keras.initializers import glorot_uniform

# import tensorflow as tf
# print(tf.__version__)

import os
import logging

MFCC = 'mfcc'
C_CENS = 'c_cens'
MEL = 'mel'
C_CQT = 'c_cqt'
C_STFT = 'c_stft'

feature_model_dirs = {
    MFCC: 'mfcc',
    C_CENS: 'chroma_cens',
    MEL: 'melsprectrogram',
    C_CQT: 'chroma_cqt',
    C_STFT: 'chroma_stft'
}

logger = logging.Logger(name="global", level=logging.DEBUG)


def load_model_from_file(type=None):
    model_dir = 'saved_models'

    if type not in [MFCC, C_CENS, MEL, C_CQT, C_STFT]:
        raise Exception("Invalid type.")

    concerned_dir = os.path.join(model_dir, feature_model_dirs[type])

    dir_contents = os.listdir(concerned_dir)

    if len(dir_contents) == 0:
        raise Exception("No model found in {}".format(concerned_dir))

    list_dir = [f.lower() for f in dir_contents]   # Convert to lower case
    
    model_name = sorted(list_dir)[-1]

    logger.debug('Found best model "{}" for type: {}'.format(model_name, feature_model_dirs[type]))

    model_path = os.path.join(concerned_dir, model_name)

    # with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
    model = load_model(model_path)

    return model


def open_file_picker():
    filename = askopenfilename(filetypes=[(".wav", ".mp3")])
    print(filename)

def init_root_window():
    root = Tk()
    root.title("COPD Analyzer")
    root.geometry("600x400")
    # root.minsize(600, 400)


    text=Label(root, text="Select files to upload", width=15, height=10, anchor=SW)
    # text.config(anchor=CENTER)
    text.pack()

    myButton = Button(root, text="Upload File", padx=50, command=open_file_picker)
    myButton.pack()

    filename = "101_Meditron.wav"
    fileNameText=Label(root, text="File Name: "+ filename, width=75, height=10, anchor=SW)
    fileNameText.pack()

    result = "Positive"
    resultText=Label(root, text="Result: " + result, width=75, height=2, anchor=SW)
    resultText.pack()

    root.mainloop()


if __name__ == "__main__":
    # mfcc_model = load_model('saved_models/mfcc')
    # chroma_cens_model = load_model('saved_models/chroma_cens')

    # init_root_window()

    mfcc_model = load_model_from_file(MFCC)
    mel_model = load_model_from_file(MEL)
    chroma_cens_model = load_model_from_file(C_CENS)
    chroma_cqt_model = load_model_from_file(C_CQT)
    chroma_stft_model = load_model_from_file(C_STFT)

    



