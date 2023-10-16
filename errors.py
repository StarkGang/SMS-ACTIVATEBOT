class NOBALANCEERROR(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)


class NONUMBERERROR(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)


class APIFAILURE(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)