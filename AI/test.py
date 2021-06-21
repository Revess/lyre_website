from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

def print_handler(address, *args):
    if "img" not in address:
        print(f"{address}: {args}")
    elif "img" in address:
        print(f"{address}: {args}")

def default_handler(address, *args):
    if "img" not in address and "weights" not in address and "system" not in address:
        print(f"DEFAULT {address}: {args}")

print("start osc_server")
dispatcher = Dispatcher()
dispatcher.map("/something/*", print_handler)
dispatcher.set_default_handler(default_handler)
ip = "127.0.0.1"
port = 5001
server = BlockingOSCUDPServer((ip, port), dispatcher)
server.serve_forever()  # Blocks forever

class SERVER():
    def __init__(self):
        for ip,port in var.addresses.items():
            if port == 7001:
                self.td_event_blocks = SimpleUDPClient(ip, port)
            else:
                var.oscclients.append(SimpleUDPClient(ip, port))

    def send_message(self,osc_address,message,client_type=0):
        if type(message) == type(np.array([])):
            message = message.tolist()
        for client in var.oscclients:
            try:
                client.send_message(osc_address, message)
            except :
                print("client: ", client, "caused an error when sending its message")