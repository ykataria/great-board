class ConstraintException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"ConstraintException raised with message: {self.message}"


class ObjectAlreadyPresentException(ConstraintException):
    pass


class LimitOverflowException(ConstraintException):
    pass


class ConstraintViolationException(ConstraintException):
    pass


class NoDataException(Exception):
    pass
