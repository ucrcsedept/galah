..
    Copyright 2012 John Sullivan
    Copyright 2012 Other contributers as noted in the CONTRIBUTERS file

    This file is part of Galah.

    Galah is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Galah is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Galah.  If not, see <http://www.gnu.org/licenses/>.

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
--Acting as user jsull003@ucr.edu--
Your archive is being created. You have 0 jobs ahead of you.
The server is requesting that you download a file...
Where would you like to save it (default: ./submissions.tar.gz)?: submissions-all.tar.gz
File saved to submissions-all.tar.gz.
>>> get_archive 5091654355c448096df90687 student@ucr.edu
--Acting as user jsull003@ucr.edu--
Your archive is being created. You have 0 jobs ahead of you.
The server is requesting that you download a file...
Where would you like to save it (default: ./submissions.tar.gz)?:  
File saved to ./submissions.tar.gz.

Permissions
-----------

**admin** and **teacher** users can use this command. Teacher users can only
download submissions for assignments in a class they're assigned to.