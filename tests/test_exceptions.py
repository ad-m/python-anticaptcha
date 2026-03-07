from python_anticaptcha.exceptions import (
    AnticaptchaException,
    AnticatpchaException,
    InvalidWidthException,
    MissingNameException,
)


class TestAnticaptchaException:
    def test_attributes(self):
        exc = AnticaptchaException(1, "ERROR_KEY", "Some description")
        assert exc.error_id == 1
        assert exc.error_code == "ERROR_KEY"
        assert exc.error_description == "Some description"

    def test_str_format(self):
        exc = AnticaptchaException(1, "ERROR_KEY", "Some description")
        assert str(exc) == "[ERROR_KEY:1]Some description"

    def test_typo_alias(self):
        assert AnticatpchaException is AnticaptchaException


class TestInvalidWidthException:
    def test_message(self):
        exc = InvalidWidthException(75)
        assert exc.width == 75
        assert "75" in str(exc)
        assert "100, 50, 33, 25" in str(exc)
        assert exc.error_id == "AC-1"
        assert exc.error_code == 1


class TestMissingNameException:
    def test_message(self):
        exc = MissingNameException("MyClass")
        assert exc.cls == "MyClass"
        assert "MyClass" in str(exc)
        assert '__init__(name="X")' in str(exc)
        assert 'serialize(name="X")' in str(exc)
        assert exc.error_id == "AC-2"
        assert exc.error_code == 2
