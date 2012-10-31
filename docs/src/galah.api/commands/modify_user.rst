modify_user
===========

Changes the account type of a user.

Reference
---------

.. function:: modify_user(email, account_type)
    
    :param email: The email of the user to change the type of.

    :param account_type: The new account type for the user. May be one of
                         student, teacher, or admin.

Example Usage
-------------

Here we will elevate the student **test@school.edu** to the status of
**teacher**.

>>> modify_user test@school.edu teacher
--Logged in as jsull003@ucr.edu--
Success! User [email = test@school.edu, account_type = student] has been retyped as a teacher