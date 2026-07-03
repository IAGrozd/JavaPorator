class ConversionError(Exception):
    def __init__(self, msg="Възникна грешка при конвертирането на кода."):
        super().__init__(msg)


class JavaSyntaxError(ConversionError):
    def __init__(self, msg: str):
        super().__init__(msg)