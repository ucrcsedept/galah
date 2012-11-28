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

delete_user
===========

Deletes the given user from existence.

Reference
---------

.. function:: delete_user(email):
    
    :param email: The exact email of the user to delete.

Example Usage
-------------

Here we delete the user **test@test.edu**. Notice that there is no prompt or
verification step! **So be careful!**

>>> delete_user test@test.edu
--Acting as user jsull003@ucr.edu--
Success! User [email = test@test.edu, account_type = student] deleted.

Permissions
-----------

**admin** users can use this command.