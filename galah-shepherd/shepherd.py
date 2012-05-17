import zmq

context = zmq.Context()

# Socket to send Test Requests to galah-test(s)
sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:5557")

# Socket to recieve Test Results from galah-test(s)
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5558")

print """Test Request should look like: {database: "bla.bla", id: 47cc67093475061e3d95369d}"""
while True:
    # For now, take in tasks from stdin
    test_request = raw_input("Enter Test Request: ")
    
    sender.send(test_request)
    
    
