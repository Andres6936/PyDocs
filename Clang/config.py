from ctypes import cdll

from Clang.decorators.cached_property import CachedProperty
from Clang.exceptions.lib_clang import LibclangError

class Config:
    library_path = None
    library_file = None
    compatibility_check = True
    loaded = False

    @staticmethod
    def set_library_path(path):
        """Set the path in which to search for libclang"""
        if Config.loaded:
            raise Exception("library path must be set before before using "
                            "any other functionalities in libclang.")

        Config.library_path = path

    @staticmethod
    def set_library_file(filename):
        """Set the exact location of libclang"""
        if Config.loaded:
            raise Exception("library file must be set before before using "
                            "any other functionalities in libclang.")

        Config.library_file = filename

    @staticmethod
    def set_compatibility_check(check_status):
        """ Perform compatibility check when loading libclang

        The python bindings are only tested and evaluated with the version of
        libclang they are provided with. To ensure correct behavior a (limited)
        compatibility check is performed when loading the bindings. This check
        will throw an exception, as soon as it fails.

        In case these bindings are used with an older version of libclang, parts
        that have been stable between releases may still work. Users of the
        python bindings can disable the compatibility check. This will cause
        the python bindings to load, even though they are written for a newer
        version of libclang. Failures now arise if unsupported or incompatible
        features are accessed. The user is required to test themselves if the
        features they are using are available and compatible between different
        libclang versions.
        """
        if Config.loaded:
            raise Exception("compatibility_check must be set before before "
                            "using any other functionalities in libclang.")

        Config.compatibility_check = check_status

    @CachedProperty
    def lib(self):
        from Clang.prototypes.register_functions import register_functions

        lib = self.get_cindex_library()
        register_functions(lib, not Config.compatibility_check)
        Config.loaded = True
        return lib

    def get_filename(self):
        if Config.library_file:
            return Config.library_file

        import platform
        name = platform.system()

        if name == 'Darwin':
            file = 'libclang.dylib'
        elif name == 'Windows':
            file = 'libclang.dll'
        else:
            file = 'libclang.so'

        if Config.library_path:
            file = Config.library_path + '/' + file

        return file

    def get_cindex_library(self):
        try:
            library = cdll.LoadLibrary(self.get_filename())
        except OSError as e:
            msg = str(e) + ". To provide a path to libclang use " \
                           "Config.set_library_path() or " \
                           "Config.set_library_file()."
            raise LibclangError(msg)

        return library

    def function_exists(self, name):
        try:
            getattr(self.lib, name)
        except AttributeError:
            return False

        return True


conf = Config()
