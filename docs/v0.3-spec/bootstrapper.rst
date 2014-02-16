# Boostrapper Specification

The bootstrapper is the small application that is loaded onto every VM by the vmfactory. The bootstrapper handles any necessary guest-level operations and communicates with the outside world through a simple protocol.

The minimum required version of Python available on the VM is version 2.6 (the same version requirement as the Galah server codebase).

The module ``bootstrapper.protocol`` should be used when communicating the bootstrapper. In addition, make sure that any changes to that file that break the interface are then updated here.

## Bootstrapper Protocol

Once the bootstrapper starts up it will accept TCP connections on port ``40``.

### Framing

Messages to the bootstrapper should follow the format ``COMMAND NUM_BYTES PAYLOAD``: an ASCII encoded message type followed by a space, the number of bytes in the payload (encoded as an ASCII encoded string containing the number) followed by a space, followed by the payload (encoding depends on the command). Any newline and space characters printed before a message are ignored (useful when interacting with the bootstrapper over telnet). For example, the following stream contains two well framed messages:

.. code-block:: json

    foo 19 {"args": [1, 2, 3]}
    bar 12 random data!

Responses by the bootstrapper will be framed the same way.

The ``bootstrapper.protocol.Decoder`` object is capable of decoding well-framed messages from a byte stream.

.. note::

    A message with a 0 length payload must still have a space after the 0.

### Security

The bootstrapper is listening on a TCP port and allows multiple connections. Therefore there is nothing stopping the student's code from connecting to it. In order to prevent any malicious behavior from arising from this, the bootstrapper is configured with a randomly generated "secret" which is then used to authenticate connections to it.

### Commands

#### init

**Payload encoding:** a UTF-8 encoded JSON dictionary containing the configuration.

When the bootstrapper receives an ``init`` command it will initialize itself based on the payload. The JSON dictionary must have the following keys and no others (this list should mirror the list at ``bootstrapper.protocol.INIT_FIELDS``:

 * **user** (string or int): The username or UID to run the harness under.
 * **group** (string or int): The groupname or GID to run the harness under.
 * **harness_directory** (string): The directory to store the test harness in.
 * **submission_directory** (string): The directory to store the submission in.
 * **secret** (string): A string of bytes that all subsequent connections must authenticate with in order for the bootstrapper to accept their commands.

The bootstrapper will respond with an ``ok`` response with an empty payload.

#### get_config

**Payload encoding:** empty.

When the bootstrapper recieves this command it will respond with a ``config``
message containing the UTF-8 JSON encoded configuration it received from the
last ``init`` command (it may not match the exact payload that was sent though because it will be reserialized from the bootstrapper's own internal representation of the configuration).

#### upload_harness and upload_submission

**Payload encoding:** a zip file containing the files.

When the bootstrapper receives this command it will unpack the zip file into the correct directory depending on its configuration, and then respond with an empty ``ok`` message.

####
