from src.utils import read_varint


PAGE_SIZE_OFFSET = 16
DATABASE_HEADER_OFFSET = 100
CELL_COUNT_OFFSET = DATABASE_HEADER_OFFSET + 3
CELL_CONTENT_AREA = DATABASE_HEADER_OFFSET + 5
FIRST_CELL_POINTER_OFFSET = 12
CELL_COUNT_TABLE_LEAF_OFFSET = 3
PAGE_HEADER_TABLE_LEAF = 8
RIGHT_CHILD_PAGE_NUMBER_OFFSET = 8


class Database():
    def __init__(self, path):
        self.path = path

        self.f = None
        self.page_size = None

    def _get_page_size(self):
        self.f.seek(PAGE_SIZE_OFFSET)

        page_size = self.f.read(2)
        page_size = int.from_bytes(page_size, 'big')

        return page_size

    def _get_cell_count(self):
        self.f.seek(CELL_COUNT_OFFSET)

        cell_count = self.f.read(2)
        cell_count = int.from_bytes(cell_count, 'big')

        return cell_count

    def _get_cell_content_area(self):
        self.f.seek(CELL_CONTENT_AREA)

        cell_content_area = self.f.read(2)
        cell_content_area = int.from_bytes(cell_content_area, 'big')

        return cell_content_area

    def __enter__(self):
        self.f = open(self.path, "rb")

        self.page_size = self._get_page_size()
        self.cell_count = self._get_cell_count()
        self.cell_content_area = self._get_cell_content_area()
        self.object_names = self._get_object_names(1)

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.f:
            self.f.close()

    def _get_object_names(self, page_number):
        if page_number == 1:
            page_offset = DATABASE_HEADER_OFFSET
        else:
            page_offset = (page_number - 1) * self.page_size
        
        self.f.seek(page_offset)
        page_type = int.from_bytes(self.f.read(1))
        if page_type == 0x05: # interior
            self.f.seek(page_offset + FIRST_CELL_POINTER_OFFSET)
            records = []
            for _ in range(self.cell_count):
                point_to_offset = int.from_bytes(self.f.read(2), 'big')

                next_cell_pos = self.f.tell()
                
                self.f.seek(point_to_offset)
                next_page_number = int.from_bytes(self.f.read(4), 'big')
                records += self._get_object_names(next_page_number)

                self.f.seek(next_cell_pos)

            self.f.seek(page_offset + RIGHT_CHILD_PAGE_NUMBER_OFFSET)
            next_page_number = int.from_bytes(self.f.read(4), 'big')
            
            return records + self._get_object_names(next_page_number)
        
        # page_type == 0x0d leaf
        self.f.seek(page_offset + CELL_COUNT_TABLE_LEAF_OFFSET)
        cell_count = int.from_bytes(self.f.read(2), 'big')

        self.f.seek(page_offset + PAGE_HEADER_TABLE_LEAF)
        records = []
        for _ in range(cell_count):
            point_to_offset = int.from_bytes(self.f.read(2), 'big')

            next_leaf_cell_pos = self.f.tell()
            self.f.seek(page_offset + point_to_offset)

            payload_size = read_varint(self.f)
            rowid = read_varint(self.f)

            header_size, total_read_bytes = read_varint(self.f)
                    
            # payload_size | rowid | header_size | serial_type1 | serial_type2 | ...
            serial_types = []
            while (header_size - total_read_bytes):
                serial_type, read_bytes = read_varint(self.f)

                serial_types.append(serial_type)
                total_read_bytes += read_bytes

            column_name = []
            for serial_type in serial_types:
                if serial_type == 0:
                    column_name.append(None)
                elif serial_type >= 1 and serial_type <= 6:
                    object_name = int.from_bytes(self.f.read(serial_type), 'big')
                    column_name.append(object_name)
                elif serial_type >= 13 and serial_type % 2 == 1:
                    length = (serial_type - 13) // 2
                    column_name.append(self.f.read(length).decode("utf-8"))
            
            records.append(column_name[1])
            self.f.seek(next_leaf_cell_pos)
        
        return records
