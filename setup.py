from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
  name = 'namelist_python',
  ng_description=readme,
  packages = ['namelist_python'],
  version = '0.1.1',
  description = 'Fortran namelist file parser in Python',
  author = 'Leif Denby',
  author_email = 'leifdenby@gmail.com',
  url = 'https://github.com/leifdenby/namelist_python',
  download_url = 'https://github.com/leifdenby/namelist_python/archive/0.1.tar.gz',
  keywords = ['namelist', 'fortran', 'parsing'],
  classifiers = [],
)
