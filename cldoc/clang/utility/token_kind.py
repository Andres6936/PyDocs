class TokenKind(object):
    """Describes a specific type of a Token."""

    _value_map = {}  # int -> TokenKind

    def __init__(self, value, name):
        """Create a new TokenKind instance from a numeric value and a name."""
        self.value = value
        self.name = name

    def __repr__(self):
        return 'TokenKind.%s' % (self.name,)

    @staticmethod
    def from_value(value):
        """Obtain a registered TokenKind instance from its value."""
        result = TokenKind._value_map.get(value, None)

        if result is None:
            raise ValueError('Unknown TokenKind: %d' % value)

        return result

    @staticmethod
    def register(value, name):
        """Register a new TokenKind enumeration.

        This should only be called at module load time by code within this
        package.
        """
        if value in TokenKind._value_map:
            pass
            # raise ValueError('TokenKind already registered: %d' % value)

        kind = TokenKind(value, name)
        TokenKind._value_map[value] = kind
        setattr(TokenKind, name, kind)