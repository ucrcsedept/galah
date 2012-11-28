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

create_user
===========

Creates a user with the given credentials. Be very careful executing this
API as the password may be momentarilly visible in a ps listing. Ensure you
are in a secure terminal.

Also, if the Galah webserver is not set up to use HTTPS, you should take
effort to make sure you're on the same network as Galah, because **the
password will be sent as plaintext**.

Reference
---------

.. function:: create_user(email[, password = '', account_type = 'student']):

    :param email: The email the user will use to sign in.
    
    :param password: The users password, it will be immediately hashed. You can
                     specify a blank password in which case the user will have
                     to long in through OAuth2.

    :param account_type: The account type. Current available options are
                         student, teacher, or admin. Multiple account types are
                         not legal.

Example Usage
-------------

Creating a student named **test@school.edu** with the password
**gReatPassWord**.

>>> create_user test@school.edu gReatPassWord
--Acting as user jsull003@ucr.edu--
Success! User [email = test@school.edu, account_type = student] created.

Permissions
-----------

**admin** users can use this command.