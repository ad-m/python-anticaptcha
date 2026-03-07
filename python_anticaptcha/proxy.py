from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Proxy:
    proxy_type: str
    proxy_address: str
    proxy_port: int
    proxy_login: str = ""
    proxy_password: str = ""

    @classmethod
    def parse_url(cls, url: str) -> Proxy:
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
        return {
            "proxy_type": self.proxy_type,
            "proxy_address": self.proxy_address,
            "proxy_port": self.proxy_port,
            "proxy_login": self.proxy_login,
            "proxy_password": self.proxy_password,
        }
