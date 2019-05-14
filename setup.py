import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def run_tests(self):
        import shlex
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(['tests/'])
        sys.exit(errno)

setup(
  name = 'namelist_python',
  packages = ['namelist_python'],
  version = '0.1.4',
  description = 'Fortran namelist file parser in Python',
  author = 'Leif Denby',
  author_email = 'leifdenby@gmail.com',
  url = 'https://github.com/leifdenby/namelist_python',
  download_url = 'https://github.com/leifdenby/namelist_python/archive/0.1.3.tar.gz',
  keywords = ['namelist', 'fortran', 'parsing'],
  cmdclass=dict(test=PyTest),
  tests_require=['pytest',],
  classifiers = [],
)
