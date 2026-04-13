from __future__ import annotations
from typing import Any
from .constants import DATABASE_HEADER_LEN
from .headers import DatabaseHeader
from .pages import Page


class Database:
    def __init__(self, path: str) -> None:
        self._path = path
        self._f = None
        self.header = None

    def __enter__(self) -> Database:
        self._f = open(self._path, "rb")

        database_header_bytes = self._f.read(DATABASE_HEADER_LEN)
        self.header = DatabaseHeader(database_header_bytes)

        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        if self._f:
            self._f.close()

    def _read_page_bytes(self, page_number: int) -> bytes:
        self._f.seek((page_number - 1) * self.header.page_size)
        page_bytes = self._f.read(self.header.page_size)
        return page_bytes

    def get_page_content(self, page_number: int) -> list[list[None | int | str]]:
        page_bytes = self._read_page_bytes(page_number)
        page = Page.get_page(page_bytes, page_number == 1)

        content_type, items = page.get_content_pointers()

        if content_type == "pages":
            data = []
            for pointed_page_number in items:
                data += self.get_page_content(pointed_page_number)
            return data

        return items
