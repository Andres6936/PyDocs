# libclang Python Bindings

This is an import of the python bindings for libclang taken from the
`bindings/python/clang` directory of the
[clang](https://github.com/llvm-mirror/clang) repository.

The files are taken from SVN commit 328949 with the modifications listed in
`cldoc/clang/cindex-updates.patch`.

To apply the cldoc changes, run:

	cp ${CLANG_DIR}/bindings/python/clang/cindex.py cldoc/clang/cindex.py
	patch -p1 < cldoc/clang/cindex-updates.patch

To revert the custom modifications, run:

	patch -R -p1 < cldoc/clang/cindex-updates.patch

To create a new patch (e.g. after applying the cldoc changes on top of a new clang version), run:

	git add cldoc/clang/cindex.py
	cp ${CLANG_DIR}/bindings/python/clang/cindex.py cldoc/clang/cindex.py
	git diff -R cldoc/clang/cindex.py > cldoc/clang/cindex-updates.patch

Clang Indexing Library Bindings
===============================

This module provides an interface to the Clang indexing library. It is a low-level interface to the indexing library
which attempts to match the Clang API directly while also being "pythonic". Notable differences from the C API are:

* string results are returned as Python strings, not CXString objects.

* null cursors are translated to None.

* access to child cursors is done via iteration, not visitation.

The major indexing objects are:

Index

    The top-level object which manages some global library state.

TranslationUnit

    High-level object encapsulating the AST for a single translation unit. These
    can be loaded from cldoc.ast files or parsed on the fly.

Cursor

    Generic object for representing a node in the AST.

SourceRange, SourceLocation, and File

    Objects representing information about the input source.

Most object information is exposed using properties, when the underlying API call is efficient.

# TODO

# ====

#

# o API support for invalid translation units. Currently we can't even get the

# diagnostics on failure because they refer to locations in an object that

# will have been invalidated.

#

# o fix memory management issues (currently client must hold on to index and

# translation unit, or risk crashes).

#

# o expose code completion APIs.

#

# o cleanup ctypes wrapping, would be nice to separate the ctypes details more

# clearly, and hide from the external interface (i.e., help(cindex)).

#

# o implement additional SourceLocation, SourceRange, and File methods.

----

# This file is part of cldoc. cldoc is free software: you can

# redistribute it and/or modify it under the terms of the GNU General Public

# License as published by the Free Software Foundation, version 2.

#

# This program is distributed in the hope that it will be useful, but WITHOUT

# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS

# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more

# details.

#

# You should have received a copy of the GNU General Public License along with

# this program; if not, write to the Free Software Foundation, Inc., 51

# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# ===- cindex.py - Python Indexing Library Bindings -----------*- python -*--===#

#

# The LLVM Compiler Infrastructure

#

# This file is distributed under the University of Illinois Open Source

# License. See LICENSE.TXT for details.