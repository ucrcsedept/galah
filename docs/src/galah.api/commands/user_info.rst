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

user_info
=========

Gets information on the given user including enrolled classes.

Reference
---------

.. function:: user_info(email):
    
    :param email: The exact email of the user to get info on.

Example Usage
-------------

Here we will get information on the user **eadel002@ucr.edu** who is enrolled in
only one class.

>>> user_info eadel002@ucr.edu
--Logged in as jsull003@ucr.edu--
User [email = eadel002@ucr.edu, account_type = student] is enrolled in:
    Class [id = 5090634855c448134f67b3e3, name = CS 9000]

Permissions
-----------

**admin** and **teacher** users are permitted to use this command.