class LibclangError(Exception):
    def __init__(self, message):
        self.m = message

    def __str__(self):
        return self.m