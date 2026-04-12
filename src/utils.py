def read_varint(f, offset=None):
    '''
    On success returns tuple consisting varint and read bytes 
    On success function moves file cursor
    On failure function moves back file cursor to the previous position
    If no offset given 
    then function looks for varint 
    from current file cursor position
    '''

    curr_pos = f.tell()
    if offset is not None:
        f.seek(offset)

    val = 0
    for bytes in range(9):
        byte = int.from_bytes(f.read(1))
        data = byte & 0x7F

        val = (val << 7) | data

        if (byte & 0x80) == 0:
            return (val, bytes + 1) 

    f.seek(curr_pos)
    raise RuntimeError("There is no varint in given offset")
