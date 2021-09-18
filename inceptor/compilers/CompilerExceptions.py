class OperationNotSupported(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class CompilationError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
