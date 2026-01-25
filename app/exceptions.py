"""
Shared exception classes for the GPT Lab application.

This module consolidates all custom exceptions to avoid duplication
and provide consistent error handling across the application.
"""


class OpenAIError(Exception):
    """Wraps OpenAI API errors with error type tracking."""
    def __init__(self, message, error_type=None):
        super().__init__(message)
        self.error_type = error_type


class DBError(Exception):
    """Base class for database errors."""
    pass


class RecordNotFoundError(DBError):
    """Record was not found in database."""
    pass


class RecordNotCreatedError(DBError):
    """Failed to create a record in database."""
    pass


class RecordUpdateError(DBError):
    """Failed to update a record in database."""
    pass


class BadRequestError(Exception):
    """Invalid request parameters."""
    pass


class BotNotFoundError(RecordNotFoundError):
    """Bot was not found in database."""
    pass


class BotIncompleteError(Exception):
    """Bot configuration is incomplete."""
    pass


class UserNotFoundError(RecordNotFoundError):
    """User was not found in database."""
    pass
