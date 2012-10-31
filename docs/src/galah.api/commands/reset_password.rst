reset_password
==============

Resets the password of a user to a given password.

Reference
---------

.. function:: reset_password(email, new_password)
    
    :param email: The email of the user to change the password of.

    :param new_password: The new password for the user.

Example Usage
-------------

Here we will reset **test@school.edu**'s password to **cool_password**.

>>> reset_password test@school.edu cool_password
--Logged in as jsull003@ucr.edu--
Success! Password for User [email = test@school.edu, account_type = teacher] succesfully reset.