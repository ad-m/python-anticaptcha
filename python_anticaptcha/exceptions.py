from __future__ import annotations


class AnticaptchaException(Exception):
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


class InvalidWidthException(AnticaptchaException):
    def __init__(self, width: int) -> None:
        self.width = width
        msg = f"Invalid width ({self.width}). Can be one of these: 100, 50, 33, 25."
        super().__init__("AC-1", 1, msg)


class MissingNameException(AnticaptchaException):
    def __init__(self, cls: type) -> None:
        self.cls = cls
        msg = 'Missing name data in {0}. Provide {0}.__init__(name="X") or {0}.serialize(name="X")'.format(
            str(self.cls)
        )
        super().__init__("AC-2", 2, msg)
