from __future__ import annotations
from abc import ABC, abstractmethod
from .cells import CellInterior, CellLeaf
from .constants import DATABASE_HEADER_LEN, CELL_COUNT_LEN, VARINT_MAX_LEN
from .headers import PageHeaderInterior, PageHeaderLeaf
from src.utils.varint import read_varint


class Page(ABC):
    INTERIOR_PAGE_TYPE = 0x05
    LEAF_PAGE_TYPE = 0x0D

    CELL_POINTER_LEN = 2

    @classmethod
    def get_page(
        cls, page_bytes: bytes, is_page_first: bool = False
    ) -> PageInterior | PageLeaf:
        header_offset = 0
        if is_page_first:
            header_offset = DATABASE_HEADER_LEN

        # Check and return proper page type
        page_type = page_bytes[header_offset]

        if page_type == cls.INTERIOR_PAGE_TYPE:
            return PageInterior(page_bytes, header_offset)
        elif page_type == cls.LEAF_PAGE_TYPE:
            return PageLeaf(page_bytes, header_offset)

        raise RuntimeError("Unknown page type")

    @classmethod
    @abstractmethod
    def _get_cell(cls, page_bytes: bytes, cell_offset: int) -> CellInterior | CellLeaf:
        pass

    @classmethod
    def _get_cells(
        cls, page_bytes: bytes, cell_count_offset: int, page_header_len: int
    ) -> list[CellInterior | CellLeaf]:
        cells = []

        # Get number of cells
        cell_count_bytes = page_bytes[
            cell_count_offset : cell_count_offset + CELL_COUNT_LEN
        ]
        cell_count = int.from_bytes(cell_count_bytes, "big")

        # Iterate through each cell
        for cell_idx in range(cell_count):
            cell_offset_bytes = page_bytes[
                page_header_len + (cell_idx * cls.CELL_POINTER_LEN) : page_header_len
                + (cell_idx * cls.CELL_POINTER_LEN)
                + cls.CELL_POINTER_LEN
            ]
            cell_offset = int.from_bytes(cell_offset_bytes, "big")

            cell = cls._get_cell(page_bytes, cell_offset)
            cells.append(cell)

        return cells

    @abstractmethod
    def get_content_pointers(self) -> tuple[str, list[int] | list[None | int | str]]:
        pass


class PageInterior(Page):
    PAGE_HEADER_LEN = 12
    PAGE_NUMBER_LEN = 4
    ROWID_LEN = 1

    def __init__(self, page_bytes: bytes, header_offset: int) -> None:
        page_header_bytes = page_bytes[
            header_offset : header_offset + self.PAGE_HEADER_LEN
        ]
        self.header = PageHeaderInterior(page_header_bytes)

        self.cells = self._get_cells(
            page_bytes,
            header_offset + self.header.CELL_COUNT_OFFSET,
            header_offset + self.PAGE_HEADER_LEN,
        )

    @classmethod
    def _get_cell(cls, page_bytes: bytes, cell_offset: int) -> CellInterior:
        cell_bytes = page_bytes[
            cell_offset : cell_offset + cls.PAGE_NUMBER_LEN + cls.ROWID_LEN
        ]
        return CellInterior(cell_bytes)

    def get_content_pointers(self) -> tuple[str, list[int]]:
        pointers = [cell.page_number for cell in self.cells]
        pointers.append(self.header.right_child_page_number)
        return ("pages", pointers)


class PageLeaf(Page):
    PAGE_HEADER_LEN = 8

    def __init__(self, page_bytes: bytes, header_offset: int) -> None:
        page_header_bytes = page_bytes[
            header_offset : header_offset + self.PAGE_HEADER_LEN
        ]
        self.header = PageHeaderLeaf(page_header_bytes)

        self.cells = self._get_cells(
            page_bytes,
            header_offset + self.header.CELL_COUNT_OFFSET,
            header_offset + self.PAGE_HEADER_LEN,
        )

    @classmethod
    def _get_cell(cls, page_bytes: bytes, cell_offset: int) -> CellLeaf:
        payload_size, number_payload_size_read_bytes = read_varint(
            page_bytes[cell_offset : cell_offset + VARINT_MAX_LEN]
        )
        rowid, number_rowid_read_bytes = read_varint(
            page_bytes[
                cell_offset + number_payload_size_read_bytes : cell_offset
                + number_payload_size_read_bytes
                + VARINT_MAX_LEN
            ]
        )

        cell_bytes = page_bytes[
            cell_offset : cell_offset
            + number_payload_size_read_bytes
            + number_rowid_read_bytes
            + payload_size
        ]
        return CellLeaf(cell_bytes)

    def get_content_pointers(self) -> tuple[str, list[None | int | str]]:
        content = [cell.payload.content for cell in self.cells]
        return ("data", content)
