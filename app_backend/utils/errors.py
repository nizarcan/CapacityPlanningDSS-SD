class FileValidationError(Exception):
    def __init__(self, *args):
        if args:
            self.message = f"An error happened while the compilation and the validation of the {args[0]} file."
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return self.message
        else:
            return "An error has occured while the validation of the file is being made."


class WrongFileExtensionError(Exception):
    def __init__(self, *args):
        if args:
            self.message = f"The filetype {args[0]} is not appropriate for the operation."
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return self.message
        else:
            return "An error happened because the filetype is not appropriate ."

