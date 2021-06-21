'''--------------lyre.io--------------
Lyre.io is an interactive application that uses GPT-2 as its backend.
The GPT-2 code is an improved version of the original created by Nshepperd: https://github.com/nshepperd/gpt-2
All the code that is based on the version of Nshepperd can be found in the /src folder. This source code 
has been slightly altered with the TF 2.4 upgrade tool to make it compatible with the latest version of TensorFlow.
interakt.py contains the core functionality which is wrapped into a GUI.
In this code some code is copied and altered from the Nshepperd source code (interactive_conditional_samples.py) so
it was able to work with the GUI interaction. These pieces of code will be pointed out with the comment tag: Nshepperd.
'''

##--------------Imports--------------##
import json
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"                                                                            #Turn off all logging of Tensorflow, improved performance and debugging
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'                                                                           #Force Tensorflow to use CPU
import numpy as np
import tensorflow as tf
import time as t
import sys
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading as td
import random

from src import model, sample, encoder

def default_handler(address, *args):
    global queue
    if "input_string" in address:
        queue.append(args)

def receiver():
    dispatcher = Dispatcher()
    # dispatcher.map("/something/*", print_handler)
    dispatcher.set_default_handler(default_handler)
    server = BlockingOSCUDPServer(("127.0.0.1", 5001), dispatcher)
    server.serve_forever()  # Blocks forever

def main_code():
    global queue
    queue = []
    client = SimpleUDPClient("127.0.0.1", 5002)
    print("ready")
    while(True):
        if len(queue) > 0:
            ip_client = queue[0][1]
            raw_text = queue[0][0]
            print("processing")
            client.send_message("/output", [str(random.randint(0,500)),ip_client])
            print("ready")
            queue.pop(0)
            raw_text = ''
        t.sleep(1)

def main():
    server = td.Thread(target=receiver)
    mainc = td.Thread(target=main_code)
    server.daemon = True
    mainc.daemon = True
    mainc.start()
    server.start()
    mainc.join()
    server.join()

    

if __name__ == '__main__':
    main()
    try:
        while True:
            t.sleep(2)
    except KeyboardInterrupt:
        pass