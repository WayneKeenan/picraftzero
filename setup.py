import os
from setuptools import setup, find_packages
base_dir = os.path.dirname(os.path.abspath(__file__))

version = "0.1.0"

install_requires = []       # optional: #cap1xxx==0.1.3 evdev==0.6.4
tests_require = []

setup(
    name='picraftzero',
    version=version,
    description="A library for building universal controls for robots",
    long_description="\n\n".join([
        open(os.path.join(base_dir, "README.md"), "r").read(),
    ]),
    url='https://www.thebubbleworks.com/picraftzero',
    author='Wayne Keenan',
    author_email='wayne@thebubbleworks.com',
    maintainer='Wayne Keenan',
    maintainer_email='wayne@thebubbleworks.com',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="tests.get_tests",
)
