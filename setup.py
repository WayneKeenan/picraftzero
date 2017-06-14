import os
import unittest
from setuptools import setup, find_packages
from pprint import pformat
base_dir = os.path.dirname(os.path.abspath(__file__))

version = "0.1.3"

install_requires = ['gpiozero']       # optional: #cap1xxx==0.1.3 evdev==0.6.4x
tests_require = ['selenium']


def test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('test')
    return test_suite



setup(
    name='picraftzero',
    version=version,
    description="A library for building universal controls for robots",
    #long_description="\n\n".join([
    #    open(os.path.join(base_dir, "README.md"), "r").read(),
    #]),
    long_description="PiCraftZero, universal robot remote controls and viewer",
    url='https://www.thebubbleworks.com/picraftzero',
    author='Wayne Keenan',
    author_email='wayne@thebubbleworks.com',
    maintainer='Wayne Keenan',
    maintainer_email='wayne@thebubbleworks.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    #package_data={'picraftzero': ['picraftzero.cfg']},
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="setup.test_suite",
    platforms=['Raspberry Pi', 'Linux', 'Mac'],
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Development Status :: 4 - Beta',
                 'Programming Language :: Python :: 3',
                 'Environment :: Console',
                 'Environment :: Web Environment',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Developers',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: POSIX',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 ],
)
