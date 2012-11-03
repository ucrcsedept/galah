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
--Logged in as jsull003@ucr.edu--
Success! User [email = test@test.edu, account_type = student] deleted.