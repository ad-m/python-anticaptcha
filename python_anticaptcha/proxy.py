from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Proxy:
    """Immutable representation of a proxy server.

    Use :meth:`parse_url` to build from a URL string, then pass the proxy
    parameters to a proxy-enabled task class with :meth:`to_kwargs`::

        proxy = Proxy.parse_url("socks5://user:pass@host:1080")
        task = NoCaptchaTask(url, key, user_agent=UA, **proxy.to_kwargs())

    :param proxy_type: Protocol — ``"http"``, ``"socks4"``, or ``"socks5"``.
    :param proxy_address: Hostname or IP address.
    :param proxy_port: Port number.
    :param proxy_login: Username for authentication (default: ``""``).
    :param proxy_password: Password for authentication (default: ``""``).
    """

    proxy_type: str
    proxy_address: str
    proxy_port: int
    proxy_login: str = ""
    proxy_password: str = ""

    @classmethod
    def parse_url(cls, url: str) -> Proxy:
        """Create a :class:`Proxy` from a URL string.

        :param url: Proxy URL, e.g. ``"socks5://user:pass@host:1080"``
            or ``"http://host:8080"``.
        :returns: A new :class:`Proxy` instance.
        :raises ValueError: If the URL is missing a hostname or port.
        """
        parsed = urlparse(url)
        if not parsed.hostname or not parsed.port:
            raise ValueError(f"Invalid proxy URL: {url}")
        return cls(
            proxy_type=parsed.scheme,
            proxy_address=parsed.hostname,
            proxy_port=parsed.port,
            proxy_login=parsed.username or "",
            proxy_password=parsed.password or "",
        )

    def to_kwargs(self) -> dict[str, str | int]:
        """Convert to a keyword-arguments dictionary for task constructors.

        The returned dictionary can be unpacked directly into any
        proxy-enabled task class::

            task = NoCaptchaTask(url, key, user_agent=UA, **proxy.to_kwargs())

        :returns: Dictionary with ``proxy_type``, ``proxy_address``,
            ``proxy_port``, ``proxy_login``, and ``proxy_password`` keys.
        """
        return {
            "proxy_type": self.proxy_type,
            "proxy_address": self.proxy_address,
            "proxy_port": self.proxy_port,
            "proxy_login": self.proxy_login,
            "proxy_password": self.proxy_password,
        }
