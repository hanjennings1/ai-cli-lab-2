
# PERSON CLASS THAT USER WILL INHERIT FROM

class Person:
    """Base class for any person in the system - holds identity fields
    shared across possible subclasses (currently just User).
    """

    def __init__(self, name, email):
        if not name or not name.strip():
            raise ValueError("Name cannot be empty.")
        if not email or not email.strip():
            raise ValueError("Email cannot be empty.")

        self.name = name.strip()
        self.email = email.strip()

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, email={self.email!r})"