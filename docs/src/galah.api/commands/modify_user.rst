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

modify_user
===========

Changes the account type of a user.

Reference
---------

.. function:: modify_user(email, account_type):
    
    :param email: The email of the user to change the type of.

    :param account_type: The new account type for the user. May be one of
                         student, teacher, or admin.

Example Usage
-------------

Here we will elevate the student **test@school.edu** to the status of
**teacher**.

>>> modify_user test@school.edu teacher
--Acting as user jsull003@ucr.edu--
Success! User [email = test@school.edu, account_type = student] has been retyped as a teacher

Permissions
-----------

**admin** users can use this command.