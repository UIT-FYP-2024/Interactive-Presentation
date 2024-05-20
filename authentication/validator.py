# authentication/validator.py

import re


class FormValidator:
    """
    This class will check the validity of the entered username, name, and email for a
    newly registered user.
    """

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Checks the validity of the entered username.

        Parameters
        ----------
        username: str
            The username to be validated.
        Returns
        -------
        bool
            Validity of entered username.
        """
        pattern = r"^[a-zA-Z0-9_-]{1,20}$"
        return bool(re.match(pattern, username))

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Checks the validity of the entered name.

        Parameters
        ----------
        name: str
            The name to be validated.
        Returns
        -------
        bool
            Validity of entered name.
        """
        return 1 < len(name) < 100

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Checks the validity of the entered email.

        Parameters
        ----------
        email: str
            The email to be validated.
        Returns
        -------
        bool
            Validity of entered email.
        """
        return "@" in email and 2 < len(email) < 320
