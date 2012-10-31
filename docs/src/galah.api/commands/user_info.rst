user_info
=========

Gets information on the given user including enrolled classes.

Reference
---------

.. function:: user_info(email)
    
    :param email: The exact email of the user to get info on.

Example Usage
-------------

Here we will get information on the user **eadel002@ucr.edu** who is enrolled in
only one class.

>>> user_info eadel002@ucr.edu
--Logged in as jsull003@ucr.edu--
User [email = eadel002@ucr.edu, account_type = student] is enrolled in:
    Class [id = 5090634855c448134f67b3e3, name = CS 9000]