class Database():
    def __init__(self, path):
        self.path = path

        self.f = None
        self.page_size = None

    def __get_page_size(self):
        self.f.seek(16)

        page_size = self.f.read(2)
        page_size = int.from_bytes(page_size, 'big')

        return page_size

    def __enter__(self):
        try:
            self.f = open(self.path, "rb")
        except Exception as e:
            raise RuntimeError("Cannot open .db file:", e)

        self.page_size = self.__get_page_size()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.f:
            self.f.close()
