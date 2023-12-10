from ctypes import POINTER, c_void_p, c_char_p

# ctypes doesn't implicitly convert c_void_p to the appropriate wrapper
# object. This is a problem, because it means that from_parameter will see an
# integer and pass the wrong value on platforms where int != void*. Work around
# this by marshalling object arguments as void**.

c_object_p = POINTER(c_void_p)


# Python 3 strings are unicode, translate them to/from utf8 for C-interop.
class c_interop_string(c_char_p):

    def __init__(self, p=None):
        if p is None:
            p = ""
        if isinstance(p, str):
            p = p.encode("utf8")
        super(c_char_p, self).__init__(p)

    def __str__(self):
        return self.value

    @property
    def value(self):
        if super(c_char_p, self).value is None:
            return None
        return super(c_char_p, self).value.decode("utf8")

    @classmethod
    def from_param(cls, param):
        if isinstance(param, str):
            return cls(param)
        if isinstance(param, bytes):
            return cls(param)
        if param is None:
            # Support passing null to C functions expecting char arrays
            return None
        raise TypeError("Cannot convert '{}' to '{}'".format(type(param).__name__, cls.__name__))

    @staticmethod
    def to_python_string(x, *args):
        return x.value
