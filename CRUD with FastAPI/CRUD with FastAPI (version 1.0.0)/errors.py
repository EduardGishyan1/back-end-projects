class ValidationError(Exception):
    def __init__(self, detail):
      self.detail = detail

class FileError(Exception):
    def __init__(self, detail):
      self.detail = detail

class NotFoundError(Exception):
    def __init__(self, detail):
      self.detail = detail