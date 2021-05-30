from ctypes import POINTER, c_uint, byref, cast

from clang.config import conf
from clang.token import Token


class TokenGroup(object):
    """Helper class to facilitate token management.

    Tokens are allocated from libclang in chunks. They must be disposed of as a
    collective group.

    One purpose of this class is for instances to represent groups of allocated
    tokens. Each token in a group contains a reference back to an instance of
    this class. When all tokens from a group are garbage collected, it allows
    this class to be garbage collected. When this class is garbage collected,
    it calls the libclang destructor which invalidates all tokens in the group.

    You should not instantiate this class outside of this module.
    """

    def __init__(self, tu, memory, count):
        self._tu = tu
        self._memory = memory
        self._count = count

    def __del__(self):
        conf.lib.clang_disposeTokens(self._tu, self._memory, self._count)

    @staticmethod
    def get_tokens(tu, extent):
        """Helper method to return all tokens in an extent.

        This functionality is needed multiple places in this module. We define
        it here because it seems like a logical place.

        :tu (TranslationUnit) The translation unit whose text is being tokenized.
        :extent (SourceRange) The source range in which text should be tokenized.
            All of the tokens produced by tokenization will fall within this
            source range,
        """
        # This pointer will be set to point to the array of tokens that occur
        # within the given source range. The returned pointer must be freed with
        # clang_disposeTokens() before the translation unit is destroyed.
        tokens_memory = POINTER(Token)()
        # Will be set to the number of tokens in the *Tokens array.
        tokens_count = c_uint()

        # Tokenize the source code described by the given range into raw
        # lexical tokens.
        conf.lib.clang_tokenize(tu, extent, byref(tokens_memory),
                                byref(tokens_count))

        count = int(tokens_count.value)

        # If we get no tokens, no memory was allocated. Be sure not to return
        # anything and potentially call a destructor on nothing.
        if count < 1:
            return

        tokens_array = cast(tokens_memory, POINTER(Token * count)).contents

        token_group = TokenGroup(tu, tokens_memory, tokens_count)

        for i in range(0, count):
            token = Token()
            token.int_data = tokens_array[i].int_data
            token.ptr_data = tokens_array[i].ptr_data
            token._tu = tu
            token._group = token_group

            yield token

    def __repr__(self):
        """
        Return the representation of object in the form of number of
        tokens that have been parsed.
        """
        return "{} Tokens".format(self._count.value)
