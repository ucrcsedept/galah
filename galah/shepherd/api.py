import zmq

context = zmq.Context()
context.linger = 2 * 1000

def send_test_request(shepherd_host, submission_id):
    # TODO: Make the socket thread-local.
    # Create a new socket to send a test request to shepherd.
    shepherd = context.socket(zmq.DEALER)

    shepherd.connect(shepherd_host)
    shepherd.send_json({
       "submission_id": str(submission_id)
    })

    shepherd.close()
