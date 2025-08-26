    


import abc


class BaseException(Exception): 

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class URLFormatException(BaseException):

    def __init__(self, message: str):
        super().__init__(message)
