PAGE_SIZE_OFFSET = 16


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

    def __enter__(self):
        self.f = open(self.path, "rb")

        self.page_size = self._get_page_size()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.f:
            self.f.close()
