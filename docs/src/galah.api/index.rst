Galah API
=========

Summary
-------
This is a complete reference to Galah's outward facing API. If you are using
api_client.py to access the API, you should treat each parameter given for
the functions below as an argument to pass to the command.

For example, to create a new  user, you could execute...

   api_client.py create_user john.doe@college.edu StRongPassWOrd

Notice I leave out the last two arguments (account_type and send_receipt). I
can do this because both has default parameters. You could specify a value for
each of them if you desire...

   api_client.py create_user jane.doe@college.edu DifferentPassWoRD teacher

You will be given the results of your command in a human-readable format.

If you are accessing the API via a Python interpreter, the only thing to note
is that every API function will always, and only, return a string. This may be
changed soon.

Reference
---------
.. automodule:: galah.api.commands
    :members:
