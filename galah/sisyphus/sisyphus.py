#!/usr/bin/env python
# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
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

# Load Galah's configuration.
from galah.base.config import load_config
config = load_config("sisyphus")

# Set up logging
import logging
logger = logging.getLogger("galah.sisyphus")

# Connect to the mongo database
import mongoengine
mongoengine.connect(config["MONGODB"])

# Set up the queue we will store tasks in
from Queue import Queue
from collections import namedtuple
Task = namedtuple("Task", ("name", "args", "kwargs"))
task_queue = Queue()

# Grab all of the tasks we know about
from tasks import task_list

# All ZMQ operations must be done within a context
import zmq
context = zmq.Context()

# Open up a socket we will listen on.
socket = context.socket(zmq.REP)
socket.bind(config["SISYPHUS_ADDRESS"])

import sys
def consumer():
    # Create a new logger for this consumer
    from threading import current_thread
    logger = logging.getLogger("galah.sisyphus." + current_thread().name)
    
    while True:
        task = task_queue.get()

        try:
            task_list[task.name](*task.args, **task.kwargs)
        except Exception as e:
            if type(e) is TypeError and str(e).startswith("%s()" % task.name):
                logger.error("Task with bad parameters: %s", str(task))
            else:
                logger.warning(
                    "Exception in task %s.", task.name,
                    exc_info = sys.exc_info()
                )

def to_task(request):
    # Do very explicit validation on the request so we can give better error
    # messages.
    is_valid = (
        type(request) is dict and
        all(k in request.keys() for k in ("task_name", "args", "kwargs")) and
        isinstance(request["task_name"], basestring) and
        type(request["args"]) is list and
        type(request["kwargs"]) is dict
    )

    if not is_valid:
        raise RuntimeError("Poorly formed request.")

    return Task(
        name = request["task_name"],
        args = request["args"],
        kwargs = request["kwargs"]
    )

from threading import Thread
consumer_thread = Thread(name = "consumer", target = consumer)
consumer_thread.daemon = True
consumer_thread.start()

def main():
    while True:
        task = socket.recv_json()

        # Convert the JSON dict we got into a Task object.
        try:
            task = to_task(task)
        except RuntimeError as e:
            # sisyphus is only exposed to internal components within Galah.
            # This is a very serious error signifying a problem with Galah's
            # logic.
            logger.exception("Error converting request to Task object.")

            socket.send_json({
                "success": False,
                "error_string": str(e)
            })

            continue

        logger.info("Recieved request for task %s.", task.name)

        # Check if this is a recognized command.
        if task.name not in task_list.keys():
            # Same as above, this is a serious error signifying a problem with
            # Galah's logic.
            logger.error("Unknown task '%s'.", task.name)

            socket.send_json({
                "success": False,
                "error_string": "Unknown task '%s'" % task.name
            })

            continue

        # All is good, place the task in the queue
        task_queue.put(task)

        socket.send_json({"success": True})

if __name__ == "__main__":
    main()