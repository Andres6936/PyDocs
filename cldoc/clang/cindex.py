# This file is part of cldoc.  cldoc is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# ===- cindex.py - Python Indexing Library Bindings -----------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
# ===------------------------------------------------------------------------===#

r"""

"""

from ctypes import *

from clang.config import conf
from clang.cursor import Cursor
from clang.decorators.cached_property import CachedProperty
from clang.objects.completion_chunk import completionChunkKindMap
from clang.objects.completion_string import CompletionString
from clang.prototypes.functions import c_object_p, callbacks
from clang.spelling_cache import SpellingCache
from clang.utility.source_location import SourceLocation






