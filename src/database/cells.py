from .payload import Payload


class CellInterior:
    PAGE_NUMBER_LEN = 4

    @classmethod
    def _get_page_number(cls, cell_bytes: bytes) -> int:
        page_number_bytes = cell_bytes[: cls.PAGE_NUMBER_LEN]
        page_number = int.from_bytes(page_number_bytes, "big")

        return page_number

    def __init__(self, cell_bytes: bytes) -> None:
        self.page_number = self._get_page_number(cell_bytes)


class CellLeaf:
    def __init__(self, cell_bytes: bytes) -> None:
        self.payload = Payload(cell_bytes)
