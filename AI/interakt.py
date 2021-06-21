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
    ##--------------Settings--------------##
    model_name="lyrics_model_v2_ckpt26"
    seed=None
    nsamples=1
    batch_size=1
    length=200
    temperature=1.0
    top_k=40
    top_p=0.0
    queue = []
    client = SimpleUDPClient("127.0.0.1", 5002)

    if batch_size is None:                                                                                              #Nshepperd, init the batch size
            batch_size = 1                                                                                              #Nshepperd
    assert nsamples % batch_size == 0                                                                                   #Nshepperd

    enc = encoder.get_encoder(model_name)                                                                               #Nshepperd, get the encoder from the backend to encode any language
    hparams = model.default_hparams()                                                                                   #Nshepperd, get the model's default hparams
    with open(os.path.join('models', model_name, 'hparams.json')) as f:                                                 #Nshepperd
        hparams.override_from_dict(json.load(f))                                                                        #Nshepperd

    if length is None:                                                                                                  #Nshepperd, set window size of perceptron
        length = hparams.n_ctx // 2                                                                                     #Nshepperd
    elif length > hparams.n_ctx:                                                                                        #Nshepperd
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)                               #Nshepperd
        
    with tf.compat.v1.Session(graph=tf.Graph()) as sess:                                                                #Nshepperd, load training loop
        context = tf.compat.v1.placeholder(tf.int32, [batch_size, None])                                                #Nshepperd, prepare a placeholder for the text output
        np.random.seed(seed)                                                                                            #Nshepperd, get a new seed
        tf.compat.v1.set_random_seed(seed)                                                                              #Nshepperd, set a starting point according to the seed
        output = sample.sample_sequence(                                                                                #Nshepperd, get and set the sample sequence to prepare the model
            hparams=hparams, length=length,                                                                             #Nshepperd
            context=context,                                                                                            #Nshepperd
            batch_size=batch_size,                                                                                      #Nshepperd
            temperature=temperature, top_k=top_k, top_p=top_p                                                           #Nshepperd
        )                                                                                                               #Nshepperd

        saver = tf.compat.v1.train.Saver()                                                                              #Nshepperd, load the model
        ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))                                           #Nshepperd
        saver.restore(sess, ckpt)                                                                                       #Nshepperd

        print("ready")
        while(True):
            if len(queue) > 0:
                ip_client = queue[0][1]
                raw_text = queue[0][0]
                queue.pop(0)
                print("processing")
                while not raw_text:                                                                                         #Ignore if empty
                    break
                context_tokens = enc.encode(raw_text)                                                                       #Nshepperd, get the tokens
                generated = 0                                                                                               #generating length tracker
                for _ in range(nsamples // batch_size):                                                                     #Nshepperd
                    out = sess.run(output, feed_dict={                                                                      #Nshepperd, altered piece of code to generate text, core of the text generation
                        context: [context_tokens for _ in range(batch_size)]                                                #Nshepperd
                    })[:, len(context_tokens):]   
                    text = ""
                    for i in range(batch_size):                                                                             #Go over all generated batches, decode it and write it to the output box
                        generated += 1                                                                                      
                        text = enc.decode(out[i]) 
                        text+="\n"
                    client.send_message("/output", [text,ip_client])
                print("ready")
                raw_text = ''
            t.sleep(1)

def main():
    server = td.Thread(target=receiver)
    main1 = td.Thread(target=main_code)
    # main2 = td.Thread(target=main_code)
    server.daemon = True
    main1.daemon = True
    # main2.daemon = True
    main1.start()
    # main2.start()
    server.start()
    main1.join()
    # main2.join()
    server.join()

    

if __name__ == '__main__':
    main()
    try:
        while True:
            t.sleep(2)
    except KeyboardInterrupt:
        pass