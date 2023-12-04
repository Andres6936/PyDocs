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
from __future__ import absolute_import

import argparse
import os
import sys

from cldoc.files.provider_source import ProviderSource
from cldoc.tree import Tree
from cldoc import fs, staticsite
from cldoc import log


def run_generate(t: Tree, opts):
    if opts.type != 'html' and opts.type != 'xml':
        return

    from cldoc import generators

    generator = generators.Xml(t, opts)

    if opts.type == 'html' and opts.static:
        baseout = fs.fs.mkdtemp()
    else:
        baseout = opts.output

    xmlout: str = os.path.join(baseout, 'xml')
    generator.generate(xmlout)

    if opts.type == 'html':
        generators.Html(t).generate(baseout, opts.static, opts.custom_js, opts.custom_css)

        if opts.static:
            staticsite.generate(baseout, opts)


def run(args):
    try:
        sep = args.index('--')
    except ValueError:
        if not '--help' in args:
            sys.stderr.write('Please use: cldoc generate [CXXFLAGS] -- [OPTIONS] [FILES]\n')
            sys.exit(1)
        else:
            sep = -1

    parser = argparse.ArgumentParser(description='clang based documentation generator.',
                                     usage='%(prog)s generate [CXXFLAGS] -- [OPTIONS] [FILES]')

    parser.add_argument('--quiet', default=False, action='store_const', const=True,
                        help='be quiet about it')

    parser.add_argument('--loglevel', default='error', type=str,
                        help='specify the logevel (error, warning, info)')

    parser.add_argument('--report', default=False,
                        action='store_const', const=True, help='report documentation coverage and errors')

    parser.add_argument('--output', type=str, action='store',
                        help='specify the output directory')

    parser.add_argument('--language', default='c++', metavar='LANGUAGE',
                        help='specify the default parse language (c++, c or objc)')

    parser.add_argument('--type', default='html', metavar='TYPE',
                        help='specify the type of output (html or xml, default html)')

    parser.add_argument('--merge', default=[], metavar='FILES', action='append',
                        help='specify additional description files to merge into the documentation')

    parser.add_argument('--merge-filter', default=None, metavar='FILTER',
                        help='specify program to pass merged description files through')

    parser.add_argument('--basedir', default=None, metavar='DIR',
                        help='the project base directory')

    parser.add_argument('--static', default=False, action='store_const', const=True,
                        help='generate a static website (only for when --output is html, requires globally installed cldoc-static via npm)')

    parser.add_argument('--custom-js', default=[], metavar='FILES', action='append',
                        help='specify additional javascript files to be merged into the html (only for when --output is html)')

    parser.add_argument('--custom-css', default=[], metavar='FILES', action='append',
                        help='specify additional css files to be merged into the html (only for when --output is html)')

    parser.add_argument('--files', nargs='+',
                        help='files to parse')

    restargs = args[sep + 1:]
    cxxflags = args[:sep]

    opts = parser.parse_args()

    if opts.quiet:
        sys.stdout = open(os.devnull, 'w')

    log.setLevel(opts.loglevel)

    from cldoc import tree

    if not opts.output:
        sys.stderr.write("Please specify the output directory\n")
        sys.exit(1)

    if opts.static and opts.type != 'html':
        sys.stderr.write("The --static option can only be used with the html output format\n")
        sys.exit(1)

    haslang = False

    for x in cxxflags:
        if x.startswith('-x'):
            haslang = True

    if not haslang:
        cxxflags += '-x'
        cxxflags += opts.language

    provider_source = ProviderSource()
    for directory in opts.files:
        provider_source.provider_sources(directory)
    # Sort the files first in sources then in headers
    provider_source.sort_first_by_sources()

    tree = tree.Tree(provider_source, cxxflags)

    tree.process()

    if opts.merge:
        tree.merge(opts.merge_filter, opts.merge)

    tree.cross_ref()

    run_generate(tree, opts)

# vi:ts=4:et
