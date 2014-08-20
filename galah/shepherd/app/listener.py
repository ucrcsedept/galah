import zmq, exiting, universal

def run(zsocket):
    while not exiting.exiting:
        # Wait for a message from the sheep
        address = zsocket.recv()
        zsocket.recv()
        body = zsocket.recv_json()
        
        if type(body) is str:
            # The sheep bleeted, add it to the queue
            universal.sheepQueue.append(address)
        else:
            # The sheep sent us environment information, note it
            universal.sheepEnvironments[address] = body

    raise exiting.Exiting()
