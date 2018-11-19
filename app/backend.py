import os
import os.path
import json
from flask_dance.consumer.backend import BaseBackend

class FileBackend(BaseBackend):
    def __init__(self, filepath):
        super(FileBackend, self).__init__()
        self.filepath = filepath

    def get(self, blueprint):
        if not os.path.exists(self.filepath):
            return None
        with open(self.filepath) as f:
            return json.load(f)

    def set(self, blueprint, token):
        with open(self.filepath, "w") as f:
            json.dump(token, f)

    def delete(self, blueprint):
        os.remove(self.filepath)
