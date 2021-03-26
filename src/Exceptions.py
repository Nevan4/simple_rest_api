class ApiExceptions(Exception):
    """Base class for Api exception"""

class UserNotFoundException(ApiExceptions):
    """Raised when User is not found in database"""

class IncorrectInputException(ApiExceptions):
    """Raised when input given to the server is not complained with input template"""
