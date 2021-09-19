
class ConversionError(Exception):
    def __init__(self, msg):
        super(ConversionError, self).__init__(msg)
