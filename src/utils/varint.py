def read_varint(bytes):
    val = 0
    for idx, byte in enumerate(bytes):  # Read bytes...
        if idx == 9:
            raise RuntimeError("Given bytes aren't varint")

        data = byte & 0x7F

        val = (val << 7) | data

        if (byte & 0x80) == 0:  # ...until you encounter byte with the first bit set
            return (val, idx + 1)
