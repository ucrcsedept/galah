get_archive
===========

Download all the submissions for a given assignment as a tarball. The tarball
is structured with directories corresponding to users as top-level directories,
then each of their submissions are in timestamped directories. See the below
example...

.. code-block:: none

    user@school.edu
    |---- 2012-10-20-23-44-55
    |     |---- main.cpp
    |     +---- something_else.cpp
    |---- 2012-10-20-23-33-21
    +     +---- main.cpp
    other_user@schoole.edu
    |---- 2012-10-19-21-33-43
    +     +---- main.cpp

The timestamps follow the format ``YEAR-MONTH-DAY-HOUR-MINUTE-SECOND``. Also, in
the unlikely scenario that two submissions by the same user have the same
timestamp, the timestamped directory will follow the format
``YEAR-MONTH-DAY-HOUR-MINUTE-SECOND-RANDOMNUMBER``.

Reference
---------

.. function:: get_archive(assignment[, email = '']):
    
    :param assignment: The exact id of the assignment.
    :param email: You can optionally specify a user's email to filter on, and
                  only that user's submissions will be downloaded. The structure
                  of the archive will remain the same however (so the only
                  top-level directory will be named ``email``).

Example Usage
-------------

>>>  get_archive 5091654355c448096df90687
--Logged in as jsull003@ucr.edu--
Your archive is being created. You have 0 jobs ahead of you.
The server is requesting that you download a file...
Where would you like to save it (default: ./submissions.tar.gz)?: submissions-all.tar.gz
File saved to submissions-all.tar.gz.
>>> get_archive 5091654355c448096df90687 student@ucr.edu
--Logged in as jsull003@ucr.edu--
Your archive is being created. You have 0 jobs ahead of you.
The server is requesting that you download a file...
Where would you like to save it (default: ./submissions.tar.gz)?:  
File saved to ./submissions.tar.gz.
