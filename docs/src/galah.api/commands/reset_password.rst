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

reset_password
==============

Resets the password of a user to a given password.

Reference
---------

.. function:: reset_password(email[, new_password = '']):
    
    :param email: The email of the user to change the password of.

    :param new_password: The new password for the user. You can reset the
                         password to a blank password to require the user to
                         log in through OAuth2.

Example Usage
-------------

Here we will reset **test@school.edu**'s password to **cool_password**.

>>> reset_password test@school.edu cool_password
--Acting as user jsull003@ucr.edu--
Success! Password for User [email = test@school.edu, account_type = teacher] succesfully reset.

Permissions
-----------

**admin** users can use this command.