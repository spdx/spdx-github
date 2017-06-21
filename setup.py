from distutils.core import setup
setup(name='spdx-github',
      version='1.0',
      packages=['spdx_github'],
      package_dir = {'spdx_github': 'src'},
      py_modules = ['spdx_github.repo_scan']
      )
