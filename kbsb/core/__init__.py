from reddevil.core import RdException


class RdForbidden(RdException):
    def __init__(self, description="Forbidden"):
        super().__init__(status_code=403, description=description)
