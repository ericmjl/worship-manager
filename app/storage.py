import yaml
from tinydb import Storage


class YAMLStorage(Storage):
    def __init__(self, filename):  # (1)
        self.filename = filename

    def read(self):
        with open(self.filename) as handle:
            try:
                data = yaml.safe_load(handle.read())  # (2)
                return data
            except yaml.YAMLError:
                return None  # (3)

    def write(self, data):
        with open(self.filename, 'w') as handle:
            yaml.dump(data, handle)

    def close(self):  # (4)
        pass
