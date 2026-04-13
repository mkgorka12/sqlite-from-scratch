from abc import ABC
from .constants import CELL_COUNT_LEN


class PageHeader(ABC):
    CELL_COUNT_OFFSET = 3

    @classmethod
    def _get_cell_count(self, page_header_bytes: bytes) -> None:
        cell_count_bytes = page_header_bytes[
            self.CELL_COUNT_OFFSET : self.CELL_COUNT_OFFSET + CELL_COUNT_LEN
        ]
        cell_count = int.from_bytes(cell_count_bytes, "big")

        return cell_count

    def __init__(self, page_header_bytes: bytes) -> None:
        self.cell_count = self._get_cell_count(page_header_bytes)


class PageHeaderLeaf(PageHeader):
    def __init__(self, page_header_bytes: bytes) -> None:
        super().__init__(page_header_bytes)


class PageHeaderInterior(PageHeader):
    RIGHT_CHILD_PAGE_NUMBER_OFFSET = 8
    RIGHT_CHILD_PAGE_NUMBER_LEN = 4

    @classmethod
    def _get_right_child_page_number(cls, page_header_bytes: bytes) -> int:
        right_child_page_number_bytes = page_header_bytes[
            cls.RIGHT_CHILD_PAGE_NUMBER_OFFSET : cls.RIGHT_CHILD_PAGE_NUMBER_OFFSET
            + cls.RIGHT_CHILD_PAGE_NUMBER_LEN
        ]
        right_child_page_number = int.from_bytes(right_child_page_number_bytes, "big")

        return right_child_page_number

    def __init__(self, page_header_bytes: bytes) -> None:
        super().__init__(page_header_bytes)
        self.right_child_page_number = self._get_right_child_page_number(
            page_header_bytes
        )


class DatabaseHeader:
    PAGE_SIZE_OFFSET = 16
    PAGE_SIZE_LEN = 2

    def __init__(self, database_header_bytes: bytes) -> None:
        self.page_size = self._get_page_size(database_header_bytes)

    @classmethod
    def _get_page_size(cls, database_header_bytes: bytes) -> int:
        page_size_bytes = database_header_bytes[
            cls.PAGE_SIZE_OFFSET : cls.PAGE_SIZE_OFFSET + cls.PAGE_SIZE_LEN
        ]
        page_size = int.from_bytes(page_size_bytes, "big")

        return page_size
