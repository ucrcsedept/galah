Galah API
=========

Summary
-------

This is a complete reference to Galah's outward facing API.

Using the API
-------------

To execute the commands listed below in the :ref:`command_reference`, you must
use the api_client.py client. It works by packaging up any commands you want to
execute into HTTP requests, and sending them to the Galah web server.

Configuring the API Client
^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you use api_client.py you need to configure it so that it knows where the
Galah web server is, and so that it knows your credentials so it can log in as
you.

There are a variety of locations the API client will look in for your
configuration file. They are listed, in order, below:

.. code-block:: bash

    ~/.galah/config/api_client.config
    /etc/galah/api_client.config
    ./api_client.config

Further, if you set the ``GALAH_CONFIG_PATH`` environmental variable to be a
colon delimitted list of values (just like the ``PATH`` variable), those paths
will be searched in order first.

To debug issues with the API Client finding your configuration file, you can
run the API client with the ``--config-path`` flag to have it list all the
locations it checks for configuration files.

Once you decide where to put this configuration file, you need to populate it
with values. Below is an example of a configuration file (all configuration
options are listed in this example):

.. code-block:: js

    {
        "galah_host": "http://www.galahserver.com",
        "galah_home": "~/.galah",
        "user": "myemail@school.edu",
        "password": "plaintext password",
        "use_oauth": false
    }

**Make sure to set the permissions of your api_client.config file to 600 so
other users can't access it.**

If you are uncomfortable storing your password as plain text, you can safely
leave it out of the configuration and you will be prompted when logging in.
Altenatively, set the environmental variable **GALAH_PASSWORD** before running
the API client, and that password will be used.

If you set ``use_oauth`` to true, when you have to login, a web browser will be
opened and you will be authenticated with google. You do not have to specify
a password to the API client in this case, but make sure to set your user to
the user you will log into google with.

Also make sure to replace ``www.galahserver.com`` with the address of your
institution's Galah web server. You may also want to use *https* vs *http*
depending on your institution's installation.

``galah_home`` is where the ``tmp/`` directory will be stored, and other
directories and files may find there way in there as well.

Examples Using the API Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A simple way to use the API client is to execute the api_client.py file
with the command and the arguments you want to pass to it.

>>> api_client.py find_user jsull
--Logged in as jsull003@ucr.edu--
1 user(s) found matching query {email contains 'jsull'}.
    User [email = jsull003@ucr.edu, account_type = admin]

It can be bothersome to continually type out api_client.py over and over again
if you are executing multiple commands however. Therefore **you can enter a
shell** by running the command ``api_client.py -s`` which will place you into an
interactive shell. Within this shell, you can simply enter the commands followed
by their arguments (you can even use tab completion for the commands).

>>> api_client.py -s
>>> find_user jsull
--Logged in as jsull003@ucr.edu--
1 user(s) found matching query {email contains 'jsull'}.
    User [email = jsull003@ucr.edu, account_type = admin]

All examples in the :ref:`command_reference` below assume you're in the
interactive shell.

If you downloaded the official API client tarball (download link not yet
available, run the generate_apiclient_tarbell.sh command to create it) you will
be able to access man pages on every command by typing ``man`` and then the
command (ex: ``man find_user``). The man pages are just man page versions of
the below documentation files.

Named Arguments
^^^^^^^^^^^^^^^

Some of the API commands have a lot of paramters and specifying each one on the
command line can be a real pain. That is why the API client has support for
named arguments. To specify the value for an argument by name, use the notation
``argument_name=value``.

For example, the :doc:`commands/modify_assignment` command has a lot of
parameters, but it is likely that you will only want to specify a value for one
or two of them.

>>> modify_assignment mine/domination due="10/20/2012 10:09:00"
--Acting as user jsull003@ucr.edu--
Success! The following changes were applied to Assignment [id = 50907db055c4481a5027103d, name = World Domination].
    Due date changed from '11/01/2012 00:00:00' to '10/20/2012 10:09:00'.

*I used the shorthand notation for referencing assignments which is introduced in* :ref:`referencing_objects`.

.. _referencing_objects:

Referencing Objects
^^^^^^^^^^^^^^^^^^^

A number of the API commands will ask for an assignment, a class or a user (for example, :doc:`commands/class_info` wants a class as the first argument).

You may always reference an object by its unique ID, however, these can be long
and annoying to even copy and paste around, so there are a number off different
formats for each object that you can use instead.

Users
~~~~~

Uses must be specified by their full emails, there's no shortcut for users
unfortunately. However, if you want to reference you (the current user), you
can enter in ``me`` wherever a user is expected.

