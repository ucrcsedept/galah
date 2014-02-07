# Boostrapper Specification

The bootstrapper is the small application that is loaded onto every VM by the vmfactory. The bootstrapper handles any necessary guest-level operations and communicates with the outside world through a simple protocol.

The minimum required version of Python available on the VM is version 2.6 (the same version requirement as the Galah server codebase).

## Bootstrapper Protocol

Once the bootstrapper starts up it will accept TCP connections on port ``51749``.

### Framing

Messages to the bootstrapper should follow the format ``COMMAND NUM_BYTES PAYLOAD`` or the ASCII encoded message type followed by a space, the number of bytes in the payload (encoded as an ASCII encoded string containing the number) followed by a space, followed by the payload (meaning of the payload depends on the command). Any newline and space characters printed before a message are ignored (useful when interacting with the bootstrapper over telnet). For example, the following stream contains two well framed messages:

.. code-block:: json

    foo 19 {"args": [1, 2, 3]}
    bar 12 random data!

Responses by the bootstrapper will be framed the same way.

.. note::

    A message with a 0 length payload must still have a space after the 0.

### Operation

The bootstrapper is always in one of several states. Which state it is in determines the types of commands it will accept. Below is a listing of the various states and the commands the bootstrapper will accept while in that state.

Note however, that the *get_status* and *bye* commands are accepted in every state.

 * **NOT_READY** (the initial state): Accepts *init*.
 * **IDLE**: Accepts *upload_harness*.
 * **HARNESS_READY**: Accepts *upload_submission*.
 * **TEST_READY**: Accepts *run_test*.
 * **RUNNING_TEST**: Accepts *abort_test*.
 * **RESULTS_READY**: Accepts *get_results*.

The only time (with one exception) the bootstrapper transitions between states is when it receives a command, therefore the documentation of each command below notes the transition it causes (if any). The exception is during the **RUNNING_TEST** state: once the test completes the bootstrapper will transition into the **RESULTS_READY** state.

### Commands

#### init

When the bootstrapper receives an ``init`` command it will initialize itself based on the UTF-8 encoded JSON dictionary in the payload. The JSON dictionary must have the following keys and no others:

 * **user** (string or int): The username or UID to run the harness under.
 * **group** (string or int): The groupname or GID to run the harness under.
 * **harness_directory** (string): The directory to store the test harness in.
 * **testables_directory** (string): The directory to store the testables in.

The bootstrapper will respond with an ``ok`` response.

.. code-block:: json

    init 128 {"user": 100, "group": 100, "harness_directory": "/tmp/harness", "testables_directory": "/tmp/testables"}
    ok 0

#### get_config

When the bootstrapper recieves this command it will respond with a ``config``
message containing the UTF-8 JSON encoded configuration it recieved from the
last ``init`` command.

.. code-block:: json

    get_config 0
    config 128 {"user": 100, "group": 100, "harness_directory": "/tmp/harness", "testables_directory": "/tmp/testables"}

#### subscribe

This command is used to subscribe to log messages. When the bootstrapper receives a ``subscribe`` command it will begin sending ``log`` responses whenever a loggable event occurs in the bootstrapper. These ``log`` responses can occur at any time

#### get_status

When the bootstrapper receives a ``get_status`` command it will give a ``status`` response with a UTF-8 encoded payload containing the textual representation of its state.

.. code-block:: json

    ready 0
    status 4 IDLE
