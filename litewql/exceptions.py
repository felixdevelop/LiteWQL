
class ParsingError(Exception):
    pass


class CastError(Exception):
    original_exception = None

    def __init__(self, exception):

        if isinstance(exception, Exception):
            message = str(exception)
            self.original_exception = exception
        else:
            message = str(exception)
            self.original_exception = None

        super().__init__(message)
