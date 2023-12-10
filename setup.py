#!/usr/bin/env python

from setuptools import setup, Command

import subprocess, os, shutil, glob, sys

coffee_files = [
    'cldoc.coffee',
    'page.coffee',
    'sidebar.coffee',
    'node.coffee',
    'type.coffee',
    'doc.coffee',
    'category.coffee',
    'enum.coffee',
    'templated.coffee',
    'struct.coffee',
    'structtemplate.coffee',
    'class.coffee',
    'classtemplate.coffee',
    'namespace.coffee',
    'typedef.coffee',
    'variable.coffee',
    'function.coffee',
    'functiontemplate.coffee',
    'field.coffee',
    'method.coffee',
    'methodtemplate.coffee',
    'constructor.coffee',
    'destructor.coffee',
    'base.coffee',
    'implements.coffee',
    'subclass.coffee',
    'implementedby.coffee',
    'templatetypeparameter.coffee',
    'coverage.coffee',
    'arguments.coffee',
    'report.coffee',
    'references.coffee',
    'union.coffee',
    'gobjectclass.coffee',
    'gobjectinterface.coffee',
    'gobjectboxed.coffee',
    'gobjectproperty.coffee',
]

class cldoc_generate(Command):
    description = "generate css, js and html files"

    user_options = [
        ('coffee=', None, 'path to coffeescript compiler'),
        ('sass=', None, 'path to sass compiler'),
        ('inline=', None, 'path to inline')
    ]

    def initialize_options(self):
        self.coffee = 'coffee'
        self.sass = 'sass'
        self.inline = 'Scripts/inline'

    def finalize_options(self):
        pass

    def run_coffee(self):
        print('running {0}'.format(self.coffee))

        for d in ('html/javascript', 'Pydoc/data/javascript'):
            try:
                os.makedirs(d)
            except:
                pass

        args = [self.coffee, '--bare', '--stdio', '--compile']

        try:
            sp = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        except Exception as e:
            sys.stderr.write("Failed to run coffee (please make sure it is installed)\n")
            sys.exit(1)

        for f in coffee_files:
            with open(os.path.join('html', 'coffee', f)) as ff:
                sp.stdin.write(ff.read())

        sp.stdin.close()

        with open('html/javascript/Pydoc.js', 'w') as out:
            out.write(sp.stdout.read())

        sp.wait()

        for js in glob.glob('html/javascript/*.js'):
            shutil.copyfile(js, 'Pydoc/data/javascript/' + os.path.basename(js))

    def run_sass(self):
        print('running {0}'.format(self.sass))

        for d in ('html/styles', 'Pydoc/data/styles'):
            try:
                os.makedirs(d)
            except:
                pass

        args = [self.sass, '--output-style', 'compressed']
        files = ['html/sass/Pydoc.scss', 'html/styles/Pydoc.css']

        subprocess.call(args + files)

        for css in glob.glob('html/styles/*.css'):
            shutil.copyfile(css, 'Pydoc/data/styles/' + os.path.basename(css))

    def run_inline(self):
        if self.inline == '':
            shutil.copyfile('html/index.html', 'Packages/Pydoc/data/index.html')
            return

        print('running {0}'.format(self.inline))

        args = [self.inline, 'html/index.html']

        try:
            os.makedirs('Packages/Pydoc/data')
        except:
            pass

        fout = file('Pydoc/data/index.html', 'w')

        proc = subprocess.Popen(args, stdout=fout)
        proc.wait()

    def run(self):
        self.run_coffee()
        self.run_sass()
        self.run_inline()

cmdclass = {
    'generate': cldoc_generate
}

datafiles = []
dataprefix = 'Pydoc'

for dirpath, dirnames, filenames in os.walk(os.path.join(dataprefix, 'data')):
    datafiles += [os.path.join(dirpath[len(dataprefix)+1:], f) for f in filenames]

setup(name='Pydoc',
      version='1.11',
      description='clang based documentation generator for C/C++',
      author='Jesse van den Kieboom',
      author_email='jessevdk@gmail.com',
      url='http://jessevdk.github.com/cldoc',
      license='GPLv2',
      keywords=['clang', 'c++', 'documentation'],
      packages=['Pydoc', 'Pydoc.clang', 'Pydoc.nodes', 'Pydoc.generators'],
      entry_points = {
          'console_scripts': [
              'Pydoc = Pydoc:run'
          ]
      },
      package_data={'Pydoc': datafiles},
      cmdclass=cmdclass,
      install_requires=['pyparsing == 2.2.0'])

# vi:ts=4:et
