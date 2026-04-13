from src.utils.varint import read_varint
from .constants import VARINT_MAX_LEN


class PayloadHeader:
    def __init__(self, payload_bytes: bytes) -> None:
        # payload_size | rowid | header_size | serial_type1 | serial_type2 | ...
        self.payload_size, self.payload_size_read_bytes = read_varint(
            payload_bytes[:VARINT_MAX_LEN]
        )
        self.rowid, self.rowid_read_bytes = read_varint(
            payload_bytes[
                self.payload_size_read_bytes : self.payload_size_read_bytes
                + VARINT_MAX_LEN
            ]
        )
        self.payload_header_size, self.payload_header_size_read_bytes = read_varint(
            payload_bytes[
                self.payload_size_read_bytes
                + self.rowid_read_bytes : self.payload_size_read_bytes
                + self.rowid_read_bytes
                + VARINT_MAX_LEN
            ]
        )

        self.serial_types = self._get_serial_types(
            payload_bytes[
                self.payload_size_read_bytes
                + self.rowid_read_bytes
                + self.payload_header_size_read_bytes :
            ],
            self.payload_header_size,
            self.payload_header_size_read_bytes,
        )

    @classmethod
    def _get_serial_types(
        cls,
        payload_bytes: bytes,
        payload_header_size: int,
        payload_header_size_read_bytes: int,
    ) -> list[bytes]:
        serial_types = []
        total_read_bytes = 0
        while payload_header_size - payload_header_size_read_bytes:
            serial_type, read_bytes = read_varint(
                payload_bytes[total_read_bytes : total_read_bytes + VARINT_MAX_LEN]
            )
            serial_types.append(serial_type)

            payload_header_size_read_bytes += read_bytes
            total_read_bytes += read_bytes

        return serial_types


class Payload:
    def __init__(self, payload_bytes: bytes) -> None:
        self.header = PayloadHeader(payload_bytes)
        self.content = self._get_content(payload_bytes, self.header)

    @classmethod
    def _is_null(cls, serial_type: bytes) -> bool:
        return serial_type == 0

    @classmethod
    def _is_int(cls, serial_type: bytes) -> bool:
        return serial_type >= 1 and serial_type <= 6

    @classmethod
    def _get_int_size(cls, serial_type: bytes) -> int:
        if serial_type == 1:
            return 1
        elif serial_type == 2:
            return 2
        elif serial_type == 3:
            return 3
        elif serial_type == 4:
            return 4
        elif serial_type == 5:
            return 6
        elif serial_type == 6:
            return 8

    @classmethod
    def _is_string(cls, serial_type: bytes) -> bool:
        return serial_type >= 13 and serial_type % 2 == 1

    @classmethod
    def _get_string_length(cls, serial_type: bytes) -> int:
        return (serial_type - 13) // 2

    @classmethod
    def _get_content(
        cls, payload_bytes: bytes, payload_header: PayloadHeader
    ) -> list[None | int | str]:
        payload_content = []
        total_read_bytes = (
            payload_header.payload_size_read_bytes
            + payload_header.rowid_read_bytes
            + payload_header.payload_header_size
        )

        for serial_type in payload_header.serial_types:
            if cls._is_null(serial_type):
                payload_content.append(None)
            elif cls._is_int(serial_type):
                int_size = cls._get_int_size(serial_type)

                num_bytes = payload_bytes[
                    total_read_bytes : total_read_bytes + int_size
                ]
                num = int.from_bytes(num_bytes, "big")

                payload_content.append(num)
                total_read_bytes += int_size
            elif cls._is_string(serial_type):
                length = cls._get_string_length(serial_type)
                text = payload_bytes[
                    total_read_bytes : total_read_bytes + length
                ].decode("utf-8")

                payload_content.append(text)
                total_read_bytes += length

        return payload_content
