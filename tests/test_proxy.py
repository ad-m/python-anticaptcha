import pytest

from python_anticaptcha.proxy import Proxy


class TestProxyParseUrl:
    def test_full_url(self):
        proxy = Proxy.parse_url("socks5://user:pass@host.example.com:8080")
        assert proxy.proxy_type == "socks5"
        assert proxy.proxy_address == "host.example.com"
        assert proxy.proxy_port == 8080
        assert proxy.proxy_login == "user"
        assert proxy.proxy_password == "pass"

    def test_without_credentials(self):
        proxy = Proxy.parse_url("http://123.123.123.123:9190")
        assert proxy.proxy_type == "http"
        assert proxy.proxy_address == "123.123.123.123"
        assert proxy.proxy_port == 9190
        assert proxy.proxy_login == ""
        assert proxy.proxy_password == ""

    def test_socks4(self):
        proxy = Proxy.parse_url("socks4://10.0.0.1:1080")
        assert proxy.proxy_type == "socks4"
        assert proxy.proxy_address == "10.0.0.1"
        assert proxy.proxy_port == 1080

    def test_invalid_url_no_port(self):
        with pytest.raises(ValueError, match="Invalid proxy URL"):
            Proxy.parse_url("socks5://host.example.com")

    def test_invalid_url_no_host(self):
        with pytest.raises(ValueError, match="Invalid proxy URL"):
            Proxy.parse_url("socks5://:8080")


class TestProxyToKwargs:
    def test_output(self):
        proxy = Proxy(
            proxy_type="http",
            proxy_address="1.2.3.4",
            proxy_port=8080,
            proxy_login="user",
            proxy_password="pass",
        )
        kwargs = proxy.to_kwargs()
        assert kwargs == {
            "proxy_type": "http",
            "proxy_address": "1.2.3.4",
            "proxy_port": 8080,
            "proxy_login": "user",
            "proxy_password": "pass",
        }

    def test_unpack_into_task(self):
        """Verify to_kwargs() can be unpacked into proxy-requiring task constructors."""
        proxy = Proxy.parse_url("socks5://u:p@h:8080")
        kwargs = proxy.to_kwargs()
        assert "proxy_type" in kwargs
        assert "proxy_address" in kwargs
        assert "proxy_port" in kwargs


class TestProxyFrozen:
    def test_immutable(self):
        proxy = Proxy.parse_url("http://1.2.3.4:80")
        with pytest.raises(AttributeError):
            proxy.proxy_type = "socks5"
