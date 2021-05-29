class CompilationDatabaseError(Exception):
    """Represents an error that occurred when working with a CompilationDatabase

    Each error is associated to an enumerated value, accessible under
    e.cdb_error. Consumers can compare the value with one of the ERROR_
    constants in this class.
    """

    # An unknown error occurred
    ERROR_UNKNOWN = 0

    # The database could not be loaded
    ERROR_CANNOTLOADDATABASE = 1

    def __init__(self, enumeration, message):
        assert isinstance(enumeration, int)

        if enumeration > 1:
            raise Exception("Encountered undefined CompilationDatabase error "
                            "constant: %d. Please file a bug to have this "
                            "value supported." % enumeration)

        self.cdb_error = enumeration
        Exception.__init__(self, 'Error %d: %s' % (enumeration, message))
