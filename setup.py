from setuptools import setup, find_packages
setup(
  name = "yak",
  version = "0.1",
  packages = find_packages(),
  entry_points = {
    'console_scripts': ['yak = yak.main:main'],
  }
)
