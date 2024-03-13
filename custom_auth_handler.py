from typing import Dict, Optional

class AuthHandler(Exception):
    """
    Custom exception class for authentication errors.
    """
    def __init__(self, error: Dict[str, str], status_code: int, payload: Optional[Dict[str, str]] = None):
        super().__init__(error['description'])  # Initialize the base class with the error description.
        self.error = error
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """
        Serializes the important information of the exception into a dictionary.
        """
        rv = dict(self.payload or ())
        rv['error'] = self.error
        return rv