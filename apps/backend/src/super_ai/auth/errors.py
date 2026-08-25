"""认证领域错误。code 必须来自合同目录。"""

from __future__ import annotations


class AuthAppError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)