>>> user_info me
--Acting as user jsull003@ucr.edu--
User [email = jsull003@ucr.edu, account_type = admin] is enrolled in:
    Class [id = 5090634855c448134f67b3e3, name = CS 9001]

Class
~~~~~

When specifying a class, you may provide a string and Galah will look for
classes with that string in its name (the search is case insensitive). If
multiple classes match, an error will be displayed.

>>> class_info woodshop
--Acting as user jsull003@ucr.edu--
Class [id = 5090671655c448134f67b3e5, name = Woodshop 101] has assignments:
    (No assignments)
>>> class_info 10
--Acting as user jsull003@ucr.edu--
Your command cannot be completed as entered: 2 classes match your query of '10', however, this API expects 1 class. Refine your query and try again.
    Class [id = 509066e855c448134f67b3e4, name = CS 10]
    Class [id = 5090671655c448134f67b3e5, name = Woodshop 101]

Assignments
~~~~~~~~~~~

When specifying an assignment, you can use the format ``class/assignment`` where
``class`` is a class specified just like how you'd normally specify a class (you
can give an ID or a string as described above) and ``assignment`` is a partial
string of the assignment's name that you want to reference, similar to how you
specify classes.

>>> assignment_info 9001/domination
--Acting as user jsull003@ucr.edu--
Properties of Assignment [id = 50907db055c4481a5027103d, name = World Domination]:
    for_class = 5090634855c448134f67b3e3
    due_cutoff = 11/01/2012 00:00:00
    name = World Domination
    hide_until = 11/08/2012 18:00:00
    due = 11/01/2012 00:00:00
>>> assignment_info 9001/part
--Acting as user jsull003@ucr.edu--
Your command cannot be completed as entered: 5 assignments in Class [id = 5090634855c448134f67b3e3, name = CS 9001] matched your query of {name contains 'part'}, however this API expects 1 assignment. Refine your query and try again.
    Assignment [id = 509c573255c448108291c206, name = Lots of Assignments - Part 1]
    Assignment [id = 509c594f55c44810f90ec14d, name = Lots of Assignments - Part 2]
    Assignment [id = 509c595655c44810f90ec14e, name = Lots of Assignments - Part 3]
    Assignment [id = 509c595a55c44810f90ec14f, name = Lots of Assignments - Part 4]
    Assignment [id = 509c595e55c44810f90ec150, name = Lots of Assignments - Part 5]
>>> assignment_info "9001/part 2"
--Acting as user jsull003@ucr.edu--
Properties of Assignment [id = 509c594f55c44810f90ec14d, name = Lots of Assignments - Part 2]:
    for_class = 5090634855c448134f67b3e3
    name = Lots of Assignments - Part 2
    hide_until = 01/01/1970 00:00:00
    due = 11/01/2012 00:00:00

``mine`` may be specified for ``class`` if you want to search within all of the
classes your are enrolled in or assigned to.

>>> assignment_info mine/domination
--Acting as user jsull003@ucr.edu--
Properties of Assignment [id = 50907db055c4481a5027103d, name = World Domination]:
    for_class = 5090634855c448134f67b3e3
    due_cutoff = 11/01/2012 00:00:00
    name = World Domination
    hide_until = 11/08/2012 18:00:00
    due = 11/01/2012 00:00:00
>>> assignment_info mine/part
--Acting as user jsull003@ucr.edu--
Your command cannot be completed as entered: 5 assignments in classes you are enrolled in or assigned to matched your query of {name contains 'part'}, however this API expects 1 assignment. Refine your query and try again.
    Assignment [id = 509c573255c448108291c206, name = Lots of Assignments - Part 1]
    Assignment [id = 509c594f55c44810f90ec14d, name = Lots of Assignments - Part 2]
    Assignment [id = 509c595655c44810f90ec14e, name = Lots of Assignments - Part 3]
    Assignment [id = 509c595a55c44810f90ec14f, name = Lots of Assignments - Part 4]
    Assignment [id = 509c595e55c44810f90ec150, name = Lots of Assignments - Part 5]

.. _command_reference:

Command Reference
-----------------

Below are links to reference material for every API command Galah supports.

.. toctree::
    :maxdepth: 1

    commands/assignment_info

    commands/class_info

    commands/create_assignment

    commands/create_class

    commands/create_user

    commands/delete_assignment

    commands/delete_class

    commands/delete_user

    commands/drop_student

    commands/enroll_student

    commands/find_class

    commands/find_user

    commands/get_archive
    
    commands/modify_assignment

    commands/modify_class

    commands/modify_user

    commands/reset_password

    commands/user_info