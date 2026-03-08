from __future__ import annotations


class AnticaptchaException(Exception):
    """Base exception for all Anticaptcha API errors.

    Raised when the API returns a non-zero ``errorId``. Inspect
    :attr:`error_code` to determine the cause::

        try:
            job = client.create_task(task)
        except AnticaptchaException as e:
            if e.error_code == "ERROR_ZERO_BALANCE":
                print("Please top up your balance")
            else:
                raise

    :param error_id: Numeric error ID from the API (or a local identifier).
    :param error_code: Error code string (e.g. ``"ERROR_ZERO_BALANCE"``).
    :param error_description: Human-readable error description.
    """

    def __init__(
        self,
        error_id: int | str | None,
        error_code: int | str,
        error_description: str,
        *args: object,
    ) -> None:
        super().__init__(f"[{error_code}:{error_id}]{error_description}")
        self.error_description = error_description
        self.error_id = error_id
        self.error_code = error_code


AnticatpchaException = AnticaptchaException
"""Backward-compatible alias (legacy misspelling)."""


class InvalidWidthException(AnticaptchaException):
    """Raised when an invalid grid width is specified."""

    def __init__(self, width: int) -> None:
        self.width = width
        msg = f"Invalid width ({self.width}). Can be one of these: 100, 50, 33, 25."
        super().__init__("AC-1", 1, msg)


class MissingNameException(AnticaptchaException):
    """Raised when a required ``name`` parameter is missing during serialization."""

    def __init__(self, cls: type) -> None:
        self.cls = cls
        msg = 'Missing name data in {0}. Provide {0}.__init__(name="X") or {0}.serialize(name="X")'.format(
            str(self.cls)
        )
        super().__init__("AC-2", 2, msg)
