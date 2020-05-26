import time
import zmq
from modules.constants import *

def init_zmq():
    global context
    global socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:{}".format(VALIDATE_PORT))

def validate(audio_file_name):

    print("Type: {} | Got: {}".format(type(audio_file_name), audio_file_name))

    if ".wav" in str(audio_file_name, encoding=DEFAULT_ENCODING):
        socket.send_json({
            "file_name": str(audio_file_name),
            "validity": VALID_AUDIO
        })
    else:
        socket.send_json({
            "file_name": str(audio_file_name, encoding=DEFAULT_ENCODING),
            "validity": INVALID_AUDIO
        })


if __name__ == "__main__":
    init_zmq()

    while True:
        #  Wait for next request from client
        audio_file_name = socket.recv()
        print("Received request: %s" % audio_file_name)

        validate(audio_file_name)