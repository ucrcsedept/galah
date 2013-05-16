# Copyright 2012 John Sullivan
# Copyright 2012 Other contributors as noted in the CONTRIBUTORS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

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