from zmq.utils import jsonapi

def jsonify(item):
	"""
	Serializes an object into *optimized* JSON (meaning no whitespace is used).

	"""

	return jsonapi.dumps(item, separators = (",", ":"))

def dejsonify(raw):
	"""
	Deserialize a JSON string.

	"""

	return jsonapi.loads(raw)

def router_send(socket, identify, message):
	socket.send_multipart([identify, message])

def router_send_json(socket, identity, message):
	serialized_message = jsonify(message)

	router_send(socket, identity, serialized_message)

def router_recv(socket, allow_multiple_identities = False):
	identities = socket.recv_multipart()
	message = identities.pop()

	if not allow_multiple_identities:
		if len(identities) != 1:
			raise RuntimeError("Received multiple identities.")

		return (identities[0], message)
	
	return (identities, message)

def router_recv_json(socket, allow_multiple_identities = False):
	identities, message = router_recv(socket, allow_multiple_identities)

	return (identities, dejsonify(message))
