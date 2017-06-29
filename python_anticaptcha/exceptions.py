class AnticatpchaException(Exception):
    def __init__(self, error_id, error_code, error_description, *args):
        super(AnticatpchaException, self).__init__(error_description)
        self.error_id = error_id
        self.error_code = error_code
